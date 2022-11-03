from ics import Calendar
from configparser import ConfigParser
from datetime import datetime as dt
from datetime import date
from datetime import time as t
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
        #TODO: Figure out a better way to loop this
        while(True):
            new = self.organize_events(ret_new=True)
            print("Sending notification!")
            notification.notify(
                title = "Daily notification on {}".format(date.today()),
                message = "Your three upcoming assignments are as follows:\n{} due {}\n{} due {}\n{} due {}".format(new[0].name, new[0].begin.humanize(),
                                                                                                                    new[1].name, new[1].begin.humanize(),
                                                                                                                    new[2].name, new[2].begin.humanize()),
                timeout = 45
            )
            print("Sleeping...")
            time.sleep(120)


if __name__ == "__main__":

    c = CalendarManager()
    c.run()


#for x in events:
#    print("Event {} started {}".format(x.name, x.begin))

