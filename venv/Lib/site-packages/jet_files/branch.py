import os
from shutil import copyfile, rmtree
import helper_functions as hf
import sys


def branch(branch_name):
    # Checking that there is no un-committed changed files
    filename = os.path.join(hf.get_branch_location() + 'changeset.txt')
    # Assume nothing has changed...
    changed_files = False
    # If there is a uncommitted changeset...
    if os.path.isfile(filename):
        changed_files = True
    # If any hashes don't match up
    if len(hf.get_changed_files(None, None)) > 0:
        changed_files = True
    # Error if there are uncommitted changed files...
    if changed_files:
        print ("You can't branch until you commit....")
        return
    # END changed files check

    # Checking that the given branch name is ok
    branches_path = os.path.join(hf.get_jet_directory() + '/.jet/branches/')
    if os.path.exists(branches_path):
        if os.path.exists(os.path.join(branches_path + branch_name))\
                or branch_name == 'master':
            # Name exists, error 
            print ("Already a branch with that name... please try another!")
            return
        else:
            # Make directory for the branch
            os.mkdir(os.path.join(branches_path + branch_name))
    else:
        # Make the required directories
        os.mkdir(os.path.join(hf.get_jet_directory() + '/.jet/branches/'))
        os.mkdir(os.path.join(branches_path + branch_name))
    # All ok, starting branching.

    f = []  # Contains the full path and filenames of all files to be branched
    filenames_list = []  # Contains all the file names (not full path)
    # Trawl all files in the users repo'd directory
    for (dirpath, dirnames, filenames) in os.walk(hf.get_jet_directory()):
        for filename in filenames:
            # Make sure no ignored files are present
            if hf.filter_one_file_by_ignore(filename):
                # No jet files to be included
                if not '.jet' in dirpath:
                    # Add files name to filename list
                    filenames_list.append(filename)
                    # Add full path and filename to f
                    f.append(os.path.join(dirpath, filename))

    # Create a new file listing all the current files and hashes at this point
    file_name = os.path.join(hf.get_jet_directory()
                             + '/.jet/branches/%s/latest_saved_files'
                             % branch_name)
    with open(file_name, 'w') as file_:
        for file_to_add in f:
            file_.write(file_to_add + "\n")
            file_.write(hf.checksum_md5(file_to_add) + "\n")
    # Make a folder for the init commit of the branch
    os.mkdir('.jet/branches/%s/0/' % branch_name)
    # Store the files that are in the branch at the first commit
    file_name = os.path.join(hf.get_jet_directory()
                             + '/.jet/branches/%s/0/file_log.txt'
                             % branch_name)
    with open(file_name, 'w') as file_:
        for file_to_add in f:
            file_.write(file_to_add + "\n")

    count = 0
    for file_to_add in f:
        # Make a folder to store details of that file
        folder = os.path.join(hf.get_jet_directory() +
                              '/.jet/branches/%s/%s/%s' % (branch_name,
                                                           0,
                                                           count))
        os.mkdir(folder)
        # Storing the full filename
        filename = os.path.join(hf.get_jet_directory() +
                                '/.jet/branches/%s/%s/%s/filename.txt'
                                % (branch_name, 0, count))
        with open(filename, 'w') as myFile:
                myFile.write(file_to_add)
        filename = filenames_list[count]
        # Store the contents of the file
        copyfile(file_to_add, os.path.join(hf.get_jet_directory()
                                           + '/.jet/branches/%s/0/%s/%s'
                                           % (branch_name,
                                              count,
                                              filename)))
        count += 1

    # Branch making complete, store details of branch
    print ("Branch %s made" % branch_name)
    # Storing parent branch
    filename = os.path.join(hf.get_jet_directory()
                            + '/.jet/branches/%s/parent' % branch_name)
    old_branch = hf.get_branch()
    old_commit = hf.get_commit()
    with open(filename, 'w') as file_:
        file_.write(old_branch)  # Old branch name
        file_.write('\n')
        file_.write(old_commit)  # Old branch commit number
                                 # from where branched off

    # Now storing which is the current branch
    filename = os.path.join(hf.get_jet_directory() + '/.jet/branch')
    with open(filename, 'w') as file_:
        file_.write(branch_name)  
    # Now storing the commit number (0)
    filename = os.path.join(hf.get_jet_directory() + '/.jet/current_commit')
    with open(filename, 'w') as file_:
        file_.write("0")
    # All done
    print ("You are now working in branch %s" % branch_name)


