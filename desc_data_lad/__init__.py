from .extractor import MetadataExtractor
import datalad.api
import os

from . repository import Repository, create_local_repository

from .repository import clone_nersc_root_repository



# commands like share_with_collaboration, get_from_collaboration

def get_shared_repository_space(root, user=None, project=None):
    if user is None:
        if project is None:
            raise ValueError("Must specify exactly one of project or user")
        kind = "project"
        value = project
    else:
        if project is not None:
            raise ValueError("Must specify exactly one of project or user")
        kind = "user"
        value = user

    if isinstance(root, datalad.api.Dataset):
        root = root.path

    path = os.path.join(root, kind, value)

    # If it exists already just return it
    if os.path.exists(path):
        return datalad.api.Dataset(path)

    return datalad.api.create(path=path, dataset=root)



def share_repository(dataset, root, project=None, user=None):
    """
    
    """
    # Either project or user must be specified
    # If it doesn't exist already, make a 
    d = get_shared_repository_space(root, user=user, project=project)

    # Install this dataset in the global space





# searching
# field = "creation"
# value = "2020.*"
# r = d.search(f"desc.{field}:{value}")
# for f in r:
#     print(f['path'])


# class Repository:
#     def __init__(self, path, root_path):
#         self.path = path
#         self.root_path = root_path


#     def make_