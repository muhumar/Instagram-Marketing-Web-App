from jet_files import helper_functions as hf
import sys
import os


def list_commits():
    if not hf.already_initialized():
        print ("Please init a jet repo before calling other commands")
        return
    try:
        commit_number = sys.argv[2]
        if commit_number == "0":
            # No information is stored about the initial commit,
            # so just alert user
            print ("Initial commit")
            return
    except IndexError:
        # This means the user only wants to see
        #  what commits are stored about this branch.
        folder = hf.get_branch_location()
        commits = hf.get_immediate_subdirectories(folder)
        # Folder names are the commit numbers so... 
        print ("List of all commits. Type '$jet list <commit_number>' "
               "to see more information")
        # Reverse them so they are in numerical order
        commits.reverse()
        for commit_num in commits:
            print ("Commit number: %s" % commit_num)
        # All commits printed, so complete.
        return
    folder = hf.get_branch_location()
    commits = hf.get_immediate_subdirectories(folder)
    found = False
    for commit in commits:
        if commit == commit_number:
            # The commit number was valid...
            # File that contains the list of files edited by that commit
            filename = os.path.join(hf.get_branch_location() +
                                    '/%s/file_log.txt' % commit_number)
            with open(filename, 'r') as file_:
                lines = file_.read().splitlines()
            try:
                # If this doesn't exist,
                # user wants to see what line numbers are in the commit
                line_number = sys.argv[3]
                try:
                    # Check to see if valid line number
                    line = lines[int(line_number)]
                    try:
                        # The file that contains the diff at the commit
                        filename = os.path.join(hf.get_branch_location()
                                                + '/%s/%s/changes.txt' %
                                                (commit_number, line_number))
                        with open(filename, 'r') as file_:
                            to_print = file_.read().splitlines()
                        print ("Changes to file %s" % line)
                        # print (off the diff line by line
                        for line_to_print in to_print:
                            print ("    %s" % line_to_print)
                    # Error loading changes
                    except IOError:
                        print ("That line number was not "
                               "an edited file, therefore there is no more"
                               " information on it")
                # Incorrect line number
                except (IndexError, TypeError):
                    print ("Incorrect line number, type "
                           "'$jet list %s' to see the possible"
                           " lines numbers." % commit_number)
                return
            # User wanted to see the line numbers
            except IndexError:
                print ("Changelog for commit number %s" % commit_number)
                # print (blank line
                print ("")
                count = 0
                # Number them with a counter
                for line in lines:
                    print ("Line number %s:    %s" % (count, line))
                    count += 1
                print ("")
                # To find out more information...
                print ("Type '$jet list %s <line_number>'"
                       " to see more information about that change"
                       % commit_number)
                return

    if not found:
        # The commit number didn't match any of the commits on that branch
        print ("Incorrect commit number, type '$jet list' to see all commits")


def run():
    list_commits()
