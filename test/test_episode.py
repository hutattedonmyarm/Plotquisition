import datetime
import json
import os
import unittest
from plotquisition import episode

class TestGame(unittest.TestCase):

  def test_init_timestamp_string(self):
    g = episode.Game('Testgame', '06:12')
    self.assertEqual(g.name, 'Testgame')
    self.assertEqual(g.timestamp_string, '06:12')
    self.assertEqual(g.timestamp, 372)
    self.assertEqual(f'{g}', 'Testgame @06:12 (372s)')
    self.assertEqual(g.__repr__(), 'Testgame @06:12 (372s)')

    g = episode.Game('Testgame2', '1:35:00')
    self.assertEqual(g.name, 'Testgame2')
    self.assertEqual(g.timestamp_string, '1:35:00')
    self.assertEqual(g.timestamp, 5700)

  def test_init_timestamp(self):
    g = episode.Game('Testgame3', timestamp_string=None, timestamp=1191) #19m, 51s
    self.assertEqual(g.name, 'Testgame3')
    self.assertEqual(g.timestamp_string, '19:51')
    self.assertEqual(g.timestamp, 1191)

    g = episode.Game('Testgame4', timestamp_string=None, timestamp=303)
    self.assertEqual(g.name, 'Testgame4')
    self.assertEqual(g.timestamp_string, '05:03')
    self.assertEqual(g.timestamp, 303)

  def test_init_timestamp_string_and_timestamp(self):
    #Always prioritize seconds directly
    g = episode.Game('Testgame5', timestamp_string='07:59', timestamp=1191)
    self.assertEqual(g.name, 'Testgame5')
    self.assertEqual(g.timestamp_string, '19:51')
    self.assertEqual(g.timestamp, 1191)

  def test_games_from_episode_description(self):
    #Taken form Ep. 309
    desc = '''
    The conspiracy is finally unmasked.

    Games we played this week include:
    Hades (12:20)
    Call of Duty: Cold War (15:50)
    Spider-Man: Miles Morales (17:00)
    Hyrule Warriors: Age of Calamity (26:30)
    River City Girls (37:30)
    Super Mutant Alien Assault (38:40)
    Yakuza: Like a Dragon (40:35)
    Sackboy: A Big Adventure (45:00)

    News things talked about in this episode:
    Capcom ransomware attack (50:20)
    Square Enix commits to permanent work-from-home option (55:00)
    Amazon PS5 shipping issues (1:06:30)

    Find Laura at LauraKBuzz on Twitter, Twitch, YouTube, and Patreon. All her content goes on LauraKBuzz.com, and you can catch Access-Ability on YouTube every Friday.

    Follow Conrad at ConradZimmerman on Twitter and check out his Patreon (patreon.com/fistshark). You can also peruse his anti-capitalist propaganda at pinfultruth.com.
    '''
    found_games = episode.Game.from_episode_description(desc)

    expected_games = [
      episode.Game('Hades', '12:20'),
      episode.Game('Call of Duty: Cold War', '15:50'),
      episode.Game('Spider-Man: Miles Morales', '17:00'),
      episode.Game('Hyrule Warriors: Age of Calamity', '26:30'),
      episode.Game('River City Girls', '37:30'),
      episode.Game('Super Mutant Alien Assault', '38:40'),
      episode.Game('Yakuza: Like a Dragon', '40:35'),
      episode.Game('Sackboy: A Big Adventure', '45:00'),
      episode.Game('Capcom ransomware attack', '50:20'),
      episode.Game('Square Enix commits to permanent work-from-home option', '55:00'),
      episode.Game('Amazon PS5 shipping issues', '1:06:30')
    ]
    self.assertEqual(found_games, expected_games)

  def test_games_from_manual_fixes(self):
    manual_fixes = [
      {
        "name": "Marvel's Avengers",
        "timestamp_string": "6:41"
      },{
        "name": "Fall Guys",
        "timestamp": 1150
      },{
        "name": "This is only a test",
        "timestamp_string": "10:51",
        "timestamp": 4242 #1h, 10m, 42s
      }
    ]
    found_games = episode.Game.from_manual_fixes(manual_fixes)
    #Prefer the string from manual fixes
    expected_games = [
      episode.Game("Marvel's Avengers", '6:41'),
      episode.Game('Fall Guys', '19:10'),
      episode.Game('This is only a test', '10:51')
    ]
    self.assertEqual(found_games, expected_games)

