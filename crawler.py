import os
import time
import shutil
import urllib
import requests
import seleniumrequests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException   
from selenium.webdriver.support import expected_conditions as EC
import auth
import csv

def dictListToCsv(dict_list):
    keys = dict_list[0].keys()

    with open('profiles.csv', 'w') as output_file:
       dict_writer = csv.DictWriter(output_file, keys)
       dict_writer.writeheader()
       dict_writer.writerows(dict_list)  

def checkElementExists(browser, xpath):
    try:
       browser.find_element_by_xpath(xpath)
    except NoSuchElementException:
        return False

    return True

def findEmail(string):
    string_list = string.split()
    match_list = []

    for word in string_list:
        if "@" in word and "." in word:
            match_list.append(word)
    return match_list

def scrollToPageEnd(browser):
    page_len = browser.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")

    match=False

    while(match==False):
        last_count = page_len
        time.sleep(3)
        page_len = browser.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")

        if last_count==page_len:
            match=True

def SetupChromeDriver(url, download_dir):
    chromeOptions = webdriver.ChromeOptions()
    prefs = {"download.prompt_for_download": False, "download.default_directory" : download_dir, "download.directory_upgrade": True,
     "download.default_content_setting_values.automatic_downloads": 0, "profile.default_content_setting_values.notifications" : 2,
     "Page.setDownloadBehavior": "allow"}
    chromeOptions.add_experimental_option("prefs",prefs)

    # Open Chrome and navigate to Tableau Reports
    chromeOptions.add_argument('--headless')
    chromeOptions.add_argument('--disable-gpu') 
    browser = webdriver.Chrome(executable_path='./chromedriver.exe', chrome_options = chromeOptions)

    browser.get(url)
    return browser

def Login(browser):
    print('Logging in')

    browser.maximize_window()
    username = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, "//input[contains(@name, 'login')]")))
    username.send_keys(auth.username_str)
    print('Entered username')

    password = browser.find_element_by_xpath("//input[contains(@name, 'password')]")
    password.send_keys(auth.password_str)
    print('Entered password')

    loginButton = browser.find_element_by_xpath("//input[contains(@type, 'submit')]")
    loginButton.click()
    print('Logged in')

    time.sleep(5)

def NavigateTab(browser, href):
    #xpath = "//a[@href=" + href + "]"
    xpath = "//a[@href=" + href + "]"
    tab = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, xpath)))
    print(tab.get_attribute("href"))
    tab.click()

    print('Navigated to tab')

    time.sleep(5)

def grabProfiles(browser):
    urls = []
    # scroll to the bottom of the page
    time.sleep(5)

    print('Scrolling profiles...')
    scrollToPageEnd(browser)
    print('Finished scrolling profiles')

    print('Getting profile urls')
    profile_elements = browser.find_elements_by_xpath("//a[contains(@class, 'url boosted-link')]")

    for url in profile_elements:
        urls.append(url.get_attribute("href"))

    with open('urls.txt', 'w') as output_file:
        output_file.write(urls)

    return urls

def grabContacts(browser, profiles):
    arr = []

    print('Navigating to profiles')

    for profile in profiles:
        try:
            profile_dict = dict()

            time.sleep(3)
            browser.get(profile)
            time.sleep(3)

            #browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # get personal website
            website_xpath = "//a[contains(@class, 'elsewhere-website')]"

            if checkElementExists(browser, website_xpath):
                website = browser.find_element_by_xpath(website_xpath).get_attribute("href")
            else:
                website = ''

            # get email
            bio_xpath = "//div[@class='bio']"
            if checkElementExists(browser, bio_xpath):
                bio = browser.find_element_by_xpath(bio_xpath).text
                email = findEmail(bio)
            else:
                email = ''
            

            profile_dict = {"profile": profile, "website" : website, "email": email}
            arr.append(profile_dict)

        except:
            return arr

    print('Finished grabbing profile info')
    return arr


def main():
    base_url = 'https://dribbble.com/session/new'
    download_dir = './'
    href = "'%s'" % "designers" # keep the single quotation marks pls
    browser = SetupChromeDriver(base_url, download_dir)

    Login(browser)
    NavigateTab(browser, href)
    profiles = grabProfiles(browser)
    contacts = grabContacts(browser,profiles)

    browser.quit()
    print('Browser closed')

    dictListToCsv(contacts)

main()