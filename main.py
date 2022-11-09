from ics import Calendar
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from configparser import ConfigParser
from datetime import datetime as dt
from datetime import timedelta
from datetime import date
from datetime import time as t
import pickle
import time
from os.path import exists
from os import getcwd
from plyer import notification
import requests
import re
#TODO:
#Event prioritization
#Desktop/Email notification
#GUI for easier management
#Dont forget about the fucking samsung calendar sync

WORKING_DIR = getcwd()
Configur = ConfigParser()

class CalendarManager:

    def __init__(self):
        try:
            Configur.read('bin/config.ini')
        except FileNotFoundError:
            print("Configuration file not found! Recreating...\nYou will have to add your ICS URL to /bin/config.ini!")
            self.regen_cfg()
        #Basic check to see if config.ini was broken somehow, or if the url is invalid
        if "settings" not in Configur.sections() or "http" not in Configur.get("settings", "URL"):
            self.regen_cfg()
            
        self.url = Configur.get('settings', 'URL')
        self.calendar = Calendar(requests.get(self.url).text)

    #Recreates CFG to its base form
    def regen_cfg(self):
        cfg = open('bin/config.ini', 'w')
        cfg.write("[settings]\nURL = ")
        cfg.close()
        raise Exception("Please define your URL within config.ini")

    #Creates two lists for events in the past and events in the future
    #Returns a tuple with both lists
    def organize_events(self, ret_old = False, ret_new = False):
        old, new = [],[]
        for event in self.calendar.events:
            #Splitting the event.begin text into usable shit
            eSplit = re.split(r'[tT+]', str(event.begin))
            dateSplit = eSplit[0].split('-')
            timeSplit = eSplit[1].split(':')

            for x in range(0,3):
                #Redefining everything in the split lists as integer
                #For use in datetime
                dateSplit[x] = int(dateSplit[x])
                timeSplit[x] = int(timeSplit[x])

            #Pulls date and time into one datetime instance
            eventDate = dt(dateSplit[0], dateSplit[1], dateSplit[2], timeSplit[0], timeSplit[1], timeSplit[2])

            if eventDate >= dt.today():
                new.append(event)
            elif eventDate < dt.today():
                old.append(event)
            else:
                print("What")
                #Should never get here lol
                pass                

        #Makes it so you can just return one of the lists
        #May wanna make it so it only processes one of these in the future? idk
        if ret_old and not ret_new:
            return sorted(old)
        elif ret_new and not ret_old:
            return sorted(new)
        else:
            return (sorted(old), sorted(new))

    #Constitutes the main loop for the program
    def run(self):
        #TODO: Implement a tkinter notification window
        return

    def get_calendar_service(self):
        #This links up to the google calendar service
        #Need to test what happens when multiple users are added
        #Although god only knows if imma ever get there
        SCOPES = ['https://www.googleapis.com/auth/calendar']
        CREDENTIALS_FILE = 'bin/client_secret.json'

        creds = None
        #Checks to see if the token already exists
        if exists("token.pickle"):
            with open('token.pickle','rb') as token:
                creds = pickle.load(token)

        #If it doesn't, we make it or refresh it
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
                creds = flow.run_local_server(port=0)
        #i have come for your pickle
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        service = build('calendar', 'v3', credentials=creds)
        return service

    #Does whatever I need it to
    def debug(self):
        service = self.get_calendar_service()
        d = dt.now().date()
        tomorrow = dt(d.year, d.month, d.day, 10)+timedelta(days=1)
        start = tomorrow.isoformat()
        end = (tomorrow+timedelta(hours=1)).isoformat()

        event_result = service.events().insert(calendarId='primary',
        body = {
            "summary": "Test event",
            "description": "Fortnite balls, im gay",
            "start": {"dateTime": start, "timeZone": "America/New_York"},
            "end": {"dateTime": end, "timeZone": "America/New_York"},
        }
        ).execute()

        print("Created New Event: \n")
        print("id: ", event_result['id'])
        print("summary: ", event_result['summary'])
        print("description: ", event_result['description'])
        print('Start: ', event_result['start']['dateTime'])
        print('End: ', event_result['end']['dateTime'])


    #Old code saved for reference
    #    service = self.get_calendar_service()
    #    cal_res = service.calendarList().list().execute()
    #
    #    cals = cal_res.get('items', [])
    #
    #    if not cals:
    #        print('No calendars found. The fuck?')
    #    else:
    #        for cal in cals:
    #            summary = cal['summary']
    #            id= cal['id']
    #            primary = "Primary" if cal.get('primary') else ""
    #            print("%s\t%s\t%s" % (summary, id, primary))

if __name__ == "__main__":

    c = CalendarManager()
    c.debug()

