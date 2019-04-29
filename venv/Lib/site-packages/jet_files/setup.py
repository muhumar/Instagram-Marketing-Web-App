import os
from jet_files import helper_functions as hf
import getpass
import requests

#DOMAIN = 'http://0.0.0.0:8000/'
DOMAIN = 'http://www.jetvc.co.uk/'


def setup():
    if not hf.already_initialized():
        print ("Please init a jet repo before calling other commands")
        return

    # Status code of a failure, to allow the while loop to go
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
    print ("Congrats you are logged in. These details will be saved")
    # Store the username in the local directory.
    filename = os.path.join(hf.get_jet_directory()
                            + '/.jet/username')
    # Also store the user id, which is also the API key for calls
    # Not storing password, for security reasons
    with open(filename, 'w') as file_:
        file_.write(username + '\n')
        file_.write(response.headers['user_id'])
    # Inform user how to change the setup
    print ("Re-run setup to change user")

    # Set to variable for easy access
    user_id = response.headers['user_id']

    # Same as above, initialize to the error code.
    status_code = 400
    first_time = True
    # Loop until it works...
    while not status_code == 200:
        # If they're here and it's not their first time, made an error! 
        if not first_time:
            print (hf.BColors.RED +
                   "Repository name not found - please try again!" +
                   hf.BColors.ENDC)
        # Instructions
        print ("Please type the name of the online repo you wish"
               " to link this with.")
        # Get the name from hte users input they're trying to sync
        repo_name = raw_input("Name (case-sensitive): ")
        try:
            # URL to verify the repo
            url = "%sverify_repo/" % DOMAIN
            # Preparing the POST
            data = {
                'repo_name': repo_name,
                'user_id': user_id,
            }
            # Code to do the POST
            response = requests.post(url, data=data)
            # Not their first time anymore...
            first_time = False
            status_code = response.status_code
        except Exception as e:
            # Something went wrong connecting to Jets servers.
            print ("Failed to connect to Jets servers.")
            print ("Error - %s" % e)
            return
    # All done, tell user! 
    print ("All setup.")
    print ("These details will be saved")
    # Save the repo's id for future use
    filename = os.path.join(hf.get_jet_directory()
                            + '/.jet/repo_id')
    with open(filename, 'w') as file_:
        file_.write(response.headers['repo_id'])


def run():
    setup()