def run():
    if not hf.already_initialized():
        print ("Please init a jet repo before calling other commands")
        return
    if len(sys.argv) != 3:
        print ("Please form branch commands by typing"
               " $jet branch <branch_name>")
        return
    branch_name = sys.argv[2]
    branch(branch_name)


def switch():
    if not hf.already_initialized():
        print ("Please init a jet repo before calling other commands")
        return
    if len(sys.argv) != 3:
        print ("Please form your switch commands $jet switch <branch_name>")
        return

    # Checks for any changed files, as you must have committed first!!!
    filename = os.path.join(hf.get_branch_location() + 'changeset.txt')
    # Assumes nothing has changed
    changed_files = False
    # If there is a changeset uncommitted
    if os.path.isfile(filename):
        changed_files = True
    # If any hashes don't match up...
    if len(hf.get_changed_files(None, None)) > 0:
        changed_files = True
    # Error if anything changed!! 
    if changed_files:
        print ("You can't switch branch until you commit....")
        return

    # Master info stored separately, hence the if statement
    if sys.argv[2] == 'master':
        # Record master as the branch currently on
        filename = os.path.join(hf.get_jet_directory() + '/.jet/branch')
        with open(filename, 'w') as file_:
            file_.write(sys.argv[2])
        # Do the revert process
        hf.revert(sys.argv[2], hf.get_highest_commit(sys.argv[2]))
        # Update the latest saved files with ones from new branch
        filename = os.path.join(hf.get_branch_location()
                                + 'latest_saved_files')
        # Delete previous save
        os.remove(filename)
        with open(filename, 'w') as file_:
            for file_to_add in hf.get_current_files(None):
                file_.write(file_to_add + "\n")
                file_.write(hf.checksum_md5(file_to_add) + "\n")
        # All done!
        print ("Successfully switched to branch %s" % sys.argv[2])
        return
    # Only here if the branch to switch to isn't master
    branches_path = os.path.join(hf.get_jet_directory() + '/.jet/branches/')
    if os.path.exists(branches_path):
        if os.path.exists(os.path.join(branches_path + sys.argv[2])):
            filename = os.path.join(hf.get_jet_directory() + '/.jet/branch')
            # Setting the new branch name as current branch
            with open(filename, 'w') as file_:
                file_.write(sys.argv[2])
            hf.revert(sys.argv[2], hf.get_highest_commit(sys.argv[2]))
            filename = os.path.join(hf.get_branch_location()
                                    + 'latest_saved_files')
            os.remove(filename)
            with open(filename, 'w') as file_:
                for file_to_add in hf.get_current_files(None):
                    file_.write(file_to_add + "\n")
                    file_.write(hf.checksum_md5(file_to_add) + "\n")
            print ("Successfully switched to branch %s" % sys.argv[2])
        else:
            print ("Invalid branch name")
    else:
        print ("Invalid branch name")


def display():
    # This method shows all the branches and their parents
    #  and prints to the console
    if not hf.already_initialized():
        print ("Please init a jet repo before calling other commands")
        return
    print ("Branch name (parent)")
    print ("Master(root)")
    branches_path = os.path.join(hf.get_jet_directory() + '/.jet/branches/')
    if os.path.exists(branches_path):
        branches = hf.get_immediate_subdirectories(branches_path)
        # Directories are named after the branch, so grab names from here.
        for b in branches:
            print ("%s (%s)" % (b, hf.get_parent(b)))

    # Friendly reminder what branch is the current one.
    print ("You are currently on branch %s" % hf.get_branch())


def delete_branch():
    if len(sys.argv) != 3:
        print ("Please form your delete commands $jet delete <branch_name>")
        return
    branches_path = os.path.join(hf.get_jet_directory() + '/.jet/branches/')
    # Check that the branches directory is there
    if os.path.exists(branches_path):
        if not os.path.exists(os.path.join(branches_path + sys.argv[2])):
            print ("Invalid branch name, please try again.")
            return
    else:
        print ("Invalid branch name, please try again")
        return
    if sys.argv[2] == 'master':
        # Master cannot be deleted because every other branch is a child of it.
        print ("Cannot delete master")
        return
    delete(sys.argv[2])


def delete(branch_name):
    # This method deletes the branch and all records of it from the repository.
    directory = os.path.join(hf.get_jet_directory()
                             + '/.jet/branches/%s/' % branch_name)
    rmtree(directory)
    print ("Deleted")
