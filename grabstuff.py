#!/usr/bin/env python

import json
import requests
import time
import argparse

myString = open('talkcard.html').read()
    
def card(room, data, next_data):
    """
    Transform the json data into a dictionary.
    """
    d = {}
    # Join names in public_name
    d['speaker'] = ', '.join(p['public_name'] for p in data['persons'])
    # Filter non-ascii ascii chars from the abstract and limit the
    # abstract to 1500 characters.
    d['abstract'] =  data['abstract'].encode('ascii', 'ignore')[:1500]
    # format the timestasmp
    t = time.strptime(data['date'], '%Y-%m-%dT%H:%M:%S+02:00')
    d['date'] = time.strftime('%d-%m-%Y', t)
    d['time'] = time.strftime('%H:%M', t)
    d['duration'] = data['duration']
    d['language'] = data['language']
    d['room'] = room
    d['title'] = data['title']
    d['subtitle'] = data['subtitle']
    d['next_title'] = next_data['title']
    d['next_speaker'] = ', '.join(p['public_name'] for p in next_data['persons'])
    if next_data['date'] == 'last':
        d['next_time'] = ''
    else:
        t_next = time.strptime(next_data['date'], '%Y-%m-%dT%H:%M:%S+02:00')
        d['next_time'] = time.strftime('%H:%M', t_next)
    return d
        

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('URL', help='The url to the json schedule')
    parser.add_argument('-r', '--room', help='Room name', 
        default=[], action='append', required=True)
    parser.add_argument('-d', '--day', help='Day number'\
        'The script assumes the days in the json file are numbered'\
        'from 0 onwards. It will substract 1 from the day numbers given',
        default=[], action='append', type=int, required=True)
    parser.add_argument('-p', '--prefix', help='Outputfile prefix'\
        'By default the output files are created in'\
        'the current working directory in the format'\
        'day_room.html.',
        default='')
    args = parser.parse_args()

    data = requests.get(args.URL).text.encode('ascii', 'ignore')
    for day in args.day:
        for room in args.room:
            with open('%s%s_%s.html' % (args.prefix, day, room), 'w') as out:
                # load talklist from the json file
                talklist = json.loads(data)['schedule']['conference']['days'][day-1]['rooms'][room]
                # Append a dummy talk so the last card will have a "next talk" 
                talklist.append({'title': 'More talks tomorrow', 'date': 'last', 'persons': []})
                print >>out, open('header.html').read()
                for index in range(len(talklist)-1):
                    print >>out, myString % card(room, talklist[index], talklist[index+1])
                print >>out, open('footer.html').read()

