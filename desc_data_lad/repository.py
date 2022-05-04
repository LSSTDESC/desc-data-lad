import datalad.api
import os

# export DATALAD_SSH_IDENTITYFILE=~/.ssh/nersc

# Test URL - update later
NERSC_ROOT_DIR = "/global/projecta/projectdirs/lsst/groups/WL/users/zuntz/datalad/root2"
NERSC_CONDA_DIR = "/global/cfs/cdirs/desc-wl/users/zuntz/datalad/conda/"
NERSC_GIT_ANNEX_PATH = os.path.join(NERSC_CONDA_DIR, "bin/git-annex-shell")


def create_local_repository(path):
    return Repository.create(path)


def running_on_nersc():
    return "NERSC_HOST" in os.environ


def get_system_desc_root():
    env_var = os.environ.get("DESC_DATA_ROOT")

    if env_var is not None:
        return env_var

    if running_on_nersc():
        return NERSC_ROOT_DIR

    # what should this do if you are not on a shared system?
    # just crash? use an environment variable?
    # use a ~/Library directory?
    raise ValueError("Not decided this behavior yet")
    pass


# Not quite sure about these
def get_nersc_project_repository(project_id):
    # should fail if not running on NERSC
    if not running_on_nersc():
        raise RuntimeError(
            "get_nersc_project_repository only works at NERSC. You want clone_project_repository."
        )


def get_nersc_user_repository(username):
    if not running_on_nersc():
        raise RuntimeError(
            "get_nersc_user_repository only works at NERSC. You want clone_user_repository."
        )


def clone_project_repository(project_id):
    pass


def clone_user_repository(username):
    pass


def clone_nersc_root_repository(nersc_username):
    uri = f"ssh://{nersc_username}@cori.nersc.gov:{NERSC_ROOT_DIR}"
    path = get_system_desc_root()
    d = datalad.api.clone(path=path, source=uri)
    repo = Repository(d.path)
    repo.configure_git_annex()
    repo.get_sub_repositories()
    return repo


class Repository:
    """A local data store, managed by DataLad.

    This might represent the top-level directory containing all
    DESC files, or a subset representing a user or project directory.
    It could also represent a local working space not synced with anything.

    In general, data is not downloaded into a Repository unless specifically
    requested.

    This is a wrapper around the DataLad Dataset object.

    Attributes
    -----------
    path: str
        The path to the directory on disc holding the data
    """

    def __init__(self, path):
        self.path = path

        # This is not intended for user access but
        # might be needed for rescuing broken repos I guess
        self._dataset = datalad.api.Dataset(path)

    @classmethod
    def create(cls, path, parent=None, description=None):
        """Create a new repository at the specified path.

        This will not by synchronized to anything, so if you want
        to share data with DESC you probably want one of these functions instead:
        clone_user_repository, clone_project_repository

        Para

        """
        datalad.api.create(path=path, dataset=parent, description=description)
        repo = cls(path)
        repo.configure_git_annex()
        return repo

    def configure_git_annex(self):
        # We need to tell our repos where they can find git annex on the remote system
        self._dataset.configuration(
            "set",
            [
                ("remote.origin.annex-shell", NERSC_GIT_ANNEX_PATH),
                ("remote.origin.annex-ignore", "false"),
            ],
            recursive=True,
        )

    def pull(self, recursive=True):
        """
        Pull the list of available files from the shared space.

        This doesn't actually download the files, just references
        to them - you will get a link which points to a missing file,
        until you use the download_file method to actually get them.

        Parameters
        ----------
        recursive: bool
            Whether or not to descend to sub-repositories. True by default.
        """
        self._dataset.update(recursive=recursive, how="merge")

    def push(self):
        """
        Push any changes you have saved to the shared NERSC space.
        This only works if this repo is a clone of something.
        """
        self._dataset.push()

    def create_subrepository(self, path, description=None):
        """
        Create a new sub-repository of this one.

        You might use this to split up different things you are working on.

        Parameters
        ----------
        path: str
            The relative path to the new repo, from within this repo.
        """
        return self.create(path=path, parent=self.path, description=description)

    def get_path_for(self, path):
        """
        Get the path to a file or directory within this repository.

        Parameters
        ----------
        path: str
            The relative path to the file or directory, from within this repo.

        """
        return os.path.join(self.path, path)

    def save(self, path, message=None):
        """
        Save the contents of a file or directory.

        This is like a git commit; it doesn't share your work, just save changes
        locally.

        Parameters
        ----------
        path: str
            The relative path to the file or directory, from within this repo.
        message: str, optional
            A commit message to associate with this save
        """
        path = self.get_path_for(path)
        self._dataset.save(path=path, message=message)

    def download_files(self, path):
        """
        Download the contents of a file or directory.

        Parameters
        ----------
        path: str or List[str]
            The relative path to the file or directory, from within this repo,
            or a list of such paths.
        """
        if isinstance(path, str):
            path = self.get_path_for(path)
        else:
            path = [self.get_path_for(p) for p in path]
        print(f"Getting {path} in repo {self.path}")
        self._dataset.get(path=path)
        return path

    def get_sub_repository(self, path):
        path = self.get_path_for(path)
        # Download the references but not the data, if not already present
        if not os.path.exists(path):
            self._dataset.get(path=path, get_data=False)
        repo = Repository(path)
        repo.configure_git_annex()
        return repo

    def get_sub_repositories(self):
        sub_repos = self._dataset.subdatasets()
        paths = [self.get_path_for(sub["gitmodule_url"]) for sub in sub_repos]
        # Download the references but not all the data
        self._dataset.get(path=paths, get_data=False)
        repos = [Repository(p) for p in paths]
        for repo in repos:
            repo.configure_git_annex()
        return repos

    def get_state(self, path=None):
        if path is None:
            statuses = self._dataset.status()

            # Consider the repo as a whole to be modified if any files within
            # are not listed as clean
            for s in statuses:
                if s["state"] in ["modified", "untracked", "added", "deleted"]:
                    return "modified"
            return "clean"
        else:
            return self._dataset.status(path=path)[0]["state"]

    def unlock(self, path):
        return self._dataset.unlock(path=path)
