import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime #RSS dates are RFC 822, which is handled in the email module
import re
from typing import Any, Dict, List, Optional

timestamp_regex = re.compile('(.*?)\(((\d{1,2}):(\d{2})(:(\d{2}))?)\)(,|\.|\n|$)')

class Game:
  def __init__(self, name: str, timestamp_string: str, timestamp: Optional[int] = None):
    self.name = name
    if timestamp is None:
      self.timestamp_string = timestamp_string
      self.timestamp = Episode.seconds_from_timestring(timestamp_string)
    else:
      m = int(timestamp/60)
      s = timestamp%60
      self.timestamp_string = f'{m:02d}:{s:02d}' #Converting to string to convert it back to secs later is dumb
      self.timestamp = timestamp

  # Class 'Game' is not known at the time this is parsed
  # So the return type needs to be declared using forward references,
  # that is, as string
  @staticmethod
  def from_episode_description(description: str) -> List['Game']:
    lines = description.split('\n')
    games = []
    for line in lines:
      line = line.strip()
      matches = timestamp_regex.finditer(line)
      for match in matches:
        game = match.group(1).strip()
        ts = match.group(2)
        games.append(Game(name = game, timestamp_string=ts))
    if games:
      games[0].name = games[0].name.lstrip('Games we played this week include:').strip()
      games[-1].name = games[-1].name.lstrip(' and ').strip()
    return games

  @staticmethod
  def from_manual_fixes(manual_fixes: List[Dict[str, Any]]) -> List['Game']:
    games = []
    for game in manual_fixes:
      timestamp_string = None
      timestamp = None
      if 'timestamp_string' in game:
        timestamp_string = game['timestamp_string']
      else:
        timestamp = int(game['timestamp'])
      games.append(Game(
        name=game['name'],
        timestamp_string=timestamp_string,
        timestamp=timestamp))
    return games

  def __str__(self):
    return f'{self.name} @{self.timestamp_string} ({self.timestamp}s)'

  def __repr__(self):
    return self.__str__()


class Episode():
  def __init__(
    self,
    url: str,
    audio_url: str,
    cover_url: Optional[str],
    title: str,
    description: str,
    pubdate_string: str,
    duration_string: str):

    self.url = url
    self.title = title
    self.cover_url = cover_url
    self.audio_url = audio_url
    self.title = title
    self.duration_string = duration_string
    self.description = description
    self.pubdate_string = parsedate_to_datetime(pubdate_string)
    self.pubdate = description
    self.duration = Episode.seconds_from_timestring(duration_string)
    self.games: List[Game] = []

  @staticmethod
  def seconds_from_timestring(timestring: str) -> int:
    return sum([int(x)*(60**i) for i,x in enumerate(reversed(timestring.split(':')))])

  @staticmethod
  def episodes_from_rss(feed: str, manual_fixes: Optional[Dict[str, Any]]) -> List['Episode']:
    itunes_ns_regex = re.compile('xmlns:itunes="(.*?)"')
    namespaces = {
      'itunes': itunes_ns_regex.search(feed.decode('utf8')).group(1)
    }

    channel = ET.fromstring(feed).find('channel')
    channel_cover = channel.find('itunes:image', namespaces).get('href')

    episodes: List[Episode] = []
    for item in channel.findall('item'):
      title = item.find('title').text
      if not title.startswith('Podquisition') and not title.startswith('The Podquisition'):
        print(f'Skipping episode "{title}", doesn\'t seem to be a Podquisition')
        continue
      url = item.find('link').text
      duration = item.find('itunes:duration', namespaces).text
      audio_url = item.find('enclosure').get('url')
      cover_url = None
      try:
        cover_url = item.find('itunes:image', namespaces).get('href')
      except:
        print(f'Could not find cover for episode "{title}". Using channel cover!')
        cover_url = channel_cover
      pubdate = item.find('pubDate').text
      description = item.find('description').text
      episode = Episode(
        url=url,
        audio_url=audio_url,
        cover_url=cover_url,
        title=title,
        duration_string=duration,
        description=description,
        pubdate_string=pubdate)
      episode.games = Game.from_manual_fixes(manual_fixes[url]) if url in manual_fixes else Game.from_episode_description(description)
      episodes.append(episode)
    return episodes

  def get_timestamp_url_for_game(self, game: Game) -> str:
    secs = int(game.timestamp % 60)
    mins = int((game.timestamp - secs) / 60)
    return f'{self.url}#t={mins}:{secs:02d}'
