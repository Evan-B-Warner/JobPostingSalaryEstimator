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


    def __init__(self, webdriver_path):
        service = Service(executable_path=webdriver_path)
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        self.driver = webdriver.Chrome(service=service, options=options)
    

    def search_url(self, url):
        """Navigates to the specified URL

        """
        self.driver.get(url)



class LinkedinScraper(JobPostingScraper):


    def login(self, credentials_path):
        """Logs in to Linkedin

        """
        # read credentials from file
        with open(credentials_path) as f:
            credentials = json.load(f)
            username = credentials["Username"]
            password = credentials["Password"]
        
        # input credentials and sign in
        username_input = self.driver.find_element(By.ID, "session_key")
        username_input.send_keys(username)
        password_input = self.driver.find_element(By.ID, "session_password")
        password_input.send_keys(password)
        sign_in_button = self.driver.find_element(By.CSS_SELECTOR, "[data-id='sign-in-form__submit-btn']")
        sign_in_button.click()
    

    def get_job_posting_links(self, search_term, num_posts=20):
        """Scrapes `num_posts` links of job posting results from 
        
        the specified search term
        """
        # linkedin sometimes uses a different ID for the job search
        try:
            job_search_input = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.ID, "jobs-search-box-keyword-id-ember27"))
            )
        except:
            job_search_input = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.ID, "jobs-search-box-keyword-id-ember28"))
            )
        
        # enter and search the search term
        job_search_input.send_keys(search_term)
        job_search_input.send_keys(Keys.RETURN)

        # scrape the links
        posting_list = self.driver.find_elements(By.TAG_NAME, "ul")
        for i in range(len(posting_list)):
            print('POSTING LIST', i, posting_list[i])
        return []
    

    def scrape_post(self, url):
        """Given a job posting url, scrapes all relevant information and

        returns it in a dictionary
        """
        # navigate to the post url
        self.search_url(url)
        time.sleep(3)

        # expand job description
        self.driver.find_element(By.CSS_SELECTOR, "[aria-label='Click to see more description']").click()

        # go to main card
        posting_main = self.driver.find_element(By.CSS_SELECTOR, "[role='main']")
        title_css = "h1[class='t-24 t-bold job-details-jobs-unified-top-card__job-title']"
        details_css = "div[class='job-details-jobs-unified-top-card__primary-description-without-tagline mb2']"
        salary_css = "li[class='job-details-jobs-unified-top-card__job-insight job-details-jobs-unified-top-card__job-insight--highlight']"
        description_css = "div[id='ember112']"

        # scrape job details
        title = posting_main.find_element(By.CSS_SELECTOR, title_css).text
        job_more_info = posting_main.find_element(By.CSS_SELECTOR, details_css).text
        employer, location, application_length, num_applicants = job_more_info.split("·")
        salary = posting_main.find_element(By.CSS_SELECTOR, salary_css).text
        description = posting_main.find_elements(By.XPATH, "./div")[3]

        # format scraped details
        job_details = {
            "title": title,
            "employer": employer.strip(),
            "location": location.strip(),
            "num_applicants": num_applicants.strip(),
            "salary": salary,
            "description": description,
            "url": url
        }

        return job_details
    

    def scrape_linkedin(self, search_terms):
        """Scrapes job posting data for each of the given search terms

        """
        # navigate to and login to linkedin
        scraper.search_url("https://www.linkedin.com/")
        time.sleep(3)
        scraper.login("linkedin_credentials.json")
        #time.sleep(999)


        # scrape links for each search term
        links = {}
        for search_term in search_terms:
            links[search_term] = self.get_job_posting_links(search_term)

        # scrape data from all of the links
        posting_details = {}
        for search_term in links:
            posting_details[search_term] = []
            for link in links:
                posting_details.append(self.scrape_post(link))
        
        # save all scraped data
        with open("data/linkedin_scraped_posts.json", "w") as f:
            json.dump(posting_details, f, indent=4)

        



if __name__ == "__main__":
    # initialize a linkedin scraper
    scraper = LinkedinScraper("./chromedriver_windows")

    # scrape job postings
    search_terms = [
        "Data Scientist", 
        "Data Analyst", 
        "Financial Analyst", 
        "AI Engineer", 
        "AI Developer", 
        "Backend Developer",
        "Software Engineer",
        "Software Developer",
        "Frontend Developer",
        "Full Stack Developer"
    ]
    scraper.scrape_linkedin(search_terms)


    #scraper.scrape_post("https://www.linkedin.com/jobs/view/3835957961/?eBP=CwEAAAGOiq8Cld0GTKk-P7Ydfjd9FUU8Z9q_j_eHQE8XjfuHIxTMp_HRCuHs1ncd3RqEGZOjsxrDs4JD_9BvQXSLkjBhKiAjrtKwGkQYRI-inU4CXdUXRJiC3G0F7fXFkYhvLwYHHiGI7SPUD9vode0bAlbq3xUkQyIUNoD-4NDwRIAZEG-E9nf2JdNitNijx9ERHeWwDjtR_5TCftrtcbbC1IYaegSPbPvqFs5oky42lQYxs8l4JU10-GjV-2JWyLYwYtHzquUstg8SJ4ajhzTTxqPt_5rOkpDobl33PkkMs7jwYNt099Nq6cxXCnRvOtUsLYGhYazaY_MqPH7jPG11jpDDFy1GqR7MpSn0YL0FYPAFeRPC25jr8ldLzxNTyBmn_x5bo8H7w8Sopbvg0LH9S-OusqNEZXG1_Cl0czL4uU-YUccUd1Aw&refId=s2dOCZm0x7UQBJcytPyi5g%3D%3D&trackingId=aIgrBwiACEkmlZuNUuqmEg%3D%3D&trk=flagship3_search_srp_jobs")
    #time.sleep(999)