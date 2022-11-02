from ics import Calendar
from configparser import ConfigParser
from datetime import datetime as dt
from datetime import date
from datetime import time
from os.path import exists
from os import getcwd
import requests
import re
#TODO:
#Event prioritization
#Desktop/Email notification
#GUI for easier management

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
        self.today = dt.today()

    #Recreates CFG to its base form
    def regen_cfg(self):
        cfg = open('bin/config.ini', 'w')
        cfg.write("[settings]\nURL = ")
        cfg.close()
        raise Exception("Please define your URL within config.ini")

    #Re-checks the date
    def update_date(self):
        self.today = dt.today()

    #Creates two lists for events in the past and events in the future
    #Returns a tuple with both lists
    #TODO: Use time to further differentiate
    def organize_events(self):
        old, new = [],[]
        self.update_date()
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

            if eventDate >= self.today:
                new.append(event)
            elif eventDate < self.today:
                old.append(event)
            else:
                print("What")
                #Should never get here lol
                pass                
        
        return (sorted(old), sorted(new))


if __name__ == "__main__":

    c = CalendarManager()
    old, new = c.organize_events()

    for x in old:
        print("Event {} started {}".format(x.name, x.begin.humanize()))
    
    print("\n==================================================\n")

    for x in new:
        print("Event {} starts {}".format(x.name, x.begin.humanize()))


#for x in events:
#    print("Event {} started {}".format(x.name, x.begin))

