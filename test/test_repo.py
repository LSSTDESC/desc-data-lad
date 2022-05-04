import desc_data_lad as ddl
import tempfile
import os
import pytest
import datetime
import contextlib


def get_test_user():
    try:
        return os.environ["DDL_TEST_USER"]
    except KeyError:
        raise pytest.skip("Set the environment variable DDL_TEST_USER to run NERSC-related tests")

@contextlib.contextmanager
def test_dir():
    test_dir = os.environ.get("DDL_TEST_DIR")
    if test_dir is None:
        with tempfile.TemporaryDirectory() as test_dir:
            yield test_dir
    else:
        try:
            yield test_dir
        finally:
            pass
    

def test_local_repo():
    with test_dir() as dirname:

        repo = ddl.create_local_repository(f"{dirname}/repo")

        # repo should be clean to start with
        assert repo.get_state() == 'clean'

        filename = repo.get_path_for("filename.txt")
        assert filename == f"{dirname}/repo/filename.txt"

        # Save text to file
        text = "I made some cool data\n"
        with open(filename, "w") as f:
            f.write(text)

        # Check that saving changes the status from untracked to clean
        assert repo.get_state() == 'modified'
        assert repo.get_state(filename) == 'untracked'
        repo.save(filename)
        assert repo.get_state(filename) == 'clean'


        # cannot edit files until they are unlocked

        repo.unlock(filename)
        # Make an edit
        text2 = "I made some changes to my cool data\n"
        with open(filename, "w") as f:
            f.write(text2)

        assert repo.get_state() == "modified"
        assert repo.get_state(filename) == "modified"

        repo.save(filename)

        assert repo.get_state() == "clean"
        assert repo.get_state(filename) == "clean"



def test_nersc_root_clone():
    # Get the temporary value of this variable
    # as we are overwriting it in this test
    ddr = os.environ.get("DESC_DATA_ROOT")
    user = get_test_user()

    try:
        with test_dir() as dirname:
            root = os.path.join(dirname, "root")

            # Check we can clone the central NERSC data repository
            os.environ["DESC_DATA_ROOT"] = root
            repo = ddl.clone_nersc_root_repository(user)
            repo.pull()
            assert os.path.exists(root)

            # Check we can download the readme file correctly
            readme_file = repo.download_files("README.txt")
            with open(readme_file) as f:
                readme = f.read()
            assert readme.startswith("DESC Shared Data")

            user_repo = repo.get_sub_repository(f"users/{user}")
            user_filename = user_repo.download_files("joe_test_file.txt")

            with open(user_filename) as f:
                user_text = f.read()
            assert user_text.startswith("This is a test file Joe made")

    finally:
        if ddr is not None:
            os.environ["DESC_DATA_ROOT"] = ddr


def test_share_file_with_desc():
    user = get_test_user()
    timestamp = datetime.datetime.now().isoformat()
    filename = "test_time_stamp.txt"

    with open(filename, "w") as f:
        f.write(timestamp)

    ddl.share_file_with_desc(filename, user, testing=True, new_file=False)
    os.remove(filename)

def temp_test():
    os.environ["DESC_DATA_ROOT"] = "data/new-root"
    user = get_test_user()
    repo = ddl.clone_nersc_root_repository(user)
    repo.pull()
    repo.download_files("users/zuntz")

if __name__ == '__main__':
    # test_local_repo()
    # test_nersc_root_clone()
    # test_share_file_with_desc()

    temp_test()