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
            username = credentials["username"]
            password = credentials["password"]
        
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
        # enter and search the search term
        job_search_input = self.driver.find_element(By.CSS_SELECTOR, "[role='combobox']")
        job_search_input.send_keys(search_term)
        job_search_input.send_keys(Keys.RETURN)

        # slowly get to the links page
        time.sleep(3)
        main = scraper.driver.find_element(By.CSS_SELECTOR, "div[class='application-outlet']")
        main2 = main.find_element(By.CSS_SELECTOR, "div[class='scaffold-layout__list ']")
        main3 = main2.find_element(By.CSS_SELECTOR, "ul[class='scaffold-layout__list-container']")

        # scrape the links
        links = []
        postings = main3.find_elements(By.XPATH, "./li")
        for posting in postings:
            try:
                posting_link = posting.find_element(By.TAG_NAME, "a")
                links.append(posting_link.get_attribute("href"))
            except Exception as e:
                pass

        return links


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
        description = posting_main.find_elements(By.XPATH, "./div")[3].text

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


        # scrape links for each search term
        scraper.search_url("https://www.linkedin.com/jobs/")
        links = {}
        for search_term in search_terms:
            links[search_term] = self.get_job_posting_links(search_term)

        # scrape data from all of the links
        posting_details = {}
        for search_term in links:
            posting_details[search_term] = []
            for link in links[search_term]:
                try:
                    details = self.scrape_post(link)
                    posting_details[search_term].append(details)
                except:
                    pass
        
        # save all scraped data
        with open("data/linkedin_scraped_posts.json", "w") as f:
            json.dump(posting_details, f, indent=4)


if __name__ == "__main__":
    # initialize a linkedin scraper
    scraper = LinkedinScraper("./chromedriver_mac")

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
    scraper.scrape_linkedin([search_terms[0]])
    

    