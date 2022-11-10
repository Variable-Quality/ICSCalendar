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

#Used to check if a calendar event already exists
#May want to try and use the start time of an event to narrow search
#Need to account for events that aren't in the ICS file
def search_calendar_events(service, event, len=10):
    now = dt.utcnow().isoformat()+'Z'
    events_result = service.events().list(calendarId='primary', timeMin=now, maxResults=len, singleEvents=True, orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        print("Event does not exist yet.")
        return False
    
    found = False
    eSum = event.name

    for e in events:
        start = e['summary']
        if start == eSum:
            found = True
            print('Event found!')

    return found

#Converts ICS calendar events into google calendar event objects
#Need to implement still
def convert_calendar_event(service, calendar=None, event=None):
    now = dt.now()
    if not event:
        ret = []
        for ev in calendar.events:
            eventDateStart = get_ics_date(ev, raw=True).isoformat()+'Z'
            eventDateEnd = get_ics_date(ev, raw=True, end=True).isoformat()+'Z'
            gcalEvent = {
                'summary': ev.name,
                'location': ev.location,
                'description': ev.description,
                'start': {
                    'dateTime': eventDateStart,
                    'timeZone': 'America/New_York',
                },
                'end': {
                    'dateTime': eventDateEnd,
                    'timeZone': 'America/New_York'
                }
            }
            ret.append(gcalEvent)

        return ret
    else:
        eventDateStart = get_ics_date(event).isoformat()+'Z'
        eventDateEnd = get_ics_date(event).isoformat()+'Z'

        gcalEvent = {
            'summary': event.name,
            'location': event.location,
            'description': event.description,
            'start': {
                'dateTime': eventDateStart,
                'timeZone': 'America/New_York',
            },
            'end': {
                'dateTime': eventDateEnd,
                'timeZone': 'America/New_York'
            }
        }

        return gcalEvent

#Returns the ICS date object of a given ICS event
#May wanna update later to make it work with google calendar too
def get_ics_date(event, raw=False, end=False):
    if not end:
        t = str(event.begin)
    else:
        t = str(event.end)
    
    if raw:
        return t

    eSplit = re.split(r'[tT+]', t)
    dateSplit = eSplit[0].split('-')
    timeSplit = eSplit[1].split(':')

    for x in range(0,3):
        #Redefining everything in the split lists as integer
        #For use in datetime
        dateSplit[x] = int(dateSplit[x])
        timeSplit[x] = int(timeSplit[x])

    #Pulls date and time into one datetime instance
    eventDate = dt(dateSplit[0], dateSplit[1], dateSplit[2], timeSplit[0], timeSplit[1], timeSplit[2])

    return eventDate

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
            
            eventDate = get_ics_date(event)

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
        upcoming = self.organize_events(ret_new=True)
        for event in upcoming:
            if not search_calendar_events(service, event, len(upcoming)):
                gcalEvent = convert_calendar_event(service, event=event)
                service.events().insert(calendarId='primary', body=gcalEvent).execute()
                print(gcalEvent)
                print("Added Event to calendar!")

        print("Done!")




    #Old code saved for reference

    #event_result = service.events().insert(calendarId='primary',
    #body = {
    #    "summary": "Test event",
    #    "description": "Fortnite balls, im gay",
    #    "start": {"dateTime": start, "timeZone": "America/New_York"},
    #    "end": {"dateTime": end, "timeZone": "America/New_York"},
    #}
    #).execute()

    #print("Created New Event: \n")
    #print("id: ", event_result['id'])
    #print("summary: ", event_result['summary'])
    #print("description: ", event_result['description'])
    #print('Start: ', event_result['start']['dateTime'])
    #print('End: ', event_result['end']['dateTime'])

    #############################################################################
    
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

