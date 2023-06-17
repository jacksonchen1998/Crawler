# I want to crawl a website https://www.cwb.gov.tw/V8/E/C/Statistics/monthlydata.html
# It has one select year and one select month
# The main data comes from div class="col-md-12"
# crawl the data and save it to a csv file
# column will be: Date, Station, Average Temperature, Precipitation, Humidity, Wind Speed, Sunshine Duration, Mean Pressure
# Date format: YYYY-MM, from 2010-01 to 2020-12

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import csv
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# set the year and month
def set_year_month(year, month):
    # set the year
    year_select = driver.find_element("id", "Year")
    # get the options value
    year_options = year_select.find_elements(By.TAG_NAME, "option")
    for i in range(len(year_options)):
        if year_options[i].text == year:
            year_options[i].click()
    
    # Wait for the element to become stable
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "Month")))

    # set the month
    month_select = driver.find_element("id", "Month")
    # get the options value
    month_options = month_select.find_elements(By.TAG_NAME, "option")
    for i in range(len(month_options)):
        #print(month_options[i].text)
        if month_options[i].text == month:
            month_options[i].click()
    # sleep for 0.2 second
    #time.sleep(10)
    

# get the data from table id="MonthlyData_MOD"
# header H-1 subH-2: mean_temperature
# header H-2 subH-5: precipitation
# header H-4 subH-8: humidity
# header H-7 subH-12: sunshine_duration
# header H-3 subH-6: max_wind_speed
# skip first row

def get_data():
   # find the table
    table = driver.find_element("id", "MonthlyData_MOD")
    # get the table header
    table_header = table.find_elements(By.TAG_NAME, "th")
    # get the table data
    table_data = table.find_elements(By.TAG_NAME, "td")
    # get the station
    station = table_header[0].text
    # get the average temperature
    average_temperature = table_data[0].text
    

if __name__ == "__main__":
    # set the url
    url = "https://www.cwb.gov.tw/V8/E/C/Statistics/monthlydata.html"
    # set the driver
    driver = webdriver.Chrome()
    driver.get(url)
    # create csv file called weather.csv
    with open("weather.csv", "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Date", "Station", "Average Temperature", "Precipitation", "Humidity", "Wind Speed", "Sunshine Duration", "Mean Pressure"])
    
    year = ["2010", "2011", "2012", "2013", "2014", "2015", "2016", "2017", "2018", "2019", "2020"]
    month = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10" ,"11", "12"]

    for i in range(len(year)):
        for j in range(len(month)):
            set_year_month(year[i], month[j])
            station, average_temperature, precipitation, humidity, wind_speed, sunshine_duration, mean_pressure = get_data()
            # save the data to csv file
            with open("weather.csv", "a", newline="") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([year[i] + "-" + month[j], station, average_temperature, precipitation, humidity, wind_speed, sunshine_duration, mean_pressure])
            # sleep for 0.2 second
            time.sleep(0.2)