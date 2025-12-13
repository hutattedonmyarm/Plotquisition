#!/usr/bin/env python3

import urllib.request
import http.client
from episode import Episode
from sitebuilder import make_site
import json
import os
import re
import sys


if __name__ == '__main__':
  try:
    feed = urllib.request.urlopen('https://feed.podbean.com/jimquisition/feed.xml').read()
  except urllib.error.HTTPError as e:
    print(f'Error fetching RSS: {e.code}: {e.reason}')
    sys.exit(1)
  except http.client.IncompleteRead as ire:
    print(f'Error fetching RSS: Incomplete read: {ire}')
    sys.exit(1)

  manual_fixes = {}
  with open('manual_fixes.json', 'r') as f:
    manual_fixes = json.load(f)

  cover_resizes = {}
  with open('cover_resizes.json', 'r') as f:
    cover_resizes = json.load(f)

  episodes = Episode.episodes_from_rss(feed, manual_fixes=manual_fixes, cover_resizes=cover_resizes)

  #for episode in episodes:
  #  print(f'{episode.title}, {episode.pubdate_string}')
  #  if episode.games:
  #    print('Games and topics:')
  #    print('\n'.join([f'- {game.name} @ {game.timestamp_string} -> #{episode.get_timestamp_url_for_game(game)}' for game in episode.games]))
  #  else:
  #    print('No games found in episode description')
  #  print('==========================')

  index_file = os.path.abspath('index.html')
  print('Generating ' + index_file)
  with open(index_file, 'w') as f:
    charset = 'UTF-8'
    match = re.search(r'<\?xml .*? encoding="(UTF-8)"\?>', feed.decode('utf-8'))
    if match:
      charset = match.group(1)
    f.write(make_site(episodes, charset=charset))
