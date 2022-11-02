from ics import Calendar
from datetime import datetime as dt
from datetime import date
import requests
import re
#TODO:
#Combine all into one class
#Event prioritization
#Sort based on time AND date (currently just works off date)
url = 'https://kennesaw.view.usg.edu/d2l/le/calendar/feed/user/feed.ics?token=agcqgnm6m80dlbe9b4b23'

c = Calendar(requests.get(url).text)

events = list(c.timeline)
today = date.today()

old, new = [],[]
for event in events:

    eSplit = re.split(r'[tT+]', str(event.begin))
    dateSplit = eSplit[0].split('-')
    #Reformatting date to YYYY/MM/DD format for comparison
    eventDate = date(int(dateSplit[0]),int(dateSplit[1]),int(dateSplit[2]))

    if eventDate >= today:
        new.append(event)
    elif eventDate < today:
        old.append(event)
    else:
        print("What")

for x in old:
    print("Event {} started {}".format(x.name, x.begin.humanize()))

print("\n=====================================\n")

for x in new:
    print("Event {} starts {}".format(x.name, x.begin.humanize()))


#for x in events:
#    print("Event {} started {}".format(x.name, x.begin))

