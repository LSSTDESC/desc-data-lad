from .repository import NERSC_CONDA_DIR, NERSC_ROOT_DIR, running_on_nersc
import subprocess

def share_desc_file(path, user=None, project=None, subdir=None, message=None):
    # copy a file that is not in a repository to a DESC space

    # Find the NERSC directory this should go in
    if user is None:
        if project is None:
            raise ValueError("Must specify exactly one of project or user")
        remote_dir = f"project/{project}"
    else:
        if project is not None:
            raise ValueError("Must specify exactly one of project or user")
        remote_dir = f"user/{user}"
    if subdir is not None:
        remote_dir = os.path.join(remote_dir, subdir)
    filename = os.path.basename(path)
    target_path = os.path.join(NERSC_ROOT_DIR, remote_dir, filename)

    # Run save on the relevant path in the repo over ssh
    cmd = f"bash -c 'module load python && conda activate {NERSC_CONDA_DIR} && datalad save {target_path}'"

    if running_on_nersc():
        # if we are on NERSC, just copy it in directly
        shutil.copy(path, target_path)
        subprocess.check_call(cmd)
    else:
        # Otherwise, scp the file to the target location
        man = datalad.support.sshconnector.SSHManager()
        con = man.get_connection("ssh://zuntz@cori.nersc.gov")
        con.put(path, target_path)
        con(cmd)



