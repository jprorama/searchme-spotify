#!/usr/bin/env python

#
# This queries /vi/me/player API to record the currently playing track
# with device information
#

import sys
import spotipy
import spotipy.util as util
import logging
import dataset
import json
import argparse

parser = argparse.ArgumentParser(description='Save history of played trackes on spotify')
parser.add_argument('-u', '--username', action="store", nargs=1,
                    help='spotify user for requesting history')
parser.add_argument('-f', '--file',
                    help='file to use a sqlite3 db')
parser.add_argument('-q', '--quiet', action="store_true",
                    help='supress output of filtered results')
parser.add_argument('-d', '--debug', action='store_true',
                    help='turn on debug of network connection')

args = parser.parse_args()

# connect to sqlite3 db for storing and updating queried data
if args.file:
    db = dataset.connect('sqlite:///{}'.format(args.file))
else:
    db = dataset.connect('sqlite:///spotify_history.db')


if args.debug:
    logging.basicConfig(level=logging.DEBUG)

current_playback = db.create_table('current_playback',
                          primary_id='mebotid',
                          primary_type=db.types.text)


scope = 'user-library-read,user-follow-read,user-read-recently-played,user-top-read,user-read-playback-state,user-read-currently-playing,playlist-read-private'

username = args.username[0]

token = util.prompt_for_user_token(username, scope)

if token:
    sp = spotipy.Spotify(auth=token)
    results = sp.current_playback()
    if args.debug:
        print(json.dumps(results))

    # no results if no music is playing
    if not results:
        exit()

    if not args.quiet:
        print("played_at, track, artist, length\n")
    
    # build row
    row = dict()
    row['mebotid'] = "{}:{}".format(results['timestamp'], results['item']['uri'])
    row['timestamp'] = results['timestamp']
    row['track'] = results['item']['uri']
    row['track_name'] = results['item']['name']
    row['device_id'] = results['device']['id']
    row['device_name'] = results['device']['name']
    row['is_playing'] = results['is_playing']
    row['json'] = json.dumps(results)

    # insert into db
    current_playback.insert_ignore(row, ['mebotid'], ensure=True)
    if not args.quiet:
        print("{}, {}, {}, {}".format(row['timestamp'], row['track_name'], row['device_name'], row['is_playing']))
else:
    print("Can't get token for", username)
