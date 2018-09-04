#!/usr/bin/env python3

""" Here I parse a web page (25 Newest items at IKEA) into a data file (csv) using a Python package called BeautifulSoup.
By Adam Rhys Heaton 
Date 9/4/2018 """

import bs4

from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup

#URL to the 25 Newest items at IKEA
my_url = 'https://www.ikea.com/us/en/catalog/news/departments/'

# opening connection to the webpage
uClient = uReq(my_url)
page_html = uClient.read()
uClient.close()

# html parsing
page_soup = soup(page_html, "html.parser")

#grabs each product
containers = page_soup.findAll(
    "div", {"class": "parentContainer"})

# filename 
filename = "items.csv"
f = open(filename, "w")

# formating csv file
headers = "item_status, item_name, item_desc, item_price \n"
f.write(headers)

# scraping data from webpage for csv file
for container in containers:
    item_status = container.span.text.strip()
    item_name = container.div.span.text.strip()
    item_desc = container.div.h2.div.text.strip()
    item_price = container.findAll("span", {"class": "prodPrice"})
    price = item_price[0].text.replace("\r\n\t\t\t\t \xa0", "").strip()

#output to terminal/IDLE
    print("Status: " + item_status)
    print("Name: " + item_name)
    print("Description: " + item_desc)
    print("Unit Price: " + price)

# writing to csv file   
    f.write(item_status  + "," + item_name + "," + item_desc.replace(","," /")
            + "," + price + "\n")
#closing file
f.close()
