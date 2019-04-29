import getpass
import json
import os
import sys
from jet_files import helper_functions as hf
from jet_files import init, commit_changeset, add
import requests

# Uncomment the domain that's being used. Jetvc for live and localhost for dev.
#DOMAIN = 'http://0.0.0.0:8000/'
DOMAIN = 'http://www.jetvc.co.uk/'


# This command overwrites all current content with what's stored on the server. 
def force_pull():
    # Getting branch and jet directory at the start to avoid code duplication
    branch = hf.get_branch()
    jet_directory = hf.get_jet_directory()
    # Jetvc's url of the current file list.
    url = "%scurrent_file_list/%s/%s/" % (DOMAIN,
                                          hf.get_repo_id(),
                                          branch)
    # Code to get the response from the server 
    response = requests.get(url)
    content = json.loads(response.content)
    # Get the current files of the repo
    current_files = hf.get_current_files(None)
    # Loop through the files from the server
    for _file in content['files']:
        # Get the actual filename of the file
        filename = jet_directory + '/' + _file['filename']
        try:
            # Try to remove the file
            current_files.remove(filename)
            new = False
        except ValueError:
            # If couldn't be removed, means it wasn't there - new file! 
            new = True
        try:
            # Get the hash of the current file.
            current_hash = hf.checksum_md5(filename)
        except IOError:
            # Set a default if didn't work.
            current_hash = "Not a file"
        if current_hash == _file['hash']:
            # File is unchanged
            continue
        # File is either new or edited
        print ("Updating file %s..." % hf.relative(filename, os.getcwd()))
        # REST API to get new 
        url = "%sapi/v1/file/%s/?api_key=%s" % (DOMAIN,
                                                _file['file_id'],
                                                hf.get_user_id())
        # Code to get response from server                                        
        response = requests.get(url)
        content = json.loads(response.content)
        # Gets the new contents of the file
        new_contents = content['contents']
        # If new, directories have to be made to store the file
        if new:
            hf.make_directories(filename, clone=False)
        with open(filename, 'w') as new_file:
            # Write the new contents
            new_file.write(new_contents)

    for file_to_delete in current_files:
        # And files that weren't from the server should be deleted. 
        os.remove(file_to_delete)


