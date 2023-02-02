from __future__ import print_function
import os.path
import os

# Google API import
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Server Imports
from flask import Flask, request, jsonify
from flask_cors import CORS


# Setup Server
app = Flask(__name__)
CORS(app)

# Google credentials | MUST HAVE IN ENVIRONMENT
client_id = os.environ.get("CLIENT_ID")
client_secret = os.environ.get("CLIENT_SECRET")

refresh_token = os.environ.get("REFRESH_TOKEN")
token = os.environ.get("TOKEN")
expiry = os.environ.get("EXPIRY")

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/classroom.courses.readonly']


def auth_user2():
    global client_secret
    global refresh_token
    global client_id
    global expiry
    global token
    creds = None

    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("refreshing token")
            creds.refresh(Request())
        else:
            print("creating new token")
            creds = Credentials.from_authorized_user_info(
                info={
                    'client_id':client_id,
                    'client_secret':client_secret,
                    'refresh_token':refresh_token,
                    'token':token
                },
                scopes=SCOPES
            )
        
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    return creds



@app.route("/", methods=["GET"])
def get_classes():
    creds = auth_user2()

    try:
        service = build('classroom', 'v1', credentials=creds)

        # Call the Classroom API
        results = service.courses().list(pageSize=10).execute()
        courses = results.get('courses', [])

        if not courses:
            print('No courses found.')
            return
        # Prints the names of the first 10 courses.
        print('Courses:')
        for course in courses:
            print(course['name'])

    except HttpError as error:
        print('An error occurred: %s' % error)
        
    return courses




if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False, port=8080)