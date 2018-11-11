#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import time
import os
import re
import requests
from io import BytesIO
from selenium import webdriver  # pip install selenium
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup  # pip install beautifulsoup4
from lxml import html  # pip install lxml
from PIL import Image  # pip install pillow

USER_AGENT = 'WebCrawler-Py500'

# ATTENTION!, you may need to tune this depending on your Internet connection
REFRESH_TIME = 2.5
DELAY_TIME = 0.5

TARGET_URL = 'http://fortune.com/fortune500/list/'
BASE_URL = 'http://www.fortune.com'


def download(url):
    print('Downloading:', url)
    headers = {'User-agent': USER_AGENT}
    try:
        request = requests.get(url, headers)
        html_data = request.content
    except requests.exceptions.RequestException as e:
        print('Download error:', e)
        html_data = None
    return html_data


def main():

    # Selenium WebDriver configuration
    profile = webdriver.FirefoxProfile()  # Use Firefox as driver
    # Set the user agent to identify us
    profile.set_preference('general.useragent.override', USER_AGENT)
    # Set the volume to zero to avoid annoying ads
    profile.set_preference('media.volume_scale', '0.0')

    driver = webdriver.Firefox(profile)  # Set profile

    driver.get(TARGET_URL)  # Open the target URL
    # Press the Continue button to close the cookies warning and show the entire page
    driver.find_element_by_id('meredithGdprConsentFormButton').click()

    # Refresh the page and wait a while for the dynamic list to load correctly
    time.sleep(REFRESH_TIME)
    driver.refresh()
    time.sleep(REFRESH_TIME)

    last_height = driver.execute_script(
        'return document.body.scrollHeight')  # Get the current height of page

    # Scroll down the entire page to load the lazy list
    while True:
        driver.execute_script(
            'window.scrollTo(0, document.body.scrollHeight);')  # Scroll to bottom of the page
        time.sleep(REFRESH_TIME)

        new_height = driver.execute_script('return document.body.scrollHeight')
        if new_height == last_height:  # When the page stops growing stop the scroll
            break
        last_height = new_height

    # Load the page source and close the driver
    page_html = driver.page_source
    driver.close()

    # Open file in write mode to save the data
    f1 = open('./fortune500.csv', '+w')

    # Write the CSV header
    f1.write(
        'rank;title;revenue;ceo;position;sector;industry;hq;website;years;employees;image\n')

    # Make dir to save the images
    if not os.path.exists('./img/'):
        os.makedirs('./img/')

    # Parse the page source html with BeautifulSoup
    soup = BeautifulSoup(page_html, 'html.parser')
    # Get the company list
    company_list = soup.find('ul', {'class': 'company-list'}).find_all('li')

    index = 1
    total = len(company_list)
    for company in company_list:

        # Initialize the varaibles
        rank = title = revenue = ceo = position = industry = hq = website = years = employees = img_name = 'NA'

        img_file = img_path = img_url = None

        try:
            rank = company.find('span', {'class': 'company-rank'}).text
            title = company.find('span', {'class': 'company-title'}).text
            revenue = company.find('span', {'class': 'company-revenue'}).text
        except:
            print('Error processing the company!')

        try:
            # Collect data related to the company from the record in fortune page
            company_url = company.find('a')['href']
            html_data = download(BASE_URL + company_url)

            # Parse the html data of the record page with lxml tree
            tree = html.fromstring(html_data)

            # We use the xpath locator to find the attributes we want and bypass the React dynamic IDs
            ceo = tree.xpath(
                '//*[@id="pageContent"]/div[2]/div[5]/div[1]/div[1]/div/div[1]/div[2]/div[1]/div[1]/div/p/text()')[0]
            position = tree.xpath(
                '//*[@id="pageContent"]/div[2]/div[5]/div[1]/div[1]/div/div[1]/div[2]/div[1]/div[2]/div/p/text()')[0]
            sector = tree.xpath(
                '//*[@id="pageContent"]/div[2]/div[5]/div[1]/div[1]/div/div[1]/div[2]/div[1]/div[3]/div/p/text()')[0]
            industry = tree.xpath(
                '//*[@id="pageContent"]/div[2]/div[5]/div[1]/div[1]/div/div[1]/div[2]/div[1]/div[4]/div/p/text()')[0]
            hq = tree.xpath(
                '//*[@id="pageContent"]/div[2]/div[5]/div[1]/div[1]/div/div[1]/div[2]/div[1]/div[5]/div/p/text()')[0]
            website = tree.xpath(
                '//*[@id="pageContent"]/div[2]/div[5]/div[1]/div[1]/div/div[1]/div[2]/div[1]/div[6]/div/a/text()')[0]
            years = tree.xpath(
                '//*[@id="pageContent"]/div[2]/div[5]/div[1]/div[1]/div/div[1]/div[2]/div[1]/div[7]/div/p/text()')[0]
            employees = tree.xpath(
                '//*[@id="pageContent"]/div[2]/div[5]/div[1]/div[1]/div/div[1]/div[2]/div[1]/div[8]/div/p/text()')[0]
            img_url = tree.xpath(
                '//*[@id="image-background"]/picture/source[1]/@srcset'
            )[0]
        except:
            print('Error downloading company record!')

        try:
            img_file = img_url.split('/')[5]
            img_path = './img/' + img_file
            img_name = img_file.split('.')[0]

            # Sleep to avoid being blocked
            time.sleep(DELAY_TIME)

            # Download and write the image
            img_bytes = download(img_url)

            # Reduce the image size to avoid large files
            image = Image.open(BytesIO(img_bytes))
            image = image.resize((960, 540), Image.ANTIALIAS)
            # Also can set the image quality
            # image.save(img_path, 'JPEG', quality=10)
            image.save(img_path, 'JPEG')
        except:
            print('Error downloading the image!')
            img_name = 'NA'

        print('Downloaded %d of %d...' % (index, total))
        print('> Rank: ', rank)
        print('> Title: ', title)
        print('> Revenue: ', revenue)
        print('> CEO: ', ceo)
        print('> Position: ', position)
        print('> Sector: ', sector)
        print('> Industry: ', industry)
        print('> HQ: ', hq)
        print('> Website: ', website)
        print('> Years: ', years)
        print('> Employees: ', employees)
        print('> Image: ', img_name)

        # Sleep to avoid being blocked
        time.sleep(DELAY_TIME)

        # Write CSV record
        line = rank + ';' + title + ';' + revenue + ';' + ceo + ';' + position + ';' + \
            sector + ';' + industry + ';' + hq + ';' + website + \
            ';' + years + ';' + employees + ';' + img_name + ';' + '\n'
        f1.write(line)

        index += 1

    f1.close


if __name__ == '__main__':
    main()
