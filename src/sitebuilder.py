import html
from typing import List
from episode import Episode, Game

def style() -> str:
  return '''
    <style>
    body {
      background-color: silver;
      color: #fe59d7;
    }
    a {
      color: #fd0bff;
      text-decoration-style: dotted;
    }
    .episodelist {
      display: flex;
      flex-wrap: wrap;
      justify-content: center;
    }
    .episodewrapper {
      display: grid;
      grid-template-columns: 300px auto;
      grid-template-rows: auto 1fr;
      grid-column-gap: 18px;
      margin: 8px;
      background: #3b064d;
      padding: 8px;
      border-radius: 10px;
    }
    .title {
      font-weight: bold;
      grid-row: 1;
      grid-column: 2;
    }
    .episodecover {
      grid-row: 1/3;
      grid-column: 1;
      max-width: 100%;
      border-radius: 10px;
      box-shadow: 5px 5px 15px 5px #8105d8;
    }
    .gameslist {
      grid-row: 2;
      grid-column: 2;
      min-width: 300px;
      max-width: 500px;
    }
    .gameslist.empty {
      text-align: center;
      margin: auto;
    }
    ul:empty {
      display: none;
    }

    footer {
      text-align: center;
      position: fixed;
      bottom: -8px;
      left: -8px;
      line-height: 2em;
      background: rgba(59,6,77,0.8);
      -webkit-backdrop-filter: blur(20px);
      backdrop-filter: blur(20px);
      padding: 8px 8px 16px 16px;
      border-radius: 10px;
    }

    @media (max-width: 680px) {
      .episodewrapper {
        grid-template-columns: 1fr;
        grid-template-rows: auto auto 1fr;
        grid-row-gap: 8px;
        margin: 4px 0;
      }
      .episodecover {
        grid-row: 2;
        grid-column: 1;
        max-width: 100%;
        box-shadow: 2px 2px 2px 2px #8105d8;
      }
      .gameslist {
        grid-row: 3;
        grid-column: 1;
        width: 100%;
      }
      .title {
        grid-row: 1;
        grid-column: 1;
      }
    }
    @media (max-width: 1360px) {
      .episodewrapper {
        width: 100%;
      }
      footer {
        bottom: 0;
        left: 0;
        padding: 8px;
        width: 100%;
        border-radius: 0;
      }
    }
    </style>
  '''

def html_for_episode(episode: Episode) -> str:
  title = f'<h3 class="title">{html.escape(episode.title)}</h3>'
  cover_image = f'<img src="{html.escape(episode.cover_url)}" class="episodecover" alt="Cover for episode: {html.escape(episode.title)}"/>'

  games = [f'<li><a href="{html.escape(episode.get_timestamp_url_for_game(g))}">{html.escape(g.timestamp_string)} - {html.escape(g.name)}</a></li>' for g in episode.games]
  subtitle_text = ''
  gamelist_class = 'gameslist'
  if games:
    subtitle_text = 'Games and topics this episode:'
  else:
    subtitle_text = 'No games found in episode description'
    gamelist_class += ' empty'
  gamelist = f'<div class="{gamelist_class}"><span>{subtitle_text}</span><ul>{"".join(games)}</ul></div>'

  return f'<section class="episodewrapper">{title}{cover_image}{gamelist}</section>'

def body(episodes: List[Episode]) -> str:
  episodelist = ''.join([html_for_episode(e) for e in episodes])
  return f'<body><main class="episodelist">{episodelist}</main><footer><a href="https://github.com/hutattedonmyarm/Plotquisition/">Check me out on Github, I\'m open source</a></footer></body>'

def make_site(episodes: List[Episode], charset: str = 'UTF-8') -> str:
  description = 'Provides an automatically generated list of games, talked about in each episode of the Podquisition podcast'
  title = 'Plotquisition'
  return f'''
  <!DOCTYPE html>
  <html lang="en-US">
    <head>
      <meta charset="{html.escape(charset)}">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <meta name="description" content="{description}">
      <meta property="og:description" content="{description}">
      <meta property="og:title" content="{title}">
      <meta name="twitter:title" content="{title}">
      <title>{title}</title>
      {style()}
    </head>
    {body(episodes)}
  </html>'''
