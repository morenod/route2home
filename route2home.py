#!/usr/bin/python
import googlemaps
import json
from datetime import datetime
import time
import argparse
from argparse import RawTextHelpFormatter

__VERSION__ = "0.1"

## ARGS PARSER

parser = argparse.ArgumentParser(description="Route and travel time calculation", epilog="""

GoogleMaps API Key required, obtain it on https://developers.google.com/console
Report bugs on https://github.com/morenod/route2home
""", formatter_class=RawTextHelpFormatter)
parser.add_argument('--origin', metavar='ORIGIN', nargs='?', type=str, help='Departure Point', required=True)
parser.add_argument('--destination', metavar='DESTINATION', nargs='?', type=str, help='Destination Point', required=True)
parser.add_argument('--alternatives', action='store_true', help='Obtain alternatives routes', default=False)
parser.add_argument('--apikey', metavar='KEY', nargs='?', type=str, help='GoogleMaps API Key', required=True)
parser.add_argument('--version', action='version', version=__VERSION__)
args = parser.parse_args()

## ARGS VERIFICATION

gmaps = googlemaps.Client(key=args.apikey)

now = datetime.now()
directions_result = gmaps.directions(args.origin, args.destination, mode="driving", alternatives=args.alternatives ,departure_time=now, units="metric")

## ROUTE CALC

for i in directions_result:
    time_to_home = i['legs'][0]['duration_in_traffic']['value']
    route_to_home = i['summary']
    distance_to_home = i['legs'][0]['distance']['value']
    print "Time to home: %s, %s kms via %s" %(time.strftime('%H:%M',time.gmtime(time_to_home)),distance_to_home/1000,route_to_home)
