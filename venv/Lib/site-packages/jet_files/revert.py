import os
from jet_files import helper_functions as hf
import sys


def revert():
    if not hf.already_initialized():
        print ("Please init a jet repo before calling other commands")
        return
    # Checks to make sure the command was well formatted
    if len(sys.argv) != 4:
        print ("Please form revert commands by typing"
               " '$jet revert <branch_name> <commit_number>' \n"
               "Remember the default branch is called 'master'")
        return

    # The branches path where information on the branches is
    branches_path = os.path.join(hf.get_jet_directory() + '/.jet/branches/')
    # Checks more than one branch exists
    if os.path.exists(branches_path):
        # If it's master, different file paths
        if not sys.argv[2] == 'master':
            # Check that the branch name specified exists.
            if not os.path.exists(os.path.join(branches_path + sys.argv[2])):
                print ("Invalid branch name, aborting revert")
                print ("Please form revert commands by typing"
                       " '$jet revert <branch_name> <commit_number>' \n"
                       "Remember the default branch is called 'master'")
                return

    # Check that the commit number entered is valid.
    if hf.is_valid_commit_number(sys.argv[3], sys.argv[2]):
        # DOUBlE check that the user really really wants that revert to happen.
        response = raw_input("Revert changes all your files back to the "
                             "point they were in at the commit number "
                             "specified. Any changes that are not committed"
                             " will be lost forever. \nAre you sure you wish"
                             " to revert? (yes/no) ")
        # Accept y as well as the suggested yes
        if response == 'yes' or response == 'y':
            print ("Reverting....please wait...")
            # Performing the actual revert.
            hf.revert(sys.argv[2], sys.argv[3])
            # Alert user it was completed.
            print ("Revert finished. You are now at the state of "
                   "commit number %s in branch %s"
                   % (sys.argv[3], sys.argv[2]))
        # User wishes to cancel the request
        elif response == 'no' or response == 'n':
            print ("Cancelling revert")
        # User wasn't sure what to respond.
        else:
            print ("Invalid response, cancelling")
    else:
        # Commit number didn't work, give error message
        print ("Commit number is invalid, aborting revert.")
        print ("Please form revert commands by typing"
               " '$jet revert <branch_name> <commit_number>' \n"
               "Remember the default branch is called 'master'")


def run():
    revert()
