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
#Combine all into one class
#Event prioritization
#Sort based on time AND date (currently just works off date)
#Have URL loaded from config file rather than programmed in
#Be able to regenerate config.ini if it gets fucked up
url = 'https://kennesaw.view.usg.edu/d2l/le/calendar/feed/user/feed.ics?token=agcqgnm6m80dlbe9b4b23'
WORKING_DIR = getcwd()
Configur = ConfigParser()

class CalendarManager:

    def __init__(self):
        try:
            Configur.read('bin/config.ini')
        except FileNotFoundError:
            print("Configuration file not found! Recreating...\nYou will have to add your ICS URL to /bin/config.ini!")
            self.regen_cfg()
        
        if "settings" not in Configur.sections() or "http" not in Configur.get("settings", "URL"):
            print(Configur.sections())
            print(("settings" not in Configur.sections()))
            print(("http" not in Configur.get("settings", "URL")))
            self.regen_cfg()
            
        self.url = Configur.get('settings', 'URL')
        self.calendar = Calendar(requests.get(self.url).text)
        self.today = date.today()

    #Recreates CFG to its base form
    def regen_cfg(self):
        cfg = open('bin/config.ini', 'w')
        cfg.write("[settings]\nURL = ")
        cfg.close()
        raise Exception("Please define your URL within config.ini")

    #Re-checks the date
    def update_date(self):
        self.today = date.today()

    #Creates two lists for events in the past and events in the future
    #Returns a tuple with both lists
    #TODO: Use time to further differentiate
    def organize_events(self):
        old, new = [],[]
        for event in self.calendar.events:

            eSplit = re.split(r'[tT+]', str(event.begin))
            dateSplit = eSplit[0].split('-')
            #Reformatting date to YYYY/MM/DD format for comparison
            eventDate = date(int(dateSplit[0]),int(dateSplit[1]),int(dateSplit[2]))

            if eventDate > self.today:
                new.append(event)
            elif eventDate < self.today:
                old.append(event)
            elif eventDate == self.today:
                timeSplit = eSplit[1].split(":")
                now = dt.now().time()
                eTime = time(int(timeSplit[0]), int(timeSplit[1]), int(timeSplit[2]))
                if now < eTime:
                    new.append(event)
                else:
                    old.append(event)
            else:
                print("What")
                pass                
        
        return (old, new)


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

