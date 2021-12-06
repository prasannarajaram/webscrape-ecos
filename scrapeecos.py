from bs4 import BeautifulSoup as soup
from selenium import webdriver
import pandas as pd
import time
import requests
import re
import pdb

driver = webdriver.Chrome()

MAIN_URL = "https://www.ecos.com/all-products-page/"
CSV_FILE = 'EcosIngredients.csv'
driver.get(MAIN_URL)
time.sleep(5)

html = driver.page_source
driver.close();  # Close the webpage after getting page source

parsed_html = soup(html, "html.parser")

categoryResults = parsed_html.find("div", {"id" : "categoryResults"})
hrefs = categoryResults.find_all('a', href=True)
urls = []
for href in hrefs:
    urls.append(href['href'])

table = pd.DataFrame()

for url in urls:
    try:
        h1 = soup(requests.get(url).content, "lxml").find("h1").text
        content = pd.DataFrame()
        content = pd.read_html(requests.get(url).content)[-1]
        content = content[[0,1,2]]
        content = content.rename(columns=content.iloc[0]).drop(content.index[0])
        content = content.rename(columns = {'CAS#  (list al CAS# if material is a blend)':'CAS#'})
        content = content.rename(columns = {'CAS# (list al CAS# if material is a blend)':'CAS#'})
        record_count = len(content)
        url_col = [url for _ in range(record_count)]
        heading_col = [h1 for _ in range(record_count)]
        urlseries = pd.Series(data=url_col)
        content['product page URL'] = urlseries.values
        headingseries = pd.Series(data=heading_col)
        content['product name'] = headingseries.values
        cols = content.columns.to_list()
        table = table.append(content)
    except ValueError:
        content = pd.DataFrame({'Chemical Name' : [''],
                                 'CAS#' : [''],
                                 'Function' : [''],
                                 'product page URL' : [url],
                                 'product name' : [h1]})
        table = table.append(content)

table.to_csv(CSV_FILE, header=True, index=False)
