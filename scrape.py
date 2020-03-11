# !/usr/local/bin python3

import requests
import traceback
import random
import smtplib
import re
import json
from pprint import pprint

import datetime
from bs4 import BeautifulSoup
from time import sleep
from lxml.html import fromstring

# Access Env Variables
with open('env.json') as env:
    data = json.load(env)

# List of user agents to use.
user_agent_list = data["userAgents"]


def get_proxies():
    # Get list of proxies

    url = 'https://free-proxy-list.net/'

    # Get response from url and take the page as a string
    response = requests.get(url)
    # Parse the HTML from string form
    parser = fromstring(response.text)
    proxies = []
    # loop through and get all the elite proxies that are available.
    for i in parser.xpath('//tbody/tr')[:]:
        if i.xpath('.//td[7][contains(text(),"yes")]') and i.xpath('.//td[5][contains(text(),"elite proxy")]'):
            proxy = ":".join([i.xpath('.//td[1]/text()')[0],
                              i.xpath('.//td[2]/text()')[0]])
            proxies.append(proxy)
    print(len(proxies))
    return proxies


def new_estimated_date(url):
    # If there is a product that shows when the estimated date the product will be in stock again, then
    # get that date and record it. Email the date.

    # Open file and configure dates
    f = open("arrival.txt", 'r')
    today = datetime.date.today()
    fileContent = f.read()
    f.close()

    # If the last time the file was checked was today, then no need to check again.
    if (fileContent == "Updated estimated arrival " + str(today)):
        print("No need to recheck")
        return

    # Else try to get the date again.
    proxies = get_proxies()
    for i in range(1, len(proxies) - 1):
        # Sleep so not overloading the site and be suspicious
        sleep(5)
        # Pick a random user agent from the list. Then set the header with the user-agent.
        # Header is optional information sent to the site from browser. Headers contain information sent
        # between browser and web server from request and responses. Having a header helps with showing the
        # authenticity of the scrape.
        user_agent = random.choice(user_agent_list)
        headers = {'User-Agent': user_agent}
        # Get the i'th proxy in the list.
        proxy = proxies[i]
        print("Request #%d" % i)
        try:
            # Send a request using proxy and headers to the url and store the response.
            response = requests.get(
                url, proxies={'http': proxy, 'https': proxy}, headers=headers)
            # parse with beautifulsoup
            soup = BeautifulSoup(response.text, 'html.parser')
            print(response)

            # ------------------------------------- Change this depending on website ------------------------------------- #
            # check the tag for the next availability date. Make sure to change the tag you check for each website.
            estimated_date = soup.select("div.iStock-availability")
            # ------------------------------------------------------------------------------------------------------------ #

            print(estimated_date[0].text)
            match = re.search(r":\s(.*)", estimated_date[0].text)
            print(match.group(1))
            print(not not match.group(1))

            # Check for new estimated time of arrival of product.
            f = open("arrival.txt", 'w')
            if match.group(1):
                print("Estimated Date Updated!")
                msg = 'Subject: Estimated Date Updated!\n\n Take a look!'
                send_email(msg)
                f.write("Updated estimated arrival " + str(today))

            else:
                f.write("Updated estimated arrival " + str(today))
            return
        except Exception as e:
            print(e)
            traceback.print_tb(e.__traceback__)


def website_parser(url, proxyDict, headers):
    # Check if the item is sold out or in-stock

    try:
        # Send a request using proxy and headers to the url and store the response.
        response = requests.get(url, proxies=proxyDict, headers=headers)
        print(response)
        soup = BeautifulSoup(response.text, 'html.parser')

        # ------------------------------------- Change this depending on website ------------------------------------- #
        # Select the Add To Cart/Sold Out button
        check_out = soup.select("span#AddToCartText-1034360225835")
        # ------------------------------------------------------------------------------------------------------------ #
        print(check_out[0].text.strip())
        print(check_out[0].text.strip() == "Add to cart")
        print(check_out[0].text.strip() == "Sold Out")
        # Check if the product is available.
        if check_out:
            f = open("data.txt", 'w')

            # If it says "Add to Cart" then send email to notify and update file.
            if check_out[0].text.strip() == "Add to cart":
                print("Success, Item is available")
                msg = 'Subject: Item has arrived!\n\n Lid is here!'
                send_email(msg)
                f.write("Success " + str(datetime.date.today()))

            elif check_out[0].text.strip() == "Sold Out":
                print("Sorry! This item is still sold out")
                f.write("Failure")

            f.close()
            exit(1)
    except Exception as e:
        print("Error occured: ")
        print(e)
        traceback.print_tb(e.__traceback__)


def send_email(msg):
    # Sends email

    smtpObj = smtplib.SMTP("smtp.gmail.com", 587)
    smtpObj.ehlo()
    smtpObj.starttls()
    smtpObj.ehlo()
    # ------------------------------------------ Fill in email details ------------------------------------------ #
    smtpObj.login(data["emailUser"], data["emailPass"])
    smtpObj.sendmail(data["emailUser"],
                     data["emailUser"], msg)
    # ----------------------------------------------------------------------------------------------------------- #
    smtpObj.quit()


def execute_scrape():
    # Main function to scrape.

    # ------------------------------------- Change this depending on website ------------------------------------- #
    url = data["websiteToScrape"]
    # ------------------------------------------------------------------------------------------------------------ #
    print("Processing link: " + url)

    # Open file and configure dates
    f = open("data.txt", 'r')
    today = datetime.date.today()
    fileContent = f.read()
    f.close()
    # Check if there the site has already been checked today and the item has restocked.
    if (fileContent == "Success " + str(today)):
        print("Item has already been confirmed to have restocked today.")
        exit(1)
    # Get proxies
    proxies = get_proxies()
    for i in range(1, len(proxies) - 1):
        sleep(5)
        # Get user agents
        user_agent = random.choice(user_agent_list)
        headers = {'User-Agent': user_agent}
        # set proxy per attempt
        proxy = proxies[i]
        proxyDict = {
            'http': "http://" + proxy,
            'https': "https://" + proxy
        }
        print("Request #%d" % i)

        # new_estimated_date(url)
        website_parser(url, proxyDict, headers)


if __name__ == '__main__':
    execute_scrape()
