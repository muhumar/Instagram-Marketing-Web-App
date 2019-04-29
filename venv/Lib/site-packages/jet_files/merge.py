import os
import sys
from jet_files import helper_functions as hf
from jet_files import commit_changeset, add


def merge():
    if not hf.already_initialized():
        print ("Please init a jet repo before calling other commands")
        return
    # Checks to see if a branch was specified
    if not len(sys.argv) == 3:
        print ("Please form merge commands '$jet merge"
               "<branch>' - where <branch> is the branch to merge into"
               "the current one. \nThe merge will make a new commit"
               " in the current branch")
        return
    # Loads the changeset file, to see if there are any uncommitted changes
    filename = os.path.join(hf.get_jet_directory() + '/.jet/changeset.txt')
    # Assume there are no changed files
    changed_files = False
    # This file existing means there are uncommitted changes
    if os.path.isfile(filename):
        changed_files = True
    # Check if any changed files which haven't been added.
    if len(hf.get_changed_files(None, None)) > 0:
        changed_files = True
    # Can't merge with changed files, so display error message
    if changed_files:
        print ("You can't merge until you commit....")
        return
    branch = sys.argv[2]
    branches_path = os.path.join(hf.get_jet_directory() + '/.jet/branches/')
    # Ensuring that there are multiple branches present
    if os.path.exists(branches_path):
        # Ensures that the branch name is valid
        #  by checking if a folder exists for it
        if not os.path.exists(os.path.join(branches_path + sys.argv[2])):
            print ("Invalid branch name, please try again.")
            return

    # Calls the helper function to actually do the merge
    hf.merge(branch)
    # Calls the add method ot add the new changes to a changeset
    add.add(verbose=False)
    # Calls commit to commit and save the changes from the merge.
    commit_changeset.commit("Merged branch %s into branch %s."
                            % (branch, hf.get_branch()), verbose=False)
    # Commit number used is found for printing
    commit_number_used = hf.get_new_commit_number() - 1
    # Tell user everything worked
    print ("Merged branch %s into branch current branch %s."
           "\nCommitted merge with commit number %s." % (hf.get_branch(),
                                                         branch,
                                                         commit_number_used))


def run():
    merge()
