import os
from jet_files import helper_functions as hf


# At the moment, all files are added to the changeset, issue raised to change
def add(verbose):
    if not hf.already_initialized():
        print("Please init a jet repo before calling other commands")
        return

    filename = os.path.join(hf.get_branch_location() + 'changeset.txt')
    current_files = hf.get_current_files(None)
    stored_files_and_hashes = hf.get_stored_files_and_hashes()
    stored_files = hf.get_stored_files(stored_files_and_hashes)
    with open(filename, 'w') as file_:
        # Adds all new files
        for file_to_add in hf.get_new_files(current_files, stored_files):
            file_.write("+" + file_to_add + "\n")
        # Adds all deleted files
        for file_to_add in hf.get_deleted_files(current_files, stored_files):
            file_.write("-" + file_to_add + "\n")
        # Adds all changed files
        for file_to_add in hf.get_changed_files(current_files,
                                                stored_files_and_hashes):
            file_.write("~" + file_to_add + "\n")

    if verbose:
        print("Added to changeset")


def run():
    add(verbose=True)
