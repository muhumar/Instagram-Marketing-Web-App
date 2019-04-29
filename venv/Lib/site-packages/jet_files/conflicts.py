import os
import sys
from jet_files import helper_functions as hf


def resolve():
    if not hf.already_initialized():
        print ("Please init a jet repo before calling other commands")
        return
    if not len(sys.argv) == 3:
        print ("Please form resolve statements '$jet resolve <filename>'")
    # Allows the use of relative path names to mention files
    file_to_resolve = os.path.join(os.getcwd() + '/' + sys.argv[2])
    result = hf.resolve_conflict(file_to_resolve)
    if result == -1:
        print ("That file does not need resolving")
        return
    print ("File has been resolved")
    # If result is positive, it means there's more files left to resolve.
    if result > 0:
        print ("You have %s conflicts left to resolve" % result)
    else:
        print ("All files resolved, remember to commit!")


def list_conflicts():
    if not hf.already_initialized():
        print ("Please init a jet repo before calling other commands")
        return
    # Gets all conflicts that Jet can find, and presents them in a readable way
    conflicts = hf.get_conflicts()
    if conflicts:
        print ("You have the following merge conflicts to resolve:")
        for conflict in conflicts:
            print ("    %s" % conflict)
    else:
        print ("No merge conflicts are present!")
