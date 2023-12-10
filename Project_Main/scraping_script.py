from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
import requests
import pandas as pd
from bs4 import BeautifulSoup
from collections import defaultdict

# Methods
def parse_ridership(list_of_ids, soup):
   """
   This method takes in a list of the ids corresponding to the ridership of the rail systems on the LA Metro,
   and parses them via BeautifulSoup
   """
   dataframes_by_line = []
   for table_id in list_of_ids:

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

def selenium_driver(month: str, year: str, list_of_ids: list):
   """
   This method takes in a month and year, and uses it as input to submit a form on the LA Metro ridership website
   This returns a dataframe which contains the ridership information, as well as the weighted importance of each line
   by year when possible

   The LA Metro website stores the data for all three years including the year passed in (eg."2023" will provide information
   for 2022 and 2021 as well)
   """
   # Preliminary input checking
   if type(month) != str and type(year) != str:
      return "ValueError: Month and year must be a string"
   if int(year) >= 2024 or int(year) < 2009:
      return "Year must be between 2009 and 2023"
   if int(year) == 2023:
      if month == "November" or month == "December":
         return "Month must be October or earlier for the year 2023"

   driver = webdriver.Chrome()
   driver.get("https://isotp.metro.net/MetroRidership/YearOverYear.aspx")

   # Month element
   month_element_tag = driver.find_element(By.XPATH, "//select[@name='ctl00$ContentPlaceHolder1$ddlPeriod']")
   month_options = month_element_tag.find_elements(By.TAG_NAME, 'option')

   for option in month_options:
      month_val = option.text
      if month_val == month:
         option.click()
         break
   
   # Year element
   year_element_tag = driver.find_element(By.XPATH, "//select[@name='ctl00$ContentPlaceHolder1$ddlYear']")
   year_options = year_element_tag.find_elements(By.TAG_NAME, 'option')

   for option in year_options:
      year_val = option.text
      if year_val == year:
         option.click()
         break
   
   # Navigate to submit button
   driver.find_element(By.ID, "ContentPlaceHolder1_btnSubmit").click()

   soup = BeautifulSoup(driver.page_source, 'html.parser')
   rider_dataframes = parse_ridership(list_of_ids, soup)

   # Now rider dataframe has information about the ridership by line
   # We can now use Pandas to manipulate this data and assign weights

   # This gets just the total_ridership row, which is in the first dataframe in the rider_dataframe list
   try:
      sys_ridership = rider_dataframes[0].loc["Total Boardings"].str.replace(",", "").astype(int)
   except ValueError:
      return f"No ridership data for {month} {year}"
   # Now we have total ridership for the month for 3 years (i.e. 2023-2021)
   # We want to consider the proportions for each of the other dataframes, and add this as another row

   for df_index in range(1, len(rider_dataframes)):
      try:
         rider_dataframes[df_index].loc['Proportion of Total Boardings'] = rider_dataframes[df_index].loc['Total Boardings'].str.replace(",", "").astype(int) / sys_ridership
      except ValueError as e:
         pass
   time.sleep(3)
   driver.quit()
   return rider_dataframes

if __name__ == "__main__":
   list_of_ids = ["ContentPlaceHolder1_rpRailRidership_rpRailSystemwide_gvRailSYS",
                  "ContentPlaceHolder1_rpRailRidership_rpRailRed_gvRailRed",
                  "ContentPlaceHolder1_rpRailRidership_rpRailBlue_gvRailBlue",
                  "ContentPlaceHolder1_rpRailRidership_rpRailExpo_gvRailExpo",
                  "ContentPlaceHolder1_rpRailRidership_rpRailGreen_gvRailGreen",
                  "ContentPlaceHolder1_rpRailRidership_rpRailGold_gvRailGold"]
   
   # For our purposes, we will consider data for January - March 2023
   # We can enter many months within a given calendar year
   months = input("Enter month for ridership data: ").split()
   year_input = input("Enter year for ridership data: ")
  
   for month in months: 
      list_of_dataframes = selenium_driver(month, year_input, list_of_ids)
      if type(list_of_dataframes) != str:
         print(f"Ridership for {month} {year_input}")
         print(list_of_dataframes)
      
         for index, dataframe in enumerate(list_of_dataframes):
            rail_line = list_of_ids[index].split("_")[-1]
            dataframe.to_csv(rail_line+month+year_input+'.csv')
      else:
         print(list_of_dataframes)

