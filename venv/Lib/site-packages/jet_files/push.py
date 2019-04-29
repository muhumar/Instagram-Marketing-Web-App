import os
import sys
from jet_files import helper_functions as hf
import requests
import json

# Switch these over by un-commenting and commenting when testing on dev server.

#DOMAIN = 'http://0.0.0.0:8000/'
DOMAIN = 'http://www.jetvc.co.uk/'


# This command takes the 
def push():
    if not hf.already_initialized():
        print ("Please init a jet repo before calling other commands")
        return
    # Gets the jet directory and branch to avoid re-fetching.
    jet_directory = hf.get_jet_directory()
    branch = hf.get_branch()
    # Make sure the user is logged in and synced with the jet servers
    if not hf.is_setup():
        print ("You must setup before pushing! To do this type:"
               " $jet setup")
        return
    # Gets the hook associated with pushing
    hook = hf.get_push_hook()
    # If hook is None, means there is no hook attached.
    if hook:
        # Run the hook
        result = hf.run_hook(hook)
        # Will only give true if passed
        if result:
            print ("Hook passed.")
        else:
            print ("Hook Failed. Not pushing")
            return
    # Gets the branch name and the commit number from
    # the last time a push or pull happened.
    branch, last_update = hf.get_last_update(branch)
    # Gets the current commit number
    current_commit = hf.get_commit()
    # If they're the same, don't bother pushing.
    if int(last_update) == int(current_commit):
        print ("No changes to push")
        return
    # Connect to jets servers 
    print ("Connecting....")
    # Url containing list of current files
    url = "%scurrent_file_list/%s/%s/" % (DOMAIN,
                                          hf.get_repo_id(),
                                          branch)
    # Gets response from the server
    try:
        response = requests.get(url)
        content = json.loads(response.content)
    except Exception as e:
        print ("Failed to connect to Jets servers.")
        print ("Error - %s" % e)
        return
    # Gets the current files in the repo
    current_files = hf.get_file_list_at(branch, hf.get_commit())
    # Send commit POST
    print ("Creating commit on server...")
    url = "%screate_commit/" % DOMAIN
    # If there's a message been passed in, use it!
    try:
        if sys.argv[2] == "-m" and len(sys.argv) == 4:
            message = sys.argv[3]
        else:
            # Otherwise, use a default.
            message = "Pushed from local servers"
    except IndexError:
        message = "Pushed from local servers"
    # Prepare the POST request
    data = {
        'message': message,
        'user_id': hf.get_user_id(),
        'branch_name': branch,
        'repo_id': hf.get_repo_id(),
    }
    # Do the request
    response = requests.post(url, data=data)
    # Get the commit id from the servers response headers
    commit_id = response.headers['commit_id']
    # Loop through the files
    for _file in content['files']:
        # Store full filename
        filename = jet_directory + '/' + _file['filename']
        try:
            # Remove from list 
            current_files.remove(filename)
        except ValueError:
            # Move onto next one
            continue
        try:
            # Get the hash of the file
            current_hash = hf.checksum_md5(filename)
        except IOError:
            current_hash = "Not a file"
        # Compare hashes to see if anything needs doing
        if current_hash == _file['hash']:
            # File is unchanged, move onto next file
            continue
        # Read the contents of the file in 
        with open(filename, 'r') as myFile:
            contents = myFile.read()
        print ("Uploading file %s..." % filename)
        # Strip filename to make it relative
        stripped_filename = filename[len(jet_directory):]
        # Remove slash if it exists
        if stripped_filename.startswith('/'):
            stripped_filename = stripped_filename[1:]
        # URL to POST new files contents to
        url = "%supdate_file/" % DOMAIN
        # Prepare the POST data
        data = {
            'filename': stripped_filename,
            'api_key': hf.get_user_id(),
            'branch_name': branch,
            'repo_id': hf.get_repo_id(),
            'contents': contents,
            'commit_id': commit_id,
        }
        # Do the POST
        requests.post(url, data=data)

    # Loop through brand new files which need uploading
    for new_file in current_files:
        filename = new_file
        # Read contents of the file
        with open(filename, 'r') as myFile:
            contents = myFile.read()
        # Upload the file
        print ("Uploading file %s..." % hf.relative(filename, os.getcwd()))
        # Turn to relative filename
        stripped_filename = filename[len(jet_directory):]
        # Remove slash if it's there
        if stripped_filename.startswith('/'):
            stripped_filename = stripped_filename[1:]
        # The url to make the POST to
        url = "%supdate_file/" % DOMAIN
        # Prepare the POST data
        data = {
            'filename': stripped_filename,
            'branch_name': branch,
            'api_key': hf.get_user_id(),
            'repo_id': hf.get_repo_id(),
            'contents': contents,
            'commit_id': commit_id,
        }
        # do the POST
        requests.post(url, data=data)

    # Store the fact this content has been pushed
    hf.add_update(branch, hf.get_commit())
    # Don't want to be able to pull our own content..
    # Get last pull
    last_server_pull = hf.get_last_server_pull(branch)
    # Assume it's one higher, so save it as one more
    hf.save_last_pull(branch, last_server_pull + 1)
    # Alert user it's complete.
    print (hf.BColors.GREEN + "Pushed" + hf.BColors.ENDC)


def run():
    push()
