from shutil import copyfile
import helper_functions as hf
import sys
import os


def commit_changeset():
    if not hf.already_initialized():
        print ("Please init a jet repo before calling other commands")
        return
    if hf.is_conflicts():
        print ("You can't commit with outstanding conflicts...")
        return
    # Login required in order to put a name with the commit
    if not hf.logged_in():
        print ("You must login before commiting! To do this type:"
               " $jet login <username>")
        return

    hook = hf.get_commit_hook()
    # The hook will be null of it doesn't exist
    if hook:
        result = hf.run_hook(hook)
        if result:
            print ("Hook passed.")
        else:
            print ("Hook Failed. Not commiting")
            return
    # Must have the -m and all arguments present
    if len(sys.argv) != 4 or sys.argv[2] != "-m":
        print ("Commit commands need to be formed by typing:"
               " $jet commit -m \"Your message here\"")
    else:
        commit(sys.argv[3], verbose=True)


def commit(message, verbose):
    filename = os.path.join(hf.get_branch_location() + 'changeset.txt')
    # Checks to see if there are any files in the changeset at all...
    if os.path.isfile(filename):
        files_in_changeset = hf.get_files_in_changeset(None)
        new_files_in_changeset\
            = hf.get_new_files_in_changeset(files_in_changeset)
        deleted_files_in_changeset\
            = hf.get_deleted_files_in_changeset(files_in_changeset)
        changed_files_in_changeset\
            = hf.get_changed_files_in_changeset(files_in_changeset)
        new_commit_number = hf.get_new_commit_number()
        folder = os.path.join(hf.get_branch_location() +
                              '/%s/' % new_commit_number)
        # Making a folder to put all the details of the commit in
        os.mkdir(folder)
        filename = os.path.join(hf.get_branch_location()
                                + '/%s/file_log.txt'
                                % new_commit_number)
        # Record which files changed
        with open(filename, 'w')\
                as file_:
            for file_to_add in changed_files_in_changeset:
                file_.write("~" + file_to_add + "\n")
            for file_to_add in new_files_in_changeset:
                file_.write("+" + file_to_add + "\n")
            for file_to_add in deleted_files_in_changeset:
                file_.write("-" + file_to_add + "\n")

        # Recording commit message, and who committed it.
        filename = os.path.join(hf.get_branch_location() + '/%s/info'
                                % new_commit_number)
        with open(filename, 'w') as file_:
            file_.write(hf.get_username() + '\n')
            file_.write(message)
        # Recording which commit the HEAD is pointing to
        filename = os.path.join(hf.get_jet_directory()
                                + '/.jet/current_commit')
        with open(filename, 'w') as file_:
            file_.write(str(new_commit_number))

        # Counter to make unique folder name for each file change
        counter = 0
        for file_ in changed_files_in_changeset:
            # Making the folder
            folder = os.path.join(hf.get_branch_location()
                                  + '/%s/%s' % (new_commit_number,
                                                counter))
            os.mkdir(folder)

            # Recording the full filename 
            filename = os.path.join(hf.get_branch_location()
                                    + '/%s/%s/filename.txt'
                                    % (new_commit_number, counter))
            with open(filename, 'w') as myFile:
                myFile.write(file_)
            
            # Recording the diff from last commit
            filename = os.path.join(hf.get_branch_location()
                                    + '/%s/%s/changes.txt'
                                    % (new_commit_number, counter))
            description = hf.get_change_description(file_)
            if description:
                with open(filename, 'w') as myFile:
                    myFile.write(description)
            else:
                # If no difference, put the contents of the file in there
                copyfile(file_, filename)
            counter += 1

        # Remove files from changeset as they have been committed.
        filename = os.path.join(hf.get_branch_location()
                                + 'changeset.txt')
        os.remove(filename)

        # Section that updates the latest stored files

        # Gets all previous files
        lines = hf.get_stored_files(None)
        # Adds newly saved files
        lines.extend(new_files_in_changeset)
        to_keep = []
        for line in lines:
            # Only adds files not deleted
            if line not in deleted_files_in_changeset:
                to_keep.append(line)
        filename = os.path.join(hf.get_branch_location()
                                + 'latest_saved_files')
        # Delete old record
        os.remove(filename)
        with open(filename, 'w') as file_:
            for file_to_add in to_keep:
                file_.write(file_to_add + "\n")
                # Including new checksum of file, for status/diff checks
                file_.write(hf.checksum_md5(file_to_add) + "\n")
        if verbose:
            # Done!
            print ("Commiting")
    else:
        if verbose:
            print ("Please add files to commit using "
                   "jet add before commiting!")


def run():
    commit_changeset()
