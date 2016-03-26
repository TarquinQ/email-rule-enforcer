import os.path


def get_filename_from_fullpath(fullpath):
    return os.path.split(fullpath)[1]


def get_pathname_from_fullpath(fullpath):
    return os.path.split(fullpath)[0]


def file_exists(fullpath):
    return os.path.is_file(fullpath)


def path_exists(fullpath):
    return os.path.exists(fullpath)

