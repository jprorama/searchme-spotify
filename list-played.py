#!/usr/bin/env python

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

history = db.create_table('history',
                          primary_id='mebotid',
                          primary_type=db.types.text)


scope = 'user-library-read,user-follow-read,user-read-recently-played,user-top-read,user-read-playback-state,user-read-currently-playing,playlist-read-private'

username = args.username[0]
#if len(sys.argv) > 1:
#    username = sys.argv[1]
#else:
#    print("Usage: %s username" % (sys.argv[0],))
#    sys.exit()

token = util.prompt_for_user_token(username, scope)

if token:
    sp = spotipy.Spotify(auth=token)
    results = sp.current_user_recently_played()
    if not args.quiet:
        print("played_at, track, artist, length\n")
    for item in results['items']:
        trackhist = dict()
        track = item['track']
        trackhist['mebotid'] = "{}:{}".format(track['id'], item['played_at'])
        trackhist['track'] = json.dumps(track)
        trackhist['played_at'] = item['played_at']
        trackhist['context'] = json.dumps(item['context'])
        history.insert_ignore(trackhist, ['mebotid'], ensure=True)
        if not args.quiet:
            print("{}, {}, {}, {}".format(item['played_at'], track['name'], track['artists'][0]['name'], track['duration_ms']))
else:
    printr("Can't get token for", username)
