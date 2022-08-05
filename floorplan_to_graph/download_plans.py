#!pip install selenium
#!pip install chromedriver - make sure the versions of chromium and chromedriver match
from selenium.webdriver import Chrome
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time

download_dir = "/Users/yajva/Documents/pdfscraper"  # where the pdf files are gonna go
options = webdriver.ChromeOptions()
options.add_experimental_option('prefs', {
"download.default_directory": download_dir, #Change default directory for downloads
"download.prompt_for_download": False, #To auto download the file
"download.directory_upgrade": True,
"plugins.always_open_pdf_externally": True #It will not show PDF directly in chrome
})
wd = Chrome(executable_path="/Users/yajva/Downloads/chromedriver",chrome_options=options) # initialize Selenium Webdriver. Will need to replace with your own chromedriver path

wd.get("https://floorplans.mit.edu/searchPDF.asp") # get the central URL with building list

time.sleep(20) # time to sign in manually (need Touchstone authentication to access the website)

soup = BeautifulSoup(wd.page_source, 'lxml')
building_list = soup.find("select",attrs={'name':'Bldg'})
buildings = [f.text.strip() for f in building_list.find_all("option")] # gather list of buildings

for b in buildings:
    wd.get("https://floorplans.mit.edu/ListPDF.Asp?Bldg=" + b) # navigate to page with building floor plans
    time.sleep(2) # wait for page to load
    floors = wd.find_element(By.XPATH, "//div[@id='maincontent']").find_elements(By.XPATH, "//a[@target='_Blank']") 
    for f in floors:
        f.click() # download floor plan
        time.sleep(2) # wait for page to laod
    
