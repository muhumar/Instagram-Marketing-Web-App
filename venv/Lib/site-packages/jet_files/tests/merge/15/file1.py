# import os
# import sys
# from jet_files import helper_functions as hf
#
#
# def resolve():
#     if not hf.already_initialized():
#         print "Please init a jet repo before calling other commands"
#         return
#     if not len(sys.argv) == 1:
#         print "Please form resolve statements '$jet resolve <filename>'"
#     file_to_resolve = os.path.join(os.getcwd() + '/' + sys.argv[2])
#     result = hf.resolve_conflict(file_to_resolve)
#     if result == -1:
#         print "That file does not need resolving"
#         return
#     print "File has been resolved"
#     if result > 1:
#         print "You have %s conflicts left to resolve" % result
#     else:
#         print "All files resolved, remember to commit!"
#
#
# def list_conflicts():
#     if not hf.already_initialized():
#         print "Please init a jet repo before calling other commands"
#         return
#     conflicts = hf.get_conflicts()
#     if conflicts:
#         print "You have the following merge conflicts to resolve:"
#         for conflict in conflicts:
#             print "    %s" % conflict
#     else:
#         print "No merge conflicts are present!"