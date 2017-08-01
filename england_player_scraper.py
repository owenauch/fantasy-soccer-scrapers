# player scraper methods
# scrapes player stats from Fox Sports website and Premier League website

import csv
from urllib2 import urlopen
from bs4 import BeautifulSoup
import pandas as pd

base_url = 'http://www.foxsports.com/soccer/stats?competition=1'

#open and soupify
def soupify(url, ctx):
  html = urlopen(url, context=ctx).read()
  soup = BeautifulSoup(html, "lxml")
  return soup

# parse html table to pandas dataframe
def parse_html_table(table):
  n_columns = 0
  n_rows=0
  column_names = []

  # Find number of rows and columns
  # we also find the column titles if we can
  for row in table.find_all('tr'):
      
      # Determine the number of rows in the table
      td_tags = row.find_all('td')
      if len(td_tags) > 0:
          n_rows+=1
          if n_columns == 0:
              # Set the number of columns for our table
              n_columns = len(td_tags)
              
      # Handle column names if we find them
      th_tags = row.find_all('th') 
      if len(th_tags) > 0 and len(column_names) == 0:
          for th in th_tags:
              column_names.append(th.get_text().strip())

  # Safeguard on Column Titles
  if len(column_names) > 0 and len(column_names) != n_columns:
      raise Exception("Column titles do not match the number of columns")

  columns = column_names if len(column_names) > 0 else range(0,n_columns)
  df = pd.DataFrame(columns = columns,
                    index= range(0,n_rows))
  row_marker = 0
  for row in table.find_all('tr'):
      column_marker = 0
      columns = row.find_all('td')
      for column in columns:
          if column_marker == 0:
            df.iat[row_marker,column_marker] = column.find_all('span')[1].get_text()
          else:
            df.iat[row_marker,column_marker] = column.get_text()
          column_marker += 1
      if len(columns) > 0:
          row_marker += 1
          
  # Convert to float if possible
  for col in df:
      try:
          df[col] = df[col].astype(float)
      except ValueError:
          pass

  return df

# scrape players by position
# positions are "Defender", "Midfielder", "Forward"
def scrape_by_pos(year, ctx, position):
  print 'Scraping ' + position + 's'

  # standard stats
  url = base_url + '&season=' + year + '0&category=STANDARD&pos=' + position + '&team=0&isOpp=0&sort=3&sortOrder=0'
  filename = './data/' + position + '_England_' + year + '_Standard.csv'

  soup = soupify(url, ctx)
  table = soup.find_all('table')[0]
  standard_dataframe = parse_html_table(table)

  # will continue going until it can't see the next link anymore
  keep_going = True
  while keep_going:
    soup = soupify(url, ctx)
    table = soup.find_all('table')[0]
    standard_dataframe = standard_dataframe.append(parse_html_table(table))
    paginator = soup.find_all("div", class_="wisbb_paginator")[0]
    next_button = paginator.find_all('a')[-1]
    if "Next" not in next_button.get_text():
      keep_going = False
    else:
      url = 'http://www.foxsports.com/' + next_button['href']

    print '+++++++++++++'

  standard_dataframe.to_csv(filename, encoding='utf-8', index=False)

  # discipline stats
  url = base_url + '&season=' + year + '0&category=DISCIPLINE&pos=' + position + '&team=0&isOpp=0&sort=3&sortOrder=0'
  filename = './data/' + position + '_England_' + year + '_Discipline.csv'

  soup = soupify(url, ctx)
  table = soup.find_all('table')[0]
  discipline_dataframe = parse_html_table(table)

  # will continue going until it can't see the next link anymore
  keep_going = True
  while keep_going:
    soup = soupify(url, ctx)
    table = soup.find_all('table')[0]
    discipline_dataframe = discipline_dataframe.append(parse_html_table(table))
    paginator = soup.find_all("div", class_="wisbb_paginator")[0]
    next_button = paginator.find_all('a')[-1]
    if "Next" not in next_button.get_text():
      keep_going = False
    else:
      url = 'http://www.foxsports.com/' + next_button['href']

    print '+++++++++++++' 

  discipline_dataframe.to_csv(filename, encoding='utf-8', index=False)

def scrape_goalie(year, ctx):
  print 'Scraping goalies'
  url = base_url + '&season=' + year + '0&category=GOALKEEPING'
  filename = './data/Goalkeeper_England' + '_' + year + '.csv'

  soup = soupify(url, ctx)
  table = soup.find_all('table')[0]
  dataframe = parse_html_table(table)

  soup = soupify(url, ctx)
  table = soup.find_all('table')[0]
  dataframe = dataframe.append(parse_html_table(table))
  print '+++++++++++++'

  dataframe.to_csv(filename, encoding='utf-8', index=False)

# get england player data and output to CSV
def scrape(year, ctx):
  print 'Scraping ' + year + ' data for England...'
  scrape_by_pos(year, ctx, "Defender")
  scrape_by_pos(year, ctx, "Midfielder")
  scrape_by_pos(year, ctx, "Forward")
  scrape_goalie(year, ctx)
  print 'CSVs of data created!'
