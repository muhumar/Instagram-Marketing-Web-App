import os
import helper_functions as hf
import sys


def hook():
    if not hf.already_initialized():
        print ("Please init a jet repo before calling other commands")
        return
    # Checks the command was well formed
    if len(sys.argv) != 4:
        print ("Sorry, but that is not a recognized Jet command. Please"
               " either type '$ jet hook <commit|push> inspect' to see "
               "what hooks you already have, or type '$ jet hook <commit|pu"
               "sh> <script_name>' "
               "to add a hook!")
        return
    # If the user is interested in finding out what hook is attached
    if sys.argv[3] == 'inspect':
        # File which stores which hook is being used
        filename = (hf.get_branch_location() + 'hooks')
        # Ensuring the correct argument is in place to know which
        # command to attach to
        if sys.argv[2] == 'commit' or sys.argv[2] == 'push':
            try:
                with open(filename, 'r') as file_:
                    lines = file_.read().splitlines()
            except IOError:
                # No hooks have been added, as the file doesn't exist
                print ("You have no hooks on the %s command" % sys.argv[2])
                return
            # Files are stored:
            #   Push
            #   <filename>
            #   Commit
            #   <filename>
            # So these tests check to see which filename is relevant
            # to the command issued.
            try:
                if lines[0] == sys.argv[2]:
                    print ("The %s command is hooked by:" % sys.argv[2])
                    print ("    %s" % lines[1])
            except IndexError:
                # Index error occurs if empty file
                print ("You have no hooks on the %s command" % sys.argv[2])
            try:
                if lines[2] == sys.argv[2]:
                    print ("The %s command is hooked by:" % sys.argv[2])
                    print ("    %s" % lines[3])
            except IndexError:
                # Index error occurs if only one command had a hook.
                print ("You have no hooks on the %s command" % sys.argv[2])
        else:
            print ("Command isn't recognized by Jet, please form inspect"
                   "commands like '$ jet hook <commit|push> inspect'")
    elif sys.argv[3] == 'remove':
        if sys.argv[2] == 'commit' or sys.argv[2] == 'push':
            # Checks a valid command is entered
            filename = (hf.get_branch_location() + 'hooks')
            # Array used to keep the contents of the other command
            # , as that isn't being deleted
            to_keep = []
            try:
                with open(filename, 'r') as file_:
                    lines = file_.read().splitlines()
                if not lines[0] == sys.argv[2]:
                    to_keep.append(lines[0])
                    to_keep.append(lines[1])
                    print ("Successfully removed the %s hook" % sys.argv[2])
                if not lines[2] == sys.argv[2]:
                    to_keep.append(lines[2])
                    to_keep.append(lines[3])
                    print ("Successfully removed the %s hook" % sys.argv[2])
            except IOError:
                # If IO error then was there even a command to delete?!?
                to_keep.append("")
                to_keep.append("")
            except IndexError:
                # If index error, then it means there was only one command
                # This can therefore just be replaced by blanks
                to_keep.append("")
                to_keep.append("")
                
            # Ensure that the hooks file is kept updated.
            with open(filename, 'w') as myFile:
                myFile.write(to_keep[0] + '\n')
                myFile.write(to_keep[1] + '\n')

        else:
            print ("Command isn't recognized by Jet, please form remove"
                   "commands like '$ jet hook <commit|push> remove'")
    else:
        if not os.path.isfile(sys.argv[3]):
            # Checks the file exists. 
            print ("Couldn't add hook, unrecognized file!")
        else:
            if sys.argv[2] == 'commit' or sys.argv[2] == 'push':
                filename = (hf.get_branch_location() + 'hooks')
                # Follows the same methodology as the delete function until...
                to_keep = []
                try:
                    with open(filename, 'r') as file_:
                        lines = file_.read().splitlines()
                    if not lines[0] == sys.argv[2]:
                        to_keep.append(lines[0])
                        to_keep.append(lines[1])
                        print ("Successfully added the %s hook" % sys.argv[2])
                    if not lines[2] == sys.argv[2]:
                        to_keep.append(lines[2])
                        to_keep.append(lines[3])
                        print ("Successfully added the %s hook" % sys.argv[2])
                except IOError:
                    to_keep.append("")
                    to_keep.append("")
                    print ("Successfully added the %s hook" % sys.argv[2])
                except IndexError:
                    to_keep.append("")
                    to_keep.append("")

                # Same as delete function finished
                # Added the new file and command to the hook file as well
                # as keeping the old one
    
                with open(filename, 'w') as myFile:
                    myFile.write(sys.argv[2] + '\n')
                    myFile.write(sys.argv[3] + '\n')
                    myFile.write(to_keep[0] + '\n')
                    myFile.write(to_keep[1] + '\n')

            else:
                print ("Command isn't recognized by Jet, please form "
                       "commands like '$ jet hook <commit|push> "
                       "<script_name>'")


def run():
    hook()
