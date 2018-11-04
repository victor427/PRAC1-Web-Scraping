#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import time
import os
from selenium import webdriver  # pip install selenium
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup  # pip install beautifulsoup4

DELAY_TIME = 2.5

def main():
    profile = webdriver.FirefoxProfile()
    profile.set_preference('general.useragent.override', 'webcrawler-500')
    
    driver = webdriver.Firefox(profile)
    driver.get('http://fortune.com/fortune500/2017/list/')

    driver.find_element_by_id('meredithGdprConsentFormButton').click()

    time.sleep(DELAY_TIME)
    driver.refresh()
    time.sleep(DELAY_TIME)

    last_height = driver.execute_script('return document.body.scrollHeight')
    
    while True:
        driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
        time.sleep(DELAY_TIME)

        new_height = driver.execute_script('return document.body.scrollHeight')
        if new_height == last_height:
            break
        last_height = new_height
    
    html = driver.page_source
    driver.close()

    f1 = open('./fortune500.csv', '+w')
    f1.write('rank;title;revenue;ceo;title;sector;industry;hq;website;years;employees\n')
    soup = BeautifulSoup(html, 'html.parser')
    company_list = soup.find('ul', {'class': 'company-list'})
    for company in company_list.find_all('li'):
        rank = company.find('span', {'class': 'company-rank'}).text
        title = company.find('span', {'class': 'company-title'}).text
        revenue = company.find('span', {'class': 'company-revenue'}).text
        print('rank:', rank)
        print('title:', title)
        print('revenue:', revenue)
        print('------------------')
        line = rank + ';' + title + ';' + revenue + ';' + 'NA' + ';' + 'NA' + ';' + 'NA' + ';' + 'NA' + ';' + 'NA' + ';' + 'NA' + ';' + 'NA' + ';' + 'NA' + ';' + '\n'
        f1.write(line)

    f1.close

if __name__ == '__main__':
    main()