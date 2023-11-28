import pandas as pd
import requests
from bs4 import BeautifulSoup
from collections import defaultdict
import json
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2 Safari/601.3.9"}
url = "https://isotp.metro.net/MetroRidership/YearOverYear.aspx" # this url redirects to 2023 October as the dropdown data

def parse_ridership(list_of_ids):
   dataframes_by_line = []
   for table_id in list_of_ids:
      # print("Boardings for category:", table_id.split("_")[-1], '\n')

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
      df = pd.DataFrame(rows)
      df.set_index("Boarding Category", drop=True, inplace=True)
      dataframes_by_line.append(df)
   return dataframes_by_line

with requests.Session() as s:
   # months = [2]
   # header = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"}
   
   r = requests.get(url=url, headers=headers, verify=False)

   soup = BeautifulSoup(r.content, 'html.parser')
   list_of_ids = ["ContentPlaceHolder1_rpRailRidership_rpRailSystemwide_gvRailSYS",
                  "ContentPlaceHolder1_rpRailRidership_rpRailRed_gvRailRed",
                  "ContentPlaceHolder1_rpRailRidership_rpRailBlue_gvRailBlue",
                  "ContentPlaceHolder1_rpRailRidership_rpRailExpo_gvRailExpo",
                  "ContentPlaceHolder1_rpRailRidership_rpRailGreen_gvRailGreen",
                  "ContentPlaceHolder1_rpRailRidership_rpRailGold_gvRailGold"]  
   rider_dataframe = parse_ridership(list_of_ids)
 
   # Now rider dataframe has information about the ridership by line
   # We can now use Pandas to manipulate this data and assign weights

   # This gets just the total_ridership row, which is in the first dataframe in the rider_dataframe list
   sys_ridership = rider_dataframe[0].loc["Total Boardings"].str.replace(",", "").astype(int)
   
   # Now we have total ridership for the month for 3 years (i.e. 2023-2021)
   # We want to consider the proportions for each of the other dataframes, and add this as another row   

   for df_index in range(1, len(rider_dataframe)):
      try:
         rider_dataframe[df_index].loc['Proportion of Total Boardings'] = rider_dataframe[df_index].loc['Total Boardings'].str.replace(",", "").astype(int) / sys_ridership
      except ValueError as e:
         print("ValueError:", e)
         continue
      print(rider_dataframe[df_index])


# Now dataframe of initial url info printed to console
# Now we try to make a post request to get dynamic info 

# sept_url = "https://isotp.metro.net/MetroRidership/YearOverYear.aspx"
# r = requests.get(url=url, headers=headers, verify=False)
# soup = BeautifulSoup(r.content, 'html.parser')
# parse_ridership(list_of_ids)

"""
for month in months:
   payload = {"ctl00%24ContentPlaceHolder1%24rbFYCY": "CY",
              "ctl00$ContentPlaceHolder1$ddlYear:": "2023", 
              "ctl00$ContentPlaceHolder1$ddlPeriod": str(month),
              "ctl00$ContentPlaceHolder1$btnSubmit": "Submit"}
   r = requests.post(url=url, headers=headers, json=payload, verify=False)
      
   soup = BeautifulSoup(r.content, 'html.parser')
   parse_ridership(list_of_ids)
"""
# Selenium usage

driver = webdriver.Chrome()
driver.get("https://isotp.metro.net/MetroRidership/YearOverYear.aspx")

# Month element
element = driver.find_element(By.XPATH, "//select[@name='ctl00$ContentPlaceHolder1$ddlPeriod']")
all_options = element.find_elements(By.TAG_NAME, 'option')
for option in all_options:
   if option not in months:
      print("Value is: %s" % option.get_attribute("value"))
      option.click()
      driver.manage().timeouts().implicitlyWait(5, TimeUnit.SECONDS)
      # alert = driver.switch_to_alert
      # new_url = driver.getCurrentUrl()
      # r = requests.get(url=new_url, headers=headers, verify=False)
      # soup = BeautifulSoup(r.content, 'html.parser')
      # parse_ridership(list_of_ids) 
driver.quit()

