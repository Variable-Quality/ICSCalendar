from ics import Calendar
import requests
import re

url = 'https://kennesaw.view.usg.edu/d2l/le/calendar/feed/user/feed.ics?token=agcqgnm6m80dlbe9b4b23'

c = Calendar(requests.get(url).text)

events = list(c.timeline)
testCase = events[5]

#bSplit = str(testCase.begin).split('T+')
bSplit = re.split(r'[tT+]', str(testCase.begin))

for x in bSplit:
    print(x)

#for x in events:
#    print("Event {} started {}".format(x.name, x.begin))

