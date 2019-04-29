import os
import shutil
import helper_functions as hf


# This operation takes a copy of the current codebase and stores it.
def stash():
    # Getting jet directory and stash path to avoid re-fetching later
    jet_directory = hf.get_jet_directory()
    stash_path = os.path.join(jet_directory + '/.jet/stash/')
    # If there is a stash being currently stored.
    if os.path.exists(stash_path):
        # Ask if they're ok overwriting it
        response = raw_input("Are you sure you wish to overwrite your"
                             " previous stash? (yes/no) ")
        # Accept y as shorthand for yes
        if not response == "y" or response == "yes":
            # If they said anything else, cancel the operation.
            print ("Cancelling....")
            return
        # completely remove all trace of it 
        shutil.rmtree(stash_path)
        
    # Make the directory that will store the stash
    os.mkdir(stash_path)
    f = []  # Full filenames
    filenames_list = []  # Names of the files
    # Goes through all files in the current directory and below.
    for (dirpath, dirnames, filenames) in os.walk(jet_directory):
        for filename in filenames:
            # Checks they're not in the jet ignore file
            if hf.filter_one_file_by_ignore(filename):
                if not dirpath\
                        .startswith(os.path.join(jet_directory + '/.jet')):
                    filenames_list.append(filename)
                    f.append(os.path.join(dirpath, filename))
    
    # Counter to loop through folder names with
    count = 0
    for file_to_add in f:
        # A folder for each file, to store filename and contents separately.
        folder = os.path.join(stash_path + '/%s' % count)
        os.mkdir(folder)
        # Storing filename..
        filename = os.path.join(stash_path + '/%s/filename.txt' % count)
        with open(filename, 'w') as myFile:
                myFile.write(file_to_add)
        filename = filenames_list[count]
        # Copying the contents over, to enable diffs to work
        new_filename = os.path.join(stash_path + '/%s/%s' % (count, filename))
        shutil.copyfile(file_to_add, new_filename)
        # Increment the counter
        count += 1
    # Alert user all went well! 
    print ("Successfully stashed the code")


# This command takes the currently stashed code and restores it. 
def unstash():
    jet_directory = hf.get_jet_directory()
    if not hf.already_initialized():
        print ("Please init a jet repo before calling other commands")
        return
    # Ensures there is actually some content stashed... 
    stash_path = os.path.join(jet_directory + '/.jet/stash/')
    if not os.path.exists(stash_path):
        print ("Cannot unstash as there is no stashed content")
        return
    # Double check they wish to do this, as it's irreversible 
    print ("Are you sure you wish to restore the code that is stashed?"
           " Any un-committed changes will be lost.")
    # Get response from user
    response = raw_input("This action is irreversible. (yes/no) ")
    # Allow y as well as yes
    if not response == "y" or response == "yes":
        print ("Cancelling...")
        return

    # Get the current files in the repo
    current_files = hf.get_current_files(None)
    # Get the stored files folders in the stash
    files = os.listdir(stash_path)
    for _file in files:
        # Get the actual filename
        stored_filename_filename = os.path.join(stash_path
                                                + '/%s/filename.txt' % _file)
        # Read the file
        with open(stored_filename_filename, 'r') as myFile:
            filename = myFile.read()
        try:
            # Check to see if the file is new by trying to remove
            current_files.remove(filename)
            new = False
        except ValueError:
            # New if error removing
            new = True
        try:
            # Attempt to hash the files contents
            current_hash = hf.checksum_md5(filename)
        except IOError:
            # Give fake value if there's a problem
            current_hash = "Not a file"
        # Get the actual filename (no path)
        head, name = os.path.split(filename)
        stored_contents_filename = os.path.join(stash_path +
                                                '/%s/%s' % (_file, name))
        # Get the contents from the stored version
        with open(stored_contents_filename, 'r') as myFile:
            stored_contents = myFile.read()
        # Hash the stored version
        stored_contents_hash = hf.checksum_md5(stored_contents_filename)
        if current_hash == stored_contents_hash:
            # File is unchanged
            continue
        # File is either new or edited
        if new:
            # Make the directories to place the file in
            hf.make_directories(filename, clone=False)
        # Alert user the files being changed
        print ("Updating %s" % hf.relative(filename, os.getcwd()))
        # Change the file
        with open(filename, 'w') as new_file:
            new_file.write(stored_contents)

    # If the file needs deleting, delete it 
    for file_to_delete in current_files:
        os.remove(file_to_delete)

    # Alert user it all worked! 
    print ("Loaded in the code from the stash")


def run():
    if not hf.already_initialized():
        print ("Please init a jet repo before calling other commands")
        return

    stash()