# This function takes a copy of the repo and puts it into the current directory
# It also initializes a jet repo in the directory.
def clone():
    if hf.already_initialized():
        # Doesn't work if there is already a jet repo there.
        print("Already a repo here, can't clone into this directory.")
        return
    # Ensure the command is formed correctly. 
    if not len(sys.argv) == 4:
        print("Please form clone commands '$jet clone <repo_id>"
              " <branch_name>'")
        return
    # Get the branch and repo id from the input.
    branch = sys.argv[3]
    repo_id = sys.argv[2]
    directory = os.getcwd()
    # Ensure the directory is empty to prevent filename clashes. 
    if not os.listdir(directory) == []:
        print ("Can only clone into an empty directory, sorry.")
        return
    status_code = 403
    first_time = True
    print ("Connecting....")
    # Initialize variables
    username = None
    response = None
    # Loop until success.
    while not status_code == 200:
        # If it's not their first time, they made an error logging in
        if not first_time:
            print (hf.BColors.RED +
                   "Incorrect details - please try again!" +
                   hf.BColors.ENDC)
        # print (the instructions
        print ("Please type your Jet username used in registration"
               " at www.jetvc.co.uk. If you're not already "
               "registered please visit www.jetvc.co.uk/register/")
        # Get the users input for their username
        username = raw_input("Username: ")
        # Using a library to get the password to avoid complications
        password = getpass.getpass()

        # URL for logging a user in
        url = "%slogin_user/" % DOMAIN
        try:
            # Preparing the POST data
            data = {
                'username': username,
                'password': password,
            }
            # Code to send the POST
            response = requests.post(url, data=data)
            # Not the first time anymore, so set to False
            first_time = False
            # Set status code, ready for looping
            status_code = response.status_code
        except Exception as e:
            # Jets servers are down, error..
            print ("Failed to connect to Jets servers.")
            print ("Error - %s" % e)
            return
    # Will only go here if a 200, if so, then login details were correct!

    # Set to variable for easy access
    user_id = response.headers['user_id']

    # Gets the list of current files in the jetvc repo
    url = "%scurrent_file_list/%s/%s/" % (DOMAIN,
                                          repo_id,
                                          branch)
    try:
        # Code to get response from server..
        response = requests.get(url)
        content = json.loads(response.content)
    except Exception as e:
        # Servers are down, print (error message
        print ("Failed to connect to Jets servers.")
        print ("Error - %s" % e)
        return
    # 200 == OK
    if not response.status_code == 200:
        print ("There was an error with the repo id or branch name "
               "- please try again!!!")
        return
    for _file in content['files']:
        filename = directory + '/' + _file['filename']
        print ("Adding file %s..." % hf.relative(filename, directory))
        # REST API to get the information about the file
        url = "%sapi/v1/file/%s/?api_key=%s" % (DOMAIN,
                                                _file['file_id'],
                                                user_id)
        # Gets response from the server
        try:
            response = requests.get(url)
            content = json.loads(response.content)
        except Exception as e:
            print ("Error getting contents - do you have permission?!?")
            print (e)
            return
        # Gets the contents of the file
        new_contents = content['contents']
        # Made the directories necessary for it to work.
        hf.make_directories(filename, clone=True)
        with open(filename, 'w') as new_file:
            # Write the new contents of the file to disk
            new_file.write(new_contents)
    # Run the code to initiate a repository.
    init.run()
    print ("Congrats you are logged in. These details will be saved")
    # Store the username in the local directory.
    filename = os.path.join(hf.get_jet_directory()
                            + '/.jet/username')
    # Also store the user id, which is also the API key for calls
    # Not storing password, for security reasons
    with open(filename, 'w') as file_:
        file_.write(username + '\n')
        file_.write(user_id)
    # Inform user how to change the setup
    print ("Run $jet setup to change user")
    # Save the repo's id for future use
    filename = os.path.join(hf.get_jet_directory()
                            + '/.jet/repo_id')
    with open(filename, 'w') as file_:
        file_.write(repo_id)
    print (hf.BColors.GREEN + "Successfully cloned the repo."
           + hf.BColors.ENDC)


