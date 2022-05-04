from .repository import NERSC_CONDA_DIR, NERSC_ROOT_DIR, running_on_nersc
import subprocess
import os
import datalad.support.sshconnector


def share_file_with_desc(
    local_path,
    user,
    new_file=True,
    project=None,
    subdir=None,
    message=None,
    testing=False,
):
    """Copy a stand-alone file to a DESC space.

    In general it's better to have a local Repository mirroring the
    main data store on NERSC, which you can do using the Repository
    class and related functions.

    But sometimes you may have a single stand-alone file or directory
    that you want to share, especially when getting started.

    This function copies your file into either your personal user-space
    on NERSC, or into a shared project space.
    """

    # Find the NERSC directory this should go in
    if testing:
        remote_dir = "users/test"
    elif project is not None:
        remote_dir = f"project/{project}"
    else:
        remote_dir = f"users/{user}"
    if subdir is not None:
        remote_dir = os.path.join(remote_dir, subdir)

    filename = os.path.basename(local_path)
    target_dir = os.path.join(NERSC_ROOT_DIR, remote_dir)
    target_path = os.path.join(target_dir, filename)

    unlock_command = f"bash -c 'module load python && conda activate {NERSC_CONDA_DIR} && cd {target_dir} && datalad unlock {target_path}'"
    # Run save on the relevant path in the repo over ssh
    save_command = f"bash -c 'module load python && conda activate {NERSC_CONDA_DIR} && cd {target_dir} && datalad save {target_path}'"

    if running_on_nersc():
        # if we are on NERSC, just copy it in directly
        if not new_file:
            print(unlock_command)
            subprocess.check_call(unlock_command)

        print(f"Copying {local_path} -> {target_path}")
        shutil.copy(local_path, target_path)

        print(f"Saving {target_path} at NERSC")
        subprocess.check_call(save_command)
    else:
        # Otherwise, scp the file to the target location
        man = datalad.support.sshconnector.SSHManager()
        con = man.get_connection(f"ssh://{user}@cori.nersc.gov")

        if not new_file:
            print(f"Unlocking NERSC file {target_path}")
            con(unlock_command)

        print(f"SCP'ing {local_path} -> {target_path}")
        con.put(local_path, target_path)

        print(f"Saving {target_path} at NERSC")
        con(save_command)
