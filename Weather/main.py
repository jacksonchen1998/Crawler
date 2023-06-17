# I want to crawl a website https://www.cwb.gov.tw/V8/E/C/Statistics/monthlydata.html
# It has one select year and one select month
# The main data comes from div class="col-md-12"
# crawl the data and save it to a csv file
# column will be: Date, Station, Average Temperature, Precipitation, Humidity, Wind Speed, Sunshine Duration, Mean Pressure
# Date format: YYYY-MM, from 2010-01 to 2020-12

import requests
from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import csv

# set the year and month
def set_year_month(year, month):
    # set the year
    year_select = driver.find_element_by_id("year")
    year_options = year_select.find_elements_by_tag_name("option")
    for option in year_options:
        if option.text == year:
            option.click()
            break
    # set the month
    month_select = driver.find_element_by_id("month")
    month_options = month_select.find_elements_by_tag_name("option")
    for option in month_options:
        if option.text == month:
            option.click()
            break
    # click the search button
    search_button = driver.find_element_by_id("button")
    search_button.click()
    # wait for the page to load
    time.sleep(random.randint(1, 3))

# get first row data
def get_first_row_data():
    # get the first row data
    first_row = driver.find_element_by_xpath("//div[@class='col-md-12']/table/tbody/tr[1]")
    first_row_data = first_row.find_elements_by_tag_name("td")
    # get the date
    date = first_row_data[0].text
    # get the station
    station = first_row_data[1].text
    # get the average temperature
    average_temperature = first_row_data[2].text
    # get the precipitation
    precipitation = first_row_data[3].text
    # get the humidity
    humidity = first_row_data[4].text
    # get the wind speed
    wind_speed = first_row_data[5].text
    # get the sunshine duration
    sunshine_duration = first_row_data[6].text
    # get the mean pressure
    mean_pressure = first_row_data[7].text
    # return the data
    return date, station, average_temperature, precipitation, humidity, wind_speed, sunshine_duration, mean_pressure

if __name__ == "__main__":
    # set the url
    url = "https://www.cwb.gov.tw/V8/E/C/Statistics/monthlydata.html"
    # set the driver
    driver = webdriver.Chrome()
    driver.get(url)
    # set the year and month
    year = "2010"
    month = "01"
    set_year_month(year, month)
    # get the first row data
    date, station, average_temperature, precipitation, humidity, wind_speed, sunshine_duration, mean_pressure = get_first_row_data()
    # set the data
    data = [date, station, average_temperature, precipitation, humidity, wind_speed, sunshine_duration, mean_pressure]
    # set the csv file
    csv_file = open("weather.csv", "w", newline="")
    writer = csv.writer(csv_file)
    writer.writerow(["Date", "Station", "Average Temperature", "Precipitation", "Humidity", "Wind Speed", "Sunshine Duration", "Mean Pressure"])
    writer.writerow(data)
    csv_file.close()
    # close the driver
    driver.close()