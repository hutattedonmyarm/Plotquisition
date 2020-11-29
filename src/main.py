#!/usr/bin/env python3

import urllib.request
from episode import Episode
from sitebuilder import make_site
import os
import re

if __name__ == '__main__':
  feed = urllib.request.urlopen('http://feeds.soundcloud.com/users/soundcloud:users:125332894/sounds.rss').read()

  episodes = Episode.episodes_from_rss(feed)

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
