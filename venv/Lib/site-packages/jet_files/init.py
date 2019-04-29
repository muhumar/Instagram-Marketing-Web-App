from shutil import copyfile
from jet_files import helper_functions as hf
import os
from os import walk


def init():
    # Can't initialize in a folder already controlled by Jet.
    if hf.already_initialized():
        print ("Already a repo initialized")
    else:
        # This is the directory all Jets information will be stored under
        os.mkdir('.jet')
        f = []  # Full filenames
        filenames_list = []  # Names of the files
        # Goes through all files in the current directory and below.
        for (dirpath, dirnames, filenames) in walk(os.getcwd()):
            for filename in filenames:
                # Checks they're not in the jet ignore file
                if hf.filter_one_file_by_ignore(filename):
                    filenames_list.append(filename)
                    f.append(os.path.join(dirpath, filename))
        # Store a copy of the files being source controlled
        with open('.jet/latest_saved_files', 'w') as file_:
            for file_to_add in f:
                # Storing full filename
                file_.write(file_to_add + "\n")
                # Storing hash of the file contents
                file_.write(hf.checksum_md5(file_to_add) + "\n")
        # Making an initial commit 
        os.mkdir('.jet/0/')
        # Storing the files being saved in the commit
        with open('.jet/0/file_log.txt', 'w') as file_:
            for file_to_add in f:
                file_.write(file_to_add + "\n")

        # Going through each file storing their initial contents
        count = 0
        for file_to_add in f:
            # A folder for each file, to store filename
            # and contents separately.
            folder = os.path.join(hf.get_jet_directory() +
                                  '/.jet/%s/%s' % (0, count))
            os.mkdir(folder)
            # Storing filename..
            filename = os.path.join(hf.get_jet_directory() +
                                    '/.jet/%s/%s/filename.txt'
                                    % (0, count))
            with open(filename, 'w') as myFile:
                    myFile.write(file_to_add)
            filename = filenames_list[count]
            # Copying the contents over, to enable diffs to work
            copyfile(file_to_add, '.jet/0/%s/%s' % (count, filename))
            count += 1
            
        # Storing the current branch that's being worked on
        filename = '.jet/branch'
        with open(filename, 'w') as file_:
            file_.write("master")
        # Sets the current commit to 0
        filename = '.jet/current_commit'
        with open(filename, 'w') as file_:
            file_.write("0")
        # Init is all done, inform user with nice green text.
        print ((hf.BColors.GREEN + "Initializing Jet repository in %s"
               % os.getcwd() + hf.BColors.ENDC))


def run():
    init()
