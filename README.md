# desc_data_lad

This is a prototype of a DESC tool for managing data produced as part of our science analyses.

It will link to a NERSC space which will act as the offical central repository, but allows local mirrors of (subdirectories of) this space.

See https://github.com/LSSTDESC/RequestForComments/issues/13 for some early discussion.

## Installation

This version requires datalad, which in turn requires git-annex.  Also requires h5py.

On MacOS, you can get everything like this, using HomeBrew and a virtual environment:

```
brew install git-annex
python -m venv env
. env/bin/activate
pip install -e .
```
