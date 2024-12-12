# Import a speaker from the submission form
#
# Based on the quickstart template: https://developers.google.com/sheets/api/quickstart/python
#
#
#
# Logic:
#  - if the speaker submission is valid, not spam, and not already accepted
#   - extract important data into a yaml format
#   - download the avatar to file
#
#
# use in combination with the Makefile

import os.path
import pickle
import shutil
import sys
from pathlib import Path

import requests
import yaml
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying these scopes, delete the file token.pickle.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = "1_R7iXWXwoVFyiDMlivfa9oq7n2earV8AviQVyrjifbs"
SAMPLE_RANGE_NAME = "Form Responses 1!A1:M"


def main():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        #if creds and creds.expired and creds.refresh_token:
        #    creds.refresh(Request())
        #else:
        flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
        creds = flow.run_local_server()
        # Save the credentials for the next run
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)

    service = build("sheets", "v4", credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    result = (
        sheet.values()
        .get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=SAMPLE_RANGE_NAME)
        .execute()
    )
    values = result.get("values", [])

    header = values.pop(0)

    speakers = []
    if not values:
        print("No data found.")
    else:
        for r in values:
            row = dict(zip(header, r))
            if row["Agreement"] != "Agree":
                continue
            if "Action" in row.keys() and row["Action"] == "Spam":
                continue
            data = {
                "name": row["Name"],
                "social": row["Social Media link"],
                "video_link": row["Video Recording link"],
                "conf": row["Original Conference name"],
                "conf_link": row["Original Conference link"],
                "title": row["Talk title"],
            }
            data["id"] = "".join(x.lower() for x in data['name'] if x.isalnum())

            avurl = row["Profile picture link"]
            avatar = f"{data['id']}.png"
            data["avatar"] = avatar
            resp = requests.get(avurl, stream=True)
            with open(Path.cwd() / "img" / "avatar" / avatar, "wb") as out:
                shutil.copyfileobj(resp.raw, out)
            del resp

            speakers.append(data)

    print(yaml.dump(speakers))

    if sys.argv[1]:
        save_file = sys.argv[1]
        if Path(save_file).exists:
            with open(sys.argv[1], 'w') as f:
                f.write(yaml.dump(speakers))
            print(f"Result written to {save_file}")
        else:
            print(f"Error: {save_file} not valid")


if __name__ == "__main__":
    main()
