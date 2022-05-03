import DescData

# Make a local working data directory. Probably there is a call to DataLad.create
# underlying this if it doesn't exist already.
# Should return an object of a new class of our own design
working_repo = DescData.create_repository("./working-data-dir")

# and save work

# Probably not really necessary, just getting a path which
# must be inside the directory. Maybe skip
filename = working_repo.path_for("filename.txt")
# do something that creates files in ./working-data-dir
with open(filename, "w") as f:
    f.write("I made some cool data\n")

# Just simple call to datalad's save feature
working_repo.save(filename)


# Sharing
# -------

# Get a space in e.g. /path/to/shared/root/users/zuntz
# Should create this as a subdataset of the shared space if it doesn't exist
my_repo = DescData.get_shared_user_repository("zuntz")
# maybe also something like get_shared_project_space?

# Make a subset of that for work I want to share here
shared_repo = my_repo.create_subrepository("project_name")

# Push from my local working directory to this shared directory.
# I guess this will only work if the shared_repo is initially bare?
# Otherwise they should clone it first.
working_repo.push_to(shared_repo)

# Maybe this would be a simpler alternative in cases where they don't want to manage a
# whole repository directory
shared_repo.add_file(filename)


# Another user
# ------------

# Doesn't know who has the data so search for something they want.
# They search metadata fields for the whole collaboration's data.
# This assumes we've already written code to pull out this metadata.
DescData.search(code="CLMM")
# or find files made by me:
DescData.search(creator="zuntz")

# Project 39 is the RedMapper CosmoDC2 project - maybe they want to clone that.
# This should probably do both a "clone" and a "get" in datalad's langauge?
project_dir = DescData.get_shared_project_repository(39)
project_dir.clone_to("./my_project_39_copy")
