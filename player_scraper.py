# player scraper methods
# scrapes player stats from Fox Sports website

import csv
from urllib2 import urlopen
from bs4 import BeautifulSoup
import pandas as pd

country_codes = {'Germany': '4', 'Spain': '2', 'France': '43', 'Italy': '3'}
base_url = 'http://www.foxsports.com/soccer/stats?competition='

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
            df.iat[row_marker,column_marker] = column.find_all("a", { "class" : "wisbb_fullPlayer" })[0].find_all('span')[0].get_text()
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

# scrape goalkeepers
def scrape_goalie(country, year, ctx):
  print 'Scraping goalies'
  url = base_url + country_codes[country] + '&season=' + year + '0&category=GOALKEEPING'
  filename = './data/Goalkeeper' + '_' + country + '_' + year + '.csv'

  soup = soupify(url, ctx)
  table = soup.find_all('table')[0]
  dataframe = parse_html_table(table)

  soup = soupify(url, ctx)
  table = soup.find_all('table')[0]
  dataframe = dataframe.append(parse_html_table(table))
  print '+++++++++++++'

  dataframe.to_csv(filename, encoding='utf-8', index=False)

# scrape players by position
# positions are "Defender", "Midfielder", "Forward"
def scrape_by_pos(country, year, ctx, position):
  print 'Scraping ' + position + 's'

  # get data into two dataframes
  # CONTROL
  url = base_url + country_codes[country] + '&season=' + year + '0&category=CONTROL&pos=' + position + '&team=0&isOpp=0&sort=3&sortOrder=0'
  filename = './data/' + position + '_' + country + '_' + year + '.csv'

  soup = soupify(url, ctx)
  table = soup.find_all('table')[0]
  c_dataframe = parse_html_table(table)

  # will continue going until it can't see the next link anymore
  keep_going = True
  while keep_going:
    soup = soupify(url, ctx)
    table = soup.find_all('table')[0]
    c_dataframe = c_dataframe.append(parse_html_table(table))
    paginator = soup.find_all("div", class_="wisbb_paginator")[0]
    next_button = paginator.find_all('a')[-1]
    if "Next" not in next_button.get_text():
      keep_going = False
    else:
      url = 'http://www.foxsports.com/' + next_button['href']

    print '+++++++++++++'

  c_dataframe = c_dataframe.rename(columns = {'CONTROL':'Name'})
  c_dataframe = c_dataframe.drop(['MP', 'TT', 'P', 'GMB', 'OFF', 'CK'], axis=1)
  c_dataframe = c_dataframe.drop_duplicates()

  # DISCIPLINE
  url = base_url + country_codes[country] + '&season=' + year + '0&category=DISCIPLINE&pos=' + position + '&team=0&isOpp=0&sort=3&sortOrder=0'

  soup = soupify(url, ctx)
  table = soup.find_all('table')[0]
  d_dataframe = parse_html_table(table)

  # will continue going until it can't see the next link anymore
  keep_going = True
  while keep_going:
    paginator = soup.find_all("div", class_="wisbb_paginator")[0]
    next_button = paginator.find_all('a')[-1]
    if "Next" not in next_button.get_text():
      keep_going = False
    else:
      url = 'http://www.foxsports.com/' + next_button['href']
      soup = soupify(url, ctx)
      table = soup.find_all('table')[0]
      d_dataframe = d_dataframe.append(parse_html_table(table))

    print '+++++++++++++'

  d_dataframe = d_dataframe.rename(columns = {'DISCIPLINE':'Name'})
  d_dataframe = d_dataframe.drop(['GP', 'GS', 'MP', 'FS', 'FC', 'OFF', 'C', 'CK', 'PK'], axis=1)
  d_dataframe = d_dataframe.drop_duplicates()

  # STANDARD
  url = base_url + country_codes[country] + '&season=' + year + '0&category=STANDARD&pos=' + position + '&team=0&isOpp=0&sort=3&sortOrder=0'

  soup = soupify(url, ctx)
  table = soup.find_all('table')[0]
  s_dataframe = parse_html_table(table)

  # will continue going until it can't see the next link anymore
  keep_going = True
  while keep_going:
    paginator = soup.find_all("div", class_="wisbb_paginator")[0]
    next_button = paginator.find_all('a')[-1]
    if "Next" not in next_button.get_text():
      keep_going = False
    else:
      url = 'http://www.foxsports.com/' + next_button['href']
      soup = soupify(url, ctx)
      table = soup.find_all('table')[0]
      s_dataframe = s_dataframe.append(parse_html_table(table))

    print '+++++++++++++'

  s_dataframe = s_dataframe.rename(columns = {'STANDARD':'Name'})
  s_dataframe = s_dataframe.drop(['GP', 'GS', 'MP', 'YC', 'RC'], axis=1)
  s_dataframe = s_dataframe.drop_duplicates()

  # combine
  dataframe = pd.merge(d_dataframe, c_dataframe, on='Name', how='outer')
  dataframe = pd.merge(dataframe, s_dataframe, on='Name', how='outer')

  dataframe.to_csv(filename, encoding='utf-8', index=False)

# get data and output csv
# country = "Spain", "France", "Italy", "Germany"
# year = "2013", "2014", "2015", "2016"
# ctx = context
def scrape(country, year, ctx):
  print 'Scraping ' + year + ' data for ' + country + '...'
  scrape_by_pos(country, year, ctx, "Defender")
  scrape_by_pos(country, year, ctx, "Midfielder")
  scrape_by_pos(country, year, ctx, "Forward")
  scrape_goalie(country, year, ctx)
  print 'CSVs of data created!'

  
