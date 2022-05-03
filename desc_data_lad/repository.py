import datalad
import os

# export DATALAD_SSH_IDENTITYFILE=~/.ssh/nersc

# Test URL - update later
NERSC_ROOT_DIR = "/global/projecta/projectdirs/lsst/groups/WL/users/zuntz/datalad/root2"
NERSC_GIT_ANNEX_PATH = "/global/cfs/cdirs/desc-wl/users/zuntz/datalad/conda/bin/git-annex-shell"

def create_local_repository(path):
    return Repository.create(path)

def get_system_desc_root():
    env_var = os.environ.get("DESC_DATA_ROOT")

    if env_var is not None:
        return env_var

    if "NERSC_HOST" in os.environ:
        return NERSC_ROOT_DIR


    # what should this do if you are not on a shared system?
    # just crash? use an environment variable?
    # use a ~/Library directory?
    raise ValueError("Not decided this behavior yet")
    pass


def configure_git_annex(d):
    if isinstance(d, str):
        d = datalad.api.Dataset(d)
    # We need to tell our repos where they can fin
    d.configuration('set', [
        ('remote.origin.annex-shell', NERSC_GIT_ANNEX_PATH),
        ('remote.origin.annex-ignore', 'false')
    ], recursive=True)    

def get_nersc_project_repository(project_id):
    # should fail if not running on NERSC
    pass

def get_nersc_user_repository(username):
    # get path for this at NERSC
    # create user repo at NERSC if it doesn't exist
    pass

def clone_project_repository(project_id):
    pass

def clone_user_repository(username):
    pass

def clone_nersc_root_repository(nersc_username):
    uri = f"ssh://{nersc_username}@cori.nersc.gov:{NERSC_ROOT_DIR}"
    path = get_system_desc_root()
    d = datalad.api.clone(path=path, source=uri)
    configure_git_annex(d)
    repo = Repository(d.path)
    repo.get_sub_repositories()
    return repo


class Repository:
    def __init__(self, path):
        self.path = path
        self._dataset = datalad.api.Dataset(path)

    @classmethod
    def create(cls, path, parent=None, description=None):
        datalad.api.create(path=path, dataset=parent, description=description)
        return cls(path)

    def synchronize(self, recursive=True):
        # datalad.api.update(dataset=self.path, recursive=recursive, how="merge")
        self._dataset.update(recursive=recursive, how="merge")

    def create_subrepository(self, path, description=None):
        return self.create(path=path, parent=self.path, description=description)

    def get_path_for(self, path):
        return os.path.join(self.path, path)

    def save(self, path, message=None):
        path = os.path.join(self.path, path)
        # datalad.api.save(path=path, dataset=self.path, message=message)

    def add_file(self, path, message=None):
        pass

    def get_file(self, path):
        path = self.get_path_for(path)
        print(f"Getting {path} in repo {self.path}")
        # datalad.api.get(path=path, dataset=self.path)
        self._dataset.get(path=path)
        return path

    def get_sub_repository(self, path):
        path = self.get_file(path)
        return Repository(path)

    def get_sub_repositories(self):
        # sub_repos = datalad.api.subdatasets(dataset=self.path)
        sub_repos = self._dataset.subdatasets()
        print(f"Getting {len(sub_repos)} sub-repositories")
        for sub in sub_repos:
            d = self.get_file(sub['gitmodule_url'])
            configure_git_annex(d)

    def get_state(self, path=None):
        if path is None:
            # statuses = datalad.api.status(dataset=self.path)
            status = self._dataset.status()

            # Consider the repo as a whole to be modified if any files within
            # are not listed as clean
            for s in statuses:
                if s['state'] in ["modified", "untracked", "added", "deleted"]:
                    return "modified"
            return "clean"
        else:
            return self._dataset.status(path=path)[0]['status']
            # return datalad.api.status(path=path, dataset=self.path)[0]['state']
    
    def unlock(self, path):
        return self._dataset.unlock(path=path)
        # return datalad.api.unlock(path=path, dataset=self.path)

