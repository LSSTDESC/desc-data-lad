# desc_data_lad

This is a prototype of a DESC tool for managing data produced as part of our science analyses.

The goal is to wrap the subset of DataLad that we need in a much simpler interface.

It will link to a NERSC space which will act as the offical central repository, but allows local mirrors of (subdirectories of) this space.

See https://github.com/LSSTDESC/RequestForComments/issues/13 for some early discussion.

## Installation

Requires datalad, which in turn requires git-annex.  Also requires h5py.

On MacOS, you can get everything like this, using HomeBrew and a virtual environment:

```
brew install git-annex
python -m venv env
. env/bin/activate
pip install -e .
```


## Data Layout

Suggested layout for the central root data repository:

```
root/users - for per-user files
root/users/johndoe - for user with (NERSC) user name johndoe
root/users/test - a test user anyone can commit to
root/projects - for per-project files
root/projects/7 - for project number 7
root/production/ - for centrally chosen "official" files
root/dc2 - for DC2
```

## TODO

### General

- Finish the functions to get and clone project and user directories from the local root
- Add equivalents for the production directories
- Figure out how to set permissions on added files and directories.
    - Everything should be group-readable
    - User directories should only be user-writable
    - Project directories should be group-writable
    - Production directories?
- Add a log command to show all recent file changes (recursively) in some readable form
- Check that things work recursively as we want
- Set up the actual directory structure at NERSC, instead of the current test on in my directory
- Add a utility function `download_file_from_desc` mirroring `upload_file_to_desc`

### Searching & Metadata


- Add methods to add externally-stored per-file and per-repository metadata
- Write the `search` function to return a list of file and directory paths from the shared space matching search patterns
- Add metadata to `upload_file_to_desc`
- (maybe) Get the metadata code in `extractor.py` to run to collate DESC metadata.  Here's some code that might help:
```
import pprint
import datalad.api
import glob
files=glob.glob("example-inputs/*.hdf5")
d = datalad.api.Dataset(".")
meta = d.extract_metadata(types=["desc"], files=files)
print(meta)
for item in meta[1:]:
    pprint.pprint(item['path'])
    pprint.pprint(item['metadata']['desc'])



# Getting all my files
r = d.search('zuntz', mode='egrep')
for item in r:
    pprint.pprint(item)

r = d.metadata("example-inputs/photometry_catalog.hdf5")
print(r[0]['metadata']['desc'])
```


### Remote access

- Add a function to make a local clone of the whole root structure
- Decide on a default location for local clones on macos and linux. Maybe `~/.ddl/root` ?
- Add function to synchronize a local root with NERSC root

### UI

- add home directory configuration to save nersc user name (if not on NERSC)
- add a command-line script `ddl`  as a user interface to common commands. e.g. (just examples)
    - ddl share filename.txt --meta code=mycode  # into my user directory, if we can determine that
    - ddl share --project 17 --sub project_subdirs/subdir1 filename.txt
    - ddl clone --root
    - ddl get --project 17 project_subdirs/subdir1/filename.txt


#### Documentation

- Set up ReadTheDocs
- write ReadTheDocs pages include auto-generated api pages
