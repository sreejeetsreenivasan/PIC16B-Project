import pandas as pd
import requests
from bs4 import BeautifulSoup
from collections import defaultdict
import json

headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2 Safari/601.3.9"}
url = "https://isotp.metro.net/MetroRidership/YearOverYear.aspx" # this url redirects to 2023 March as the dropdown data

def parse_ridership(list_of_ids):
   for table_id in list_of_ids:
      print("Boardings for category:", table_id.split("_")[-1], '\n')

      rail_ridership = soup.find(lambda tag: tag.name=="table" and tag.has_attr('id') and tag['id']==table_id)
      rows = defaultdict(list)
   
      # First row is the list of dates
      first_row = rail_ridership.find('tr')
      dates = first_row.find_all('th')
      headers = ["Boarding Category"]
      headers += [date.text for date in dates if date.text != ""]

      for row in rail_ridership.find_all('tr'):
         for index, tag in enumerate(row.find_all('td')):
            rows[headers[index]].append(tag.text)
      # print(rows)
      # list_of_lines.append(rows) 
      # df = pd.DataFrame([(k, v) for k, v in rows.items()], columns=["Date", "Boardings"])
      df = pd.DataFrame(rows)
      print(df)

with requests.Session() as s:
   months = [2]

   # Get data from page directly
   r = requests.get(url=url, headers=headers, verify=False)

   # Now we need to work with BeautifulSoup to send POST requests
   soup = BeautifulSoup(r.content, 'html.parser')
   list_of_ids = ["ContentPlaceHolder1_rpRailRidership_rpRailSystemwide_gvRailSYS",
                  "ContentPlaceHolder1_rpRailRidership_rpRailRed_gvRailRed",
                  "ContentPlaceHolder1_rpRailRidership_rpRailBlue_gvRailBlue",
                  "ContentPlaceHolder1_rpRailRidership_rpRailExpo_gvRailExpo",
                  "ContentPlaceHolder1_rpRailRidership_rpRailGreen_gvRailGreen",
                  "ContentPlaceHolder1_rpRailRidership_rpRailGold_gvRailGold"]  
   list_of_lines = []
   parse_ridership(list_of_ids)
   
   for month in months:
      payload = {"ctl00$ContentPlaceHolder1$ddlYear:": "2023", "ctl00$ContentPlaceHolder1$ddlPeriod": str(month)}
      r = requests.post(url=url, headers=headers, params=payload, verify=False)
      print(r.text)
      # soup = BeautifulSoup(r.content, 'html.parser')
      # parse_ridership(list_of_ids) 

   """
   for table_id in list_of_ids:
      print("Boardings for category:", table_id.split("_")[-1], '\n')

      rail_ridership = soup.find(lambda tag: tag.name=="table" and tag.has_attr('id') and tag['id']==table_id)
      rows = defaultdict(list)
   
      # First row is the list of dates
      first_row = rail_ridership.find('tr')
      dates = first_row.find_all('th')
      headers = ["Boarding Category"]
      headers += [date.text for date in dates if date.text != ""]
   
      for row in rail_ridership.find_all('tr'):
         for index, tag in enumerate(row.find_all('td')):
            rows[headers[index]].append(tag.text)
      # print(rows)
      # list_of_lines.append(rows) 
      # df = pd.DataFrame([(k, v) for k, v in rows.items()], columns=["Date", "Boardings"])
      df = pd.DataFrame(rows)
      print(df)
   """


