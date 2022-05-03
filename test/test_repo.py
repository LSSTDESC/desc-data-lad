import desc_data_lad as ddl
import datalad
import tempfile
import os


def test_local_repo():
    with tempfile.TemporaryDirectory() as dirname:

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
    ddr = os.environ.get("DESC_DATA_ROOT")

    try:
        with tempfile.TemporaryDirectory() as dirname:
            root = os.path.join(dirname, "root")

            # Check we can clone the central NERSC data repository
            print("Testing we can clone NERSC root")
            os.environ["DESC_DATA_ROOT"] = root
            repo = ddl.clone_nersc_root_repository("zuntz")
            repo.synchronize()
            assert os.path.exists(root)
            print(os.listdir(root))

            # Check we can download the readme file correctly
            print("Testing we can download README file")
            readme_file = repo.get_file("README.txt")
            with open(readme_file) as f:
                readme = f.read()
            assert readme.startswith("DESC Shared Data")

            print("Testing for sub-repo access")
            user_repo = repo.get_sub_repository("users/zuntz")
            print(os.listdir(user_repo.path))
            user_filename = user_repo.get_file("joe_test_file.txt")

            with open(user_filename) as f:
                user_text = f.read()
            assert user_text.startswith("This is a test file Joe made")


    finally:
        if ddr is not None:
            os.environ["DESC_DATA_ROOT"] = ddr


if __name__ == '__main__':
    # test_local_repo()
    test_nersc_root_clone()
