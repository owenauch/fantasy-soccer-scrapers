# Soccer player stat scraper runner
# Arguments -- 
# [1]: league ("England", "France", "Spain", "Germany", "Italy")
# [2]: year ("2013", "2014", "2015", "2016")

import sys
from sys import version_info
import ssl

import england_player_scraper
import player_scraper

# verify set to false (not secure but doesn't really matter for this)
def verify_false():
  ctx = ssl.create_default_context()
  ctx.check_hostname = False
  ctx.verify_mode = ssl.CERT_NONE
  return ctx

if __name__ == "__main__":
  ctx = verify_false()

  if sys.argv[1] != 'all':
    if sys.argv[1] == 'England':
      england_player_scraper.scrape(sys.argv[2], ctx)
    else:
      player_scraper.scrape(sys.argv[1], sys.argv[2], ctx)
  else:
    england_player_scraper.scrape(sys.argv[2], ctx)
    player_scraper.scrape('Spain', sys.argv[2], ctx)
    player_scraper.scrape('France', sys.argv[2], ctx)
    player_scraper.scrape('Italy', sys.argv[2], ctx)
    player_scraper.scrape('Germany', sys.argv[2], ctx)