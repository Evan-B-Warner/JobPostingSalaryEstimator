import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import numpy as np
import pandas as pd


class JobPostingScraper(object):


    def __init__(self):
        pass
    



if __name__ == "__main__":
    service = Service(executable_path='./chromedriver')
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=service, options=options)

    log = open('logging.txt', 'w')


    # go to linkedin
    driver.get("https://www.linkedin.com/")
    time.sleep(3)
    log.write("got to linkedin\n")

    # log in
    with open("linkedin_credentials.json") as f:
        credentials = json.load(f)
        username = credentials["Username"]
        password = credentials["Password"]
    username_input = driver.find_element(By.ID, "session_key")
    username_input.send_keys(username)
    password_input = driver.find_element(By.ID, "session_password")
    password_input.send_keys(password)
    sign_in_button = driver.find_element(By.CSS_SELECTOR, "[data-id='sign-in-form__submit-btn']")
    sign_in_button.click()
    log.write("signed in\n")
    
    # go back to jobs page
    driver.get("https://www.linkedin.com/jobs/")
    time.sleep(5)
    log.write("went to jobs page\n")    

    # make the job search
    job_search_input = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.ID, "jobs-search-box-keyword-id-ember27"))
    )
    job_search_input.send_keys("Data Scientist")
    job_search_input.send_keys(Keys.RETURN)
    log.write("searched jobs\n")

    # job list panel
    time.sleep(5)
    posting_panels = driver.find_elements(By.TAG_NAME, "ul")
    log.write("found posting panels\n")

    c = 0
    for posting_panel in posting_panels:
        print(c)
        c += 1
        postings = posting_panel.find_elements(By.TAG_NAME, "li")
        for posting in postings:
            links = posting.find_elements(By.TAG_NAME, "a")
            if len(links):
                for link in links:
                    print(link.get_attribute("href"))

    log.close()
    #time.sleep(999)