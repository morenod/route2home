#!/usr/bin/python
import googlemaps
import json
from datetime import datetime
import time
import argparse
from argparse import RawTextHelpFormatter
import re
import sys
import os

__VERSION__ = "0.1"

## ARGS PARSER

parser = argparse.ArgumentParser(description="Route and travel time calculation", epilog="""

GoogleMaps API Key is required, obtain it on https://developers.google.com/console
Report bugs on https://github.com/morenod/route2home
""", formatter_class=RawTextHelpFormatter)
parser.add_argument('--origin', metavar='ORIGIN', nargs='?', type=str, help='Departure Point', required=True)
parser.add_argument('--destination', metavar='DESTINATION', nargs='?', type=str, help='Destination Point', required=True)
parser.add_argument('--alternatives', action='store_true', help='Obtain alternatives routes', default=False)
parser.add_argument('--apikey', metavar='KEY', nargs='?', type=str, help='GoogleMaps API Key', required=True)
parser.add_argument('--debug', action='store_true', help='Print all the route obtained from GoogleMaps as JSON', default=False)
parser.add_argument('--version', action='version', version=__VERSION__)
args = parser.parse_args()

## ARGS VERIFICATION

gmaps = googlemaps.Client(key=args.apikey)

try:
    if not gmaps.geocode(args.origin):
        print "%s: invalid origin: -- '%s'" %(os.path.basename(sys.argv[0]),args.origin)
        print "Try '%s' --help for more information" %(os.path.basename(sys.argv[0]))
        sys.exit(2)
    elif not gmaps.geocode(args.destination):
        print "%s: invalid destination: -- '%s'" %(os.path.basename(sys.argv[0]),args.destination)
        print "Try '%s' --help for more information" %(os.path.basename(sys.argv[0]))
        sys.exit(2)
except googlemaps.exceptions.ApiError:
    print "%s: invalid API Key" %(os.path.basename(sys.argv[0]))
    print "Try '%s' --help for more information" %(os.path.basename(sys.argv[0]))
    sys.exit(2)

now = datetime.now()
directions_result = gmaps.directions(args.origin, args.destination, mode="driving", alternatives=args.alternatives ,departure_time=now, units="metric")

if args.debug:
    print json.dumps(directions_result,indent=4)

## ROUTE CALC

for i in directions_result:
    summary = []
    time_to_home = i['legs'][0]['duration_in_traffic']['value']
    distance_to_home = i['legs'][0]['distance']['value']
    # Use steps with more than 1000 meters to calculate summary
    for j in i['legs'][0]['steps']:
        if j['distance']['value'] > 1000:
            # Extract road name from the step instructions. All roads are named with a capital letter, a dash and a number, into a bold html tag
            road = re.search(r"<b>[A-Z]-(\d*)</b>", j['html_instructions'])
            # If there is no main road in the step instructions, it is not added to the summary. (sometimes, there are streets with more than 1000m)
            if road is not None:
                # Remove the bold html tag
                clean = re.sub(r"<.?b>", "", road.string[road.start():road.end()])
                # Only add road to summary if it is different from the last added road (first is always added)
                if len(summary) == 0:
                    summary.append(str(clean))
                elif clean != summary[len(summary)-1]:
                    summary.append(str(clean))
    print "Time to destination: %s, %s kms via %s" %(time.strftime('%H:%M',time.gmtime(time_to_home)),distance_to_home/1000,'[ %s ]' % ' -> '.join(map(str, summary)))
