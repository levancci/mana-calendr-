import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

def create_service(client_secret_file, api_name, api_version, scopes, prefix=''):
    cred = None
    working_dir = os.getcwd()
    token_dir = 'token files'
    token_file = f'token_{api_name}_{api_version}{prefix}.pickle'

    # Check if token dir exists
    if not os.path.exists(os.path.join(working_dir, token_dir)):
        os.mkdir(os.path.join(working_dir, token_dir))

    pickle_file = os.path.join(working_dir, token_dir, token_file)

    # Check if token exists and is valid
    if os.path.exists(pickle_file):
        with open(pickle_file, 'rb') as token:
            cred = pickle.load(token)

    if not cred or not cred.valid:
        if cred and cred.expired and cred.refresh_token:
            cred.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(client_secret_file, scopes)
            cred = flow.run_local_server(port=0)

        with open(pickle_file, 'wb') as token:
            pickle.dump(cred, token)

    try:
        service = build(api_name, api_version, credentials=cred)
        print(api_name, 'service created successfully')
        return service
    except Exception as e:
        print('Unable to connect.')
        print(e)
        return None