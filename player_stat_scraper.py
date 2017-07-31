# Soccer player stat scraper
# Arguments -- 
# [1]: league ("England", "France", "Spain", "Germany", "Italy")
# [2]: year ("2013", "2014", "2015", "2016")

import sys
from sys import version_info
from bs4 import BeautifulSoup
from urllib2 import urlopen
import ssl

import england_player_scraper
import player_scraper

# verify set to false (not secure but doesn't really matter for this)
def verify_false():
  ctx = ssl.create_default_context()
  ctx.check_hostname = False
  ctx.verify_mode = ssl.CERT_NONE
  return ctx

# open and soupify
def soupify(url, ctx):
  html = urlopen(url, context=ctx).read()
  soup = BeautifulSoup(html, "lxml")
  return soup

if __name__ == "__main__":
  print str(sys.argv)

  # if sys.argv[1]
  #   if sys.argv[1] === "England":
  #     england_player_scraper.scrape(sys.argv[2])
  #   elif sys.argv[1] 