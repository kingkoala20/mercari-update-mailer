from datetime import datetime as dt
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from classes import *
import re

def set_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("disable-infobars")
    options.add_argument("start-maximized")
    options.add_argument("disable-dev-shm-usage")
    options.add_argument("no-sandbox")
    options.add_argument("disable-blink-features=AutomationControlled")

    options.add_experimental_option("excludeSwitches", ["enable-automation"])

    driver = webdriver.Chrome(options=options)
    return driver
        

def scrape_entries(query, status, pages=3, neg=None):
    """
        Scrapes prices according to status

        :param query: search term
        :param status: "sold" or "sale"
        :param pages: Number of pages to scrape
        :param neg: Excluded terms
    """
    orig_query = query[:]
    orig_status = status[:]

    if len(query.split()) != 1: # convert spaces to url code
        query= query.replace(' ','%20')

    if status == 'sold':
        status = 'sold_out'
    elif status == 'sale':
        status = 'on_sale'
    else:
        print ('Error! Invalid Status (check documentation)')
        return None

    url = f'https://jp.mercari.com/search?keyword={query}&status={status}&sort=created_time&order=desc&item_condition_id=3%2C2'
    driver = set_driver()
    driver.get(url)
    time.sleep(2)
    
    entries = []
    while pages > 0:
        
        pages -= 1
        item_list = driver.find_elements(By.XPATH, "//mer-item-thumbnail")
        for entry in item_list:
            title = entry.get_attribute("item-name").lower()
            titleflag = False
            for word in orig_query.split():
                if word not in title:
                    titleflag = True
            if neg:
                for word in neg:
                    if word in title:
                        titleflag = True
            if titleflag:
                continue
            
            price = entry.get_attribute("price")
            src = entry.get_attribute("src")
            link = re.search("m\d+", src).group()
            entries.append(Entry(title, link, price))

        if pages == 0:
            break
            
        try:
            page_bool = driver.find_element(By.XPATH, "//mer-button[@data-testid='pagination-next-button']")           
            page_bool.click()
            time.sleep(3)

        except NoSuchElementException:
            break
    return orig_query, orig_status, entries

def scrape_average_sold(query, pages=3, neg=None):
    orig_query, orig_status, entries = scrape_entries(query, "sold", pages=pages, neg=neg)
    prices = []
    for e in entries:
        prices.append(e._price)
    now = dt.now()
    now = now.strftime("%Y-%m-%d, %H:%M")
    
    return orig_query, orig_status, now, round(sum(prices)/len(prices))
        
def scrape_head(query, n = 15, pages=1, neg=None):
    entries = scrape_entries(query, "sale", pages=pages, neg=neg)[2][:n+1]
    return entries

def parse_head(query, neg=None):
    entries = scrape_head(query, neg=neg)
    code = ''
    for e in entries:
        code += str(e._link[-1])
    return code

if __name__ == "__main__":
    #scrape_entries("ddj-400","sale", neg="箱", pages=1)
    #scrape_average_sold("xdj-rx")
    scrape_head("xdj-rx")
    