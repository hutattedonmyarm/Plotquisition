import datetime
import json
import os
import re
import unittest
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from plotquisition import episode
from plotquisition import sitebuilder

class TestSitebuilderitebuilder(unittest.TestCase):

  """
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
  """

  def test_style(self):
    style = sitebuilder.style().strip()
    self.assertTrue(style.startswith('<style>'))
    self.assertTrue(style.endswith('</style>'))
    # Remove style tags
    css = re.sub(r'^<style>', '', re.sub(r'</style>$', '', style))

    # Check with W3C validator for valid CSS
    resp = urllib.request.urlopen('http://jigsaw.w3.org/css-validator/validator?text='+urllib.parse.quote(css)+'&profile=css3&output=soap12').read()
    root = ET.fromstring(resp)
    ns = 'http://www.w3.org/2003/05/soap-envelope'
    valns = 'http://www.w3.org/2005/07/css-validator'
    body = root.find('{'+ns+'}Body')
    validation_response = body.find('{'+valns+'}cssvalidationresponse')

    validity = validation_response.find('{'+valns+'}validity')
    is_valid = validity.text == 'true'

    # Ignore the the backdrop error, it's currently in a draft
    # Make sure it's the only error though
    if not is_valid:
      errors = validation_response.find('{'+valns+'}result').find('{'+valns+'}errors')
      error_count = int(errors.find('{'+valns+'}errorcount').text)
      self.assertEqual(error_count, 1)
      error = errors.find('{'+valns+'}errorlist').find('{'+valns+'}error').find('{'+valns+'}message').text.strip()
      self.assertEqual(error, 'Property “backdrop-filter” doesn\'t exist :')
    #else:
    #  self.assertTrue(is_valid)

  def test_html_for_episode(self):
    url = 'https://example.com'
    audio_url = 'https://example.com/mp3.mp3'
    cover_url = 'https://example.com/img.jpg'
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
    e.games = [episode.Game('Testgame', '06:12'), episode.Game('Testgame2', '1:35:00')]

    html = sitebuilder.html_for_episode(e)
    self.assertIsNotNone(html)
    root = ET.fromstring(html)
    self.assertEqual(root.tag, 'section')
    self.assertEqual(len(root.findall('./*[@class="title"]')), 1) #exactly one title
    images = root.findall('img')
    self.assertEqual(len(images), 1) #exactly one image, should be cover
    self.assertEqual(images[0].attrib['src'], cover_url)
    gameslist = root.findall('./*[@class="gameslist"]')[0].find('ul').findall('li')
    self.assertEqual(len(gameslist), 2)
    game1 = gameslist[0].find('a')
    self.assertEqual(game1.attrib['href'], 'https://example.com#t=6:12')
    self.assertEqual(game1.text, '06:12 - Testgame')
    game2 = gameslist[1].find('a')
    self.assertEqual(game2.attrib['href'], 'https://example.com#t=95:00')
    self.assertEqual(game2.text, '1:35:00 - Testgame2')

  def test_html_for_empty_episode(self):
    url = 'https://example.com'
    audio_url = 'https://example.com/mp3.mp3'
    cover_url = 'https://example.com/img.jpg'
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

    html = sitebuilder.html_for_episode(e)
    self.assertIsNotNone(html)
    root = ET.fromstring(html)
    gameslist_wrong = root.find('./*[@class="gameslist"]')
    self.assertIsNone(gameslist_wrong)
    gameslist = root.find('./*[@class="gameslist empty"]')
    message = gameslist.find('span').text
    self.assertEqual(message, 'No games found in episode description')
    self.assertEqual(len(list(gameslist.find('ul'))), 0)

  def test_body(self):
    url = 'https://example.com'
    audio_url = 'https://example.com/mp3.mp3'
    cover_url = 'https://example.com/img.jpg'
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
    html = sitebuilder.body([e, e])
    root = ET.fromstring(html)
    episodelist = root.findall('./*[@class="episodelist"]')[0]
    self.assertEqual(len(episodelist.findall('section')), 2)

  def test_make_site(self):
    url = 'https://example.com'
    audio_url = 'https://example.com/mp3.mp3'
    cover_url = 'https://example.com/img.jpg'
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
    site = sitebuilder.make_site([e], charset='UTF-8')
    root = ET.fromstring(site)
    charset = root.find('head').findall('./meta[@charset]')
    self.assertEqual(len(charset), 1)
    self.assertEqual(charset[0].attrib['charset'], 'UTF-8')