class TestEpisode(unittest.TestCase):
  def test_init(self):
    url = 'https://example.com',
    audio_url = 'https://example.com/mp3.mp3',
    cover_url = 'https://example.com/img.jpg',
    title = 'Testtitle'
    description = 'Testdescription'
    duration_string = '01:06:32'
    pubdate_string = 'Thu, 26 Nov 2020 14:17:00 +0000'
    e = episode.Episode(
      url=url,
      audio_url=audio_url,
      cover_url=cover_url,
      title=title,
      description=description,
      pubdate_string=pubdate_string,
      duration_string=duration_string)

    self.assertEqual(e.games, [])
    self.assertEqual(e.url, url)
    self.assertEqual(e.audio_url, audio_url)
    self.assertEqual(e.cover_url, cover_url)
    self.assertEqual(e.title, title)
    self.assertEqual(e.description, description)
    self.assertEqual(e.pubdate_string, pubdate_string)
    self.assertEqual(e.pubdate, datetime.datetime(2020, 11, 26, 14, 17, tzinfo=datetime.timezone.utc))
    self.assertEqual(e.duration_string, duration_string)
    self.assertEqual(e.duration, 3992)

  def test__check_if_image_exists(self):
    self.assertTrue(episode.Episode._check_if_image_exists('https://i1.sndcdn.com/avatars-dIwpATFkIqyCdydz-oy5UOQ-original.jpg'))
    self.assertFalse(episode.Episode._check_if_image_exists('https://i.example.com/nonexistent.jpg'))

  def test_find_best_cover(self):
    # Empty input
    self.assertEqual(episode.Episode.find_best_cover(None), None)

    # Not existing input should be returned as is
    self.assertEqual(episode.Episode.find_best_cover('https://i1.sndcdn.com/avatars-dIwpATFkIqyCdydz-oy5UOQ-fakeurl.jpg'), 'https://i1.sndcdn.com/avatars-dIwpATFkIqyCdydz-oy5UOQ-fakeurl.jpg')

    # Find resized of '-original.jpg'
    orignal_cover = 'https://i1.sndcdn.com/avatars-dIwpATFkIqyCdydz-oy5UOQ-original.jpg'
    resized_orignal_cover = 'https://i1.sndcdn.com/avatars-dIwpATFkIqyCdydz-oy5UOQ-t300x300.jpg'
    self.assertEqual(episode.Episode.find_best_cover(orignal_cover), resized_orignal_cover)

    # Find resized of https
    cover = episode.Episode.find_best_cover('https://i1.sndcdn.com/artworks-Ttv8yfkeMPgBpT4K-y7gbzQ-t500x500.jpg')
    self.assertEqual(cover, 'https://i1.sndcdn.com/artworks-Ttv8yfkeMPgBpT4K-y7gbzQ-t300x300.jpg')

    # Find resized of http, should return https
    cover = episode.Episode.find_best_cover('http://i1.sndcdn.com/artworks-Ttv8yfkeMPgBpT4K-y7gbzQ-t500x500.jpg')
    self.assertEqual(cover, 'https://i1.sndcdn.com/artworks-Ttv8yfkeMPgBpT4K-y7gbzQ-t300x300.jpg')

    # File which matches the usualy filenames, but doesn't have any sizes available should return the original
    cover = episode.Episode.find_best_cover('https://raw.githubusercontent.com/hutattedonmyarm/Plotquisition/main/unittest-t100x100.jpg')
    self.assertEqual(cover, 'https://raw.githubusercontent.com/hutattedonmyarm/Plotquisition/main/unittest-t100x100.jpg')

  def test_episodes_from_rss(self):
    episodes = []

    # Use live cover_resizes.json to avoid making a crapton of network requests
    cover_resizes = {}
    with open('cover_resizes.json', 'r') as f:
      cover_resizes = json.load(f)

    episode.Episode.cover_resizes_file = 'test/cover_resizes_output.json'

    #episodes_from_rss expects the raw bytes from the network request
    with open('test/example.rss', 'rb') as f:
      episodes = episode.Episode.episodes_from_rss(f.read(), manual_fixes=None, cover_resizes=cover_resizes)
    self.assertEqual(len(episodes), 310)
    self.assertEqual(len(episodes[0].games), 11)
    self.assertEqual(episodes[0].title, 'Podquisition 309: Celestial Bodies')
    self.assertEqual(episodes[0].pubdate_string, 'Thu, 26 Nov 2020 17:00:42 +0000')
    self.assertEqual(episodes[0].pubdate, datetime.datetime(2020, 11, 26, 17, 00, 42, tzinfo=datetime.timezone.utc))
    self.assertEqual(episodes[0].url, 'https://soundcloud.com/jimquisition/podquisition309')
    self.assertEqual(episodes[0].audio_url, 'http://feeds.soundcloud.com/stream/936445702-jimquisition-podquisition309.mp3')
    self.assertEqual(episodes[0].cover_url, 'https://i1.sndcdn.com/artworks-Udcrhd3scFsrR9EJ-76dybA-t300x300.jpg')
    self.assertEqual(episodes[0].description, '''The conspiracy is finally unmasked.

Games we played this week include:
Hades (12:20)
Call of Duty: Cold War (15:50)
Spider-Man: Miles Morales (17:00)
Hyrule Warriors: Age of Calamity (26:30)
River City Girls (37:30)
Super Mutant Alien Assault (38:40)
Yakuza: Like a Dragon (40:35)
Sackboy: A Big Adventure (45:00)

News things talked about in this episode:
Capcom ransomware attack (50:20)
Square Enix commits to permanent work-from-home option (55:00)
Amazon PS5 shipping issues (1:06:30)

Find Laura at LauraKBuzz on Twitter, Twitch, YouTube, and Patreon. All her content goes on LauraKBuzz.com, and you can catch Access-Ability on YouTube every Friday.

Follow Conrad at ConradZimmerman on Twitter and check out his Patreon (patreon.com/fistshark). You can also peruse his anti-capitalist propaganda at pinfultruth.com.''')
    self.assertEqual(episodes[0].duration_string, '01:06:32')
    self.assertEqual(episodes[0].duration, 3992)

    g = episodes[0].games[10]
    self.assertEqual(g.name,'Amazon PS5 shipping issues')
    self.assertEqual(g.timestamp_string, '1:06:30')
    self.assertEqual(g.timestamp, 3990)
    self.assertEqual(episodes[0].get_timestamp_url_for_game(g), 'https://soundcloud.com/jimquisition/podquisition309#t=66:30')

    #Only for testing non-existent episode images
    with open('test/example_short.rss', 'rb') as f:
      episodes = episode.Episode.episodes_from_rss(f.read(), manual_fixes=None, cover_resizes=None)
    self.assertEqual(len(episodes), 3)
    self.assertEqual(episodes[2].cover_url,'https://i1.sndcdn.com/avatars-dIwpATFkIqyCdydz-oy5UOQ-t300x300.jpg')
    os.remove('test/cover_resizes_output.json')