def pull():
    # Getting branch and jet directory to avoid code duplication
    branch = hf.get_branch()
    jet_directory = hf.get_jet_directory()
    # Url of jetvc files list endpoint
    url = "%scurrent_file_list/%s/%s/" % (DOMAIN,
                                          hf.get_repo_id(),
                                          branch)
    # Gets a response from the server.
    response = requests.get(url)
    content = json.loads(response.content)
    # Gets the currently stored file list
    current_files = hf.get_current_files(None)
    # Formats the file names correctly for the servers files.
    server_files = [jet_directory + '/' + _file['filename']
                    for _file in content['files']]
    # Also stores a list of ids for the files in order to make REST calls
    server_ids = [_file['file_id'] for _file in content['files']]
    # Parent branch and commit number are important for merging.
    parent_branch, parent_commit_number = hf.get_last_update(branch)
    # Gets the files from the parent branch and commit number, ready to merge
    parent_files = hf.get_file_list_at(parent_branch, parent_commit_number)

    # Start the arrays off as empty. 
    files_to_merge = []
    files_to_ask_about = []

    for file_ in current_files:
        # If the file is in both the current ones and the server ones,
        #  merge it!
        if file_ in server_files:
            files_to_merge.append(file_)
        else:
            # Otherwise, ask if it should be deleted or not
            files_to_ask_about.append(file_)
    # Add all files not looped through
    files_to_ask_about += [x for x in server_files if x not in current_files]

    for f in files_to_ask_about:
        # Actually ask about the file
        answer = hf.ask(f)
        if not answer:
            # If answer is false (they don't want the file)
            os.remove(f)
        else:
            if f not in current_files:
                # Fetch it from ths server
                print ("Downloading file %s..." % hf.relative(f, os.getcwd()))
                # REST url of the files contents
                url = "%sapi/v1/file/%s/?api_key=%s" \
                      % (DOMAIN,
                         server_ids[server_files.index(f)],
                         hf.get_user_id())
                # Code to execute the request
                response = requests.get(url)
                content = json.loads(response.content)
                # Contents stored as json
                new_contents = content['contents']
                # Write the new contents to a file
                #  after making directories for it
                hf.make_directories(f, clone=False)
                with open(f, 'w') as myFile:
                    myFile.write(new_contents)
    # Now..merge the files! 
    print ("Checking for changes / merges")
    for f in files_to_merge:
        if f in parent_files:
            # Gets the parent, if there is one...
            parent_file = hf.get_file_at(parent_branch,
                                         parent_commit_number,
                                         f)
        else:
            # If there is no parent file, blank file will work.
            parent_file = []

        # Gets the local version of the file
        with open(f, 'r') as myFile:
            local_file = myFile.read().splitlines()

        # Gets the server version of the file
        # REST api endpoint with files contents
        url = "%sapi/v1/file/%s/?api_key=%s"\
              % (DOMAIN,
                 server_ids[server_files.index(f)],
                 hf.get_user_id())
        # Process the request
        response = requests.get(url)
        content = json.loads(response.content)
        new_contents = content['contents']
        server_file = new_contents.splitlines()

        # Now we have the 3 copies of the file..

        # Check that they are not equal,
        #  as if they are that would save processing.
        if not local_file == server_file:
            try:
                # Attempt to do the merge on the file.
                new_file = hf.fix_file(f, parent_file, local_file, server_file)
            except IndexError:
                # error has happened. Apply worst case scenario.
                new_file = \
                    ['@@@@@@@@@@HEAD@@@@@@@@@@\n'] \
                    + local_file \
                    + ['\n@@@@@@@@@@SEPARATOR@@@@@@@@@@\n'] \
                    + server_file \
                    + ['\n@@@@@@@@@@END@@@@@@@@@@']
                # Add a conflict to say error happened
                hf.add_conflict(f)
            # Write the new file and its contents to disk.
            with open(f, 'w') as myFile:
                for line in new_file:
                    myFile.write('%s\n' % line)


def run():
    if not hf.already_initialized():
        print ("Please init a jet repo before calling other commands")
        return
    # Only get the branch once...
    branch = hf.get_branch()
    print ("Connecting....")
    # Url to get the highest commit number - to see if there are any updates.
    url = "%shighest_commit/%s/%s/" % (DOMAIN,
                                       hf.get_repo_id(),
                                       branch)
    try:
        # Does the request to the servers
        response = requests.get(url)
        content = json.loads(response.content)
    except Exception as e:
        # First request, so check servers are up and running
        print ("Failed to connect to Jets servers.")
        print ("Error - %s" % e)
        return
    
    server_commit = content['commit_number']
    print ("Connected.")
    last_server_pull = hf.get_last_server_pull(branch)
    # If the last pull and latest commit are the same, no need to update! 
    if server_commit == last_server_pull:
        print ("You are already up to date.")
        return
    try:
        # If -f is included, they wish to do a force pull.
        if sys.argv[2] == '-f':
            force_pull()
        else:
            print ("Invalid argument.")
            return
    except IndexError:
        # Index error means no sys argv was included, so just normal pull! 
        pull()
    # Once pulled, add the new file changes to a changeset
    add.add(verbose=False)
    # Commit the new files with custom message
    commit_changeset.commit("Merged branch %s with servers changes."
                            % branch, verbose=False)
    # Store a new last pull, for update reasons
    hf.save_last_pull(branch, server_commit)
    # Alert user all was completed.
    print ("Committed merges")
    print (hf.BColors.GREEN + "Pulled" + hf.BColors.ENDC)
