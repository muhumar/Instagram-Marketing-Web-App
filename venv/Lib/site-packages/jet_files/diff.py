import os
import sys
from jet_files import helper_functions as hf


def diff():
    # A simple method that gives the difference between the current
    # version of the filename
    # And the version specified by the branch and commit number.
    if not hf.already_initialized():
        print ("Please init a jet repo before calling other commands")
        return
    if len(sys.argv) != 5:
        print ("Please form diff commands "
               "'$jet diff <filename> <branch> <commit_number>'")
    # Ensure the filename is valid
    if os.path.exists(sys.argv[2]):
        # Allow for relative pointer towards the file
        full_file_name = os.path.join(os.getcwd() + '/' + sys.argv[2])
        # Get the contents of the file at the specified point
        old_file = hf.get_file_at(sys.argv[3], sys.argv[4], full_file_name)
        # If it's None, means it wasn't at that point, or an error has occurred
        if old_file is None:
            print ("File could not be found at the point specified")
            return
        # Get the contents of the file currently 
        with open(full_file_name, 'r') as file_:
            current_file = file_.read().splitlines()
        # Calculate the difference...
        difference = hf.diff(old_file, current_file)
        print (difference)
    else:
        print ("Invalid filename.")


def run():
    diff()
