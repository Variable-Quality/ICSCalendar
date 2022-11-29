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
def search_calendar_events(service, event, len=10, date=None):
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
        if start == eSum and not date:
            found = True
            print('Event found!')
        #Untested
        elif start == eSum and date:
            if e['start'] == date.isoformat()+'Z':
                found = True
                print('Date matches!')

    return found

#Converts ICS calendar events into google calendar event objects
#Or vice versa, depending on if goog is true
def convert_calendar_event(service, calendar=None, event=None, goog=False):
    now = dt.now()
    if not event and not goog:
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
    elif event and not goog:
        eventDateStart = get_ics_date(event).isoformat()+'Z'
        eventDateEnd = get_ics_date(event, end = True).isoformat()+'Z'

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
    
    #If the event being passed in is a google calendar event
    #Convert it to an ICS calendar event
    #This is mostly used for comparisons
    #May implement the ability to put in a list of events later
    if goog:
        googDatetime = event['start'].get('dateTime')
        sp = re.split(r'[tT-]', googDatetime)
        #Date is sp[0], sp[1], sp[2], start time is sp[3], end time is sp[4]
        #At least for single day events, multi day events are another story
        print(sp)
        startSplit = sp[3].split(':')
        endSplit = sp[4].split(':')
        return (dt(int(sp[0]),int(sp[1]),int(sp[2]),
                    int(startSplit[0]),int(startSplit[1]),int(startSplit[2])),
                   #End split is only 2 items long for whatever reason 
                dt(int(sp[0]),int(sp[1]),int(sp[2]),
                    int(endSplit[0]),int(endSplit[1]),00))


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

#Compares dates between an ical event and a google calendar event
#Returns a tuple of booleans
#First bool is if the start date is the same, second bool is if the end date is the same
#May remake in the future to be more versatile but atm doesnt need to be
def compare_dates(service, event, gcalEvent):
    startSame = False
    endSame = False

    icalStart = get_ics_date(event).isoformat()+'Z'
    icalEnd = get_ics_date(event, end= True).isoformat()+'Z'

    
    gcalStart, gcalEnd = convert_calendar_event(service, event=gcalEvent, goog=True)
    print("\nGoogle Calendar Values:\n")
    print(gcalStart.isoformat()+'Z')
    print(gcalEnd.isoformat()+'Z')
    print("\niCal values:\n")
    print(icalStart)
    print(icalEnd)

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
    def organize_ical_events(self, ret_old = False, ret_new = False):
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

    #Does the same as organize_ical_events but for google events
    #Luckily google does a bit more legwork when it comes to sorting these 
    def get_google_events(self, num_events=10, now=dt.now().isoformat()+'Z'):
        service = self.get_calendar_service()

        events_result = service.events().list(calendarId='primary', timeMin=now,
                                             maxResults=num_events, singleEvents=True,
                                             orderBy='startTime').execute()
        
        events = events_result.get('items', [])

        if not events:
            print("No upcoming events found")
            return None

        return events

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
        icalUpcoming = self.organize_ical_events(ret_new = True)
        googleUpcoming = self.get_google_events()
        service = self.get_calendar_service()
        
        compare_dates(service, icalUpcoming[0], googleUpcoming[0])

        #for e in icalUpcoming:

            #for event in googleUpcoming:
                
                #compare_dates(service, e, event)
            
            #print("\nical event exhausted, moving on...\n")


    #Will eventually become the main loop of the program
    #Still needs some backbone to it
    def run(self):
        service = self.get_calendar_service()
        upcoming = self.organize_ical_events(ret_new=True)
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

