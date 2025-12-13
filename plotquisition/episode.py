import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime #RSS dates are RFC 822, which is handled in the email module
import json
import re
import urllib.request
from typing import Any, Dict, List, Optional

timestamp_regex = re.compile(r'(.*?)\(((\d{1,2}):(\d{2})(:(\d{2}))?)\)(,|\.|\n| .*|$)')
cover_size_regex = re.compile(r'(t\d+x\d+)|(original)\.jpg$')

class Game:
  def __init__(self, name: str, timestamp_string: str, timestamp: Optional[int] = None):
    self.name = name
    if timestamp is None:
      self.timestamp_string = timestamp_string
      self.timestamp = Episode.seconds_from_timestring(timestamp_string)
    else:
      m = int(timestamp/60)
      s = timestamp%60
      if m > 60:
        h = int(m/60)
        m = int(m%60)
        self.timestamp_string = f'{h:d}:{m:02d}:{s:02d}' #Converting to string to convert it back to secs later is dumb
      else:
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
        print('Match in line', line, match, match.group(1), match.group(2), match.group(7))
        g1 = match.group(1)
        ts = match.group(2)
        if g1:
          game = g1.strip()
        else:
          game = match.group(7).strip()
        # Splits format min:sec into its components,
        # Reverses the list so seconds come first, then minutes, then hours,
        # multiplies each by 60^index (so 60^0 = 1 for seconds, 60^1 = 60 for minutes, 60^2 = 3660 for hours, ...)
        # Sums up all the seconds
        # Gives the total seconds for this timestamp
        ts_seconds = sum((int(x[1])*60**int(x[0]) for x in enumerate(reversed(ts.split(':')))))
        # Use seconds instead of timestamp string so I can format it
        games.append(Game(name = game, timestamp_string=ts, timestamp=ts_seconds))
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

  def __eq__(self, other):
    return (self.name == other.name
      and self.timestamp == other.timestamp
      and self.timestamp_string == other.timestamp_string)


class Episode():
  cover_resizes_file = 'cover_resizes.json'

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
    self.pubdate = parsedate_to_datetime(pubdate_string)
    self.pubdate_string = pubdate_string
    self.duration = Episode.seconds_from_timestring(duration_string)
    self.games: List[Game] = []

  @staticmethod
  def seconds_from_timestring(timestring: str) -> int:
    return sum([int(x)*(60**i) for i,x in enumerate(reversed(timestring.split(':')))])

  @staticmethod
  def _check_if_image_exists(cover_url: str) -> bool:
    status = -1
    try:
      status = urllib.request.urlopen(
        urllib.request.Request(cover_url, method='HEAD')
      ).status
    except Exception as e:
      #requests throws on not found or any error
      pass
    return status == 200

  # Covers can be huge (usually 3000x3000px) for the Podquisition
  # The URLs are contain the image size though,
  # so this checks for smaller sizes (200px, 300px, and "original" usually exist)
  # and uses these if found
  @staticmethod
  def find_best_cover(original_cover_url: str) -> str:
    if not original_cover_url:
      return original_cover_url
    match = cover_size_regex.search(original_cover_url)
    if not match:
      return original_cover_url
    size_urls = {
      '300': None,
      '200': None,
      'orig': None,
    }
    if match.groups()[0]:
      #sized
      size_urls['orig'] = re.sub(cover_size_regex, r'\2original', original_cover_url)
      size_urls['200'] = re.sub(cover_size_regex, r'\2t200x200', original_cover_url)
      size_urls['300'] = re.sub(cover_size_regex, r'\2t300x300', original_cover_url)
    if match.groups()[1]:
      #original
      size_urls['orig'] = original_cover_url
      size_urls['200'] = re.sub(cover_size_regex, r'\1t200x200.jpg', original_cover_url)
      size_urls['300'] = re.sub(cover_size_regex, r'\1t300x300.jpg', original_cover_url)

    for size in size_urls:
      if Episode._check_if_image_exists(size_urls[size]):
        if size_urls[size].startswith('http://'):
          https_url = size_urls[size].replace('http://', 'https://', 1)
          https_exists = Episode._check_if_image_exists(https_url)
          return https_url if https_exists else size_urls[size]
        return size_urls[size]
    return original_cover_url

  @staticmethod
  def episodes_from_rss(
    feed: bytes,
    manual_fixes: Optional[Dict[str, Any]] = None,
    cover_resizes: Optional[Dict[str, str]] = None) -> List['Episode']:

    if manual_fixes is None:
      manual_fixes = []
    if cover_resizes is None:
      cover_resizes = {}

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
      # Cover sizes are saved, so we don't need to check 300+ URLs
      # on every run
      if url in cover_resizes:
        cover_url = cover_resizes[url]
      else:
        try:
          cover_url = item.find('itunes:image', namespaces).get('href')
        except:
          print(f'Could not find cover for episode "{title}". Using channel cover!')
          cover_url = channel_cover
        cover_url = Episode.find_best_cover(cover_url)
        cover_resizes[url] = cover_url
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

    with open(Episode.cover_resizes_file, 'w') as f:
      cover_resizes = json.dump(cover_resizes, f, indent=2)
    return episodes

  def get_timestamp_url_for_game(self, game: Game) -> str:
    secs = int(game.timestamp % 60)
    mins = int((game.timestamp - secs) / 60)
    return f'{self.url}#t={mins}:{secs:02d}'
