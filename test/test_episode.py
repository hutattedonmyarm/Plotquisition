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