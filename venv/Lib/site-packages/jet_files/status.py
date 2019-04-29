import os
from jet_files import helper_functions as hf


def status():
    if not hf.already_initialized():
        print ("Please init a jet repo before calling other commands")
        return
    # Pre-loading all the information, to prevent duplicate file reading
    # And to speed things up
    cwd = os.getcwd()
    branch = hf.get_branch()
    branch_location = hf.get_branch_location_param(branch)
    jet_directory = hf.get_jet_directory()

    current_files = hf.get_current_files(jet_directory)
    stored_files_and_hashes = hf.get_stored_files_and_hashes()
    stored_files = hf.get_stored_files(stored_files_and_hashes)
    changed_files = hf.get_changed_files(current_files,
                                         stored_files_and_hashes)
                                         
    print ("You are working on branch %s" % branch)
    # If the amount of files is equal, and nothing has been changed
    #  - we're done
    if len(current_files) == len(stored_files)\
            and len(changed_files) == 0:
        print ("Nothing has changed!")
    else:
        # otherwise, there has been a change so work out what it is and print
        print ("Your repo has changed since the last commit")
        files_in_changeset = hf.get_files_in_changeset(branch_location)
        new_files = hf.get_new_files(current_files, stored_files)
        # Only execute if new files exist
        if new_files:
            new_files_in_changeset =\
                hf.get_new_files_in_changeset(files_in_changeset)
            # Only execute if the new files are in the changeset
            if new_files_in_changeset:
                unadded_new = []
                for new_file in new_files:
                    # If there's a new file and hasn't been added yet, say so
                    if new_file not in new_files_in_changeset:
                        unadded_new.append(new_file)
                print ("New files in changeset:")
                # print all the new files in the changeset in green
                for new_file_in_changeset in new_files_in_changeset:
                    print (hf.BColors.GREEN +
                           "    %s" % hf.relative(new_file_in_changeset, cwd) +
                           hf.BColors.ENDC)
            else:
                # Otherwise all new files are unadded
                unadded_new = new_files
            # If any do exist..
            if unadded_new:
                print ("New files:")
                for new_file in unadded_new:
                    # Loop through and print (them out in green
                    print (hf.BColors.GREEN +
                           "    %s" % hf.relative(new_file, cwd) +
                           hf.BColors.ENDC)
        deleted_files = hf.get_deleted_files(current_files, stored_files)
        # Only execute if deleted files exist
        if deleted_files:
            deleted_files_in_changeset =\
                hf.get_deleted_files_in_changeset(files_in_changeset)
            # Only execute if there are deleted files added to the changeset
            if deleted_files_in_changeset:
                unadded_deleted = []
                for deleted_file in deleted_files:
                    # check they're not added 
                    if deleted_file not in deleted_files_in_changeset:
                        unadded_deleted.append(deleted_file)
                print ("Deleted files in changeset:")
                # print (the added ones in red text
                for deleted_file_in_changeset in deleted_files_in_changeset:
                    print (hf.BColors.RED +
                           "    %s" % hf.relative(deleted_file_in_changeset,
                                                  cwd)
                           + hf.BColors.ENDC)
            else:
                # Otherwise all the deleted files are unadded
                unadded_deleted = deleted_files
            if unadded_deleted:
                # If there are any..
                print ("Deleted files:")
                for deleted_file in unadded_deleted:
                    # print (them off in red
                    print (hf.BColors.RED +
                           "    %s" % hf.relative(deleted_file, cwd) +
                           hf.BColors.ENDC)
        # Only execute if some files have been changed
        if changed_files:
            changed_files_in_changeset =\
                hf.get_changed_files_in_changeset(files_in_changeset)
            # Only execute if there's added files that have been changed
            if changed_files_in_changeset:
                unadded = []
                for file_ in changed_files:
                    # Separate added and non-added files
                    if file_ not in changed_files_in_changeset:
                        unadded.append(file_)
                print ("Changed files in changeset:")
                for changed_file_in_changeset in changed_files_in_changeset:
                    # print off added changed files in yellow
                    print (hf.BColors.YELLOW +
                           "    %s" % hf.relative(changed_file_in_changeset,
                                                  cwd)
                           + hf.BColors.ENDC)
            else:
                # Otherwise they're all unadded!
                unadded = changed_files
            # If there are any..
            if unadded:
                print ("Changed files:")
                for changed_file in unadded:
                    # print filenames off in  yellow!
                    print (hf.BColors.YELLOW +
                           "    %s" % hf.relative(changed_file, cwd) +
                           hf.BColors.ENDC)


def run():
    status()
