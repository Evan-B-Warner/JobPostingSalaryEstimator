import time
import json
from tqdm import tqdm
from selenium import webdriver
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import numpy as np
import pandas as pd


def salary_string2annual(salary):
    try:
        amount = salary.split("/")[0].split("$")[-1].replace("$", "")
        if "K" in amount:
            amount = amount.replace("K", "")
            amount = float(amount)*1000
        amount = float(amount)
        term = salary.split("/")[1].split(" ")[0]
        if term == 'hr':
            amount = amount*2000
    except Exception as e:
        amount = salary
    return amount


class JobPostingScraper(object):


    def __init__(self, webdriver_path, headless=True, undetected=False):
        service = Service(executable_path=webdriver_path)
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        if headless:
            options.add_argument("--headless=new")
        if undetected:
            self.driver = uc.Chrome(service=service, options=options)
        else:
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
    

    def get_job_posting_links(self, search_term):
        """Scrapes links of job posting results from
        
        the specified search term
        """
        # enter and search the search term
        print("Scraping search term:", search_term)
        job_search_input = self.driver.find_element(By.CSS_SELECTOR, "[role='combobox']")
        job_search_input.send_keys(search_term)
        job_search_input.send_keys(Keys.RETURN)

        # iterate through first 8 pages
        links = []
        print("Scraping links...")
        for i in tqdm(range(8)):
            # slowly get to the links page
            time.sleep(3)
            main = scraper.driver.find_element(By.CSS_SELECTOR, "div[class='application-outlet']")
            main2 = main.find_element(By.CSS_SELECTOR, "div[class='scaffold-layout__list ']")
            main3 = main2.find_element(By.CSS_SELECTOR, "ul[class='scaffold-layout__list-container']")

            # scrape the links
            postings = main3.find_elements(By.XPATH, "./li")
            for posting in postings:
                # scroll to the posting so the link loads
                self.driver.execute_script("arguments[0].scrollIntoView(true);", posting)
                try:
                    posting_link = posting.find_element(By.TAG_NAME, "a")
                    link = posting_link.get_attribute("href")
                    if link not in links:
                        links.append(link)
                except Exception as e:
                    pass
            
            # navigate to the next page
            try:
                time.sleep(3)
                next_page_button = self.driver.find_element(By.CSS_SELECTOR, f"li[data-test-pagination-page-btn='{i+2}']")
                next_page_button.click()
            except:
                pass

        print("Scraped", len(links), "links")
        return links


    def scrape_post(self, url):
        """Given a job posting url, scrapes all relevant information and

        returns it in a dictionary
        """
        # navigate to the post url
        self.search_url(url)
        time.sleep(2)

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
        description = posting_main.find_elements(By.CSS_SELECTOR, "[tabindex='-1']")[4].text

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
        time.sleep(2)
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
            print("Scraping Posts for", search_term + "...")
            for link in tqdm(links[search_term]):
                try:
                    details = self.scrape_post(link)
                    posting_details[search_term].append(details)
                except Exception as e:
                    pass
        
        # save all scraped data
        with open("data/linkedin_scraped_posts.json", "w") as f:
            json.dump(posting_details, f, indent=4)



class GlassDoorScraper(JobPostingScraper):

    def login(self, credentials_path):
        """Logs in to GlassDoor

        """
        # read credentials from file
        with open(credentials_path) as f:
            credentials = json.load(f)
            username = credentials["username"]
            password = credentials["password"]

        # click on sign in with google
        time.sleep(3)
        self.driver.find_element(By.CSS_SELECTOR, "button[data-test='googleBtn'").click()

        # switch window focus to google sign in pop-up tab
        window_handles = self.driver.window_handles
        for handle in window_handles:
            if handle != self.driver.current_window_handle:
                self.driver.switch_to.window(handle)
        
        # input credentials and sign in
        time.sleep(5)
        email_input = self.driver.find_element(By.CSS_SELECTOR, "input[type='email']")
        email_input.send_keys(username)
        email_input.send_keys(Keys.RETURN)
        time.sleep(5)
        password_input = self.driver.find_element(By.CSS_SELECTOR, "input[type='password']")
        password_input.send_keys(password)
        password_input.send_keys(Keys.RETURN)
        time.sleep(5)
        continue_button = self.driver.find_elements(By.CSS_SELECTOR, "div[jsname='xivUjb']")[1]
        continue_button.click()

        # switch window back to main glassdoor tab
        window_handles = self.driver.window_handles
        self.driver.switch_to.window(window_handles[0])
    

    def scrape_salary_by_title_and_employer(self, title, employer):
        """Scrapes the estimated salary for a title and employer combination
        
        """
        # go to search url
        scraper.search_url("https://www.glassdoor.ca/Salaries/know-your-worth.htm")
        time.sleep(3)

        # fill in job title and employer name, and search
        title = title.split("/")[0]
        title_input = self.driver.find_element(By.CSS_SELECTOR, "input[name='jobTitleAutocomplete']")
        title_input.send_keys(title)
        employer_input = self.driver.find_element(By.CSS_SELECTOR, "input[name='employerAutocomplete']")
        employer_input.send_keys(employer)
        time.sleep(2)
        employer_autofill = self.driver.find_elements(By.CSS_SELECTOR, "ul[class='suggestions down']")[2]
        autofill_option = employer_autofill.find_element(By.TAG_NAME, 'li')
        autofill_option.click()
        search_button = self.driver.find_element(By.CSS_SELECTOR, "button[data-test='salaries-landing-page-search-btn']")
        search_button.send_keys(Keys.RETURN)

        # scrape salary range if it exists
        try:
            salary_range = self.driver.find_element(By.CSS_SELECTOR, "div[class='hero_TotalPayLayout__jkrO9 hero_PayRange__CLL2w']")
            divs = salary_range.find_elements(By.CLASS_NAME, "hero_PayRange__CLL2w")
            lower, upper = divs[0].text + "/yr", divs[1].text
            return (salary_string2annual(lower) + salary_string2annual(upper))/2
        except:
            return -1

    
    def scrape_salary_by_title(self, title, employer):
        """Scrapes the estimated salary for a title
        
        """
        # go to search url
        scraper.search_url("https://www.glassdoor.ca/Salaries/know-your-worth.htm")
        time.sleep(3)

        # fill in job title and search
        title = title.split("/")[0]
        title_input = self.driver.find_element(By.CSS_SELECTOR, "input[name='jobTitleAutocomplete']")
        title_input.send_keys(title)
        # fill in employer name to make search button clickable
        employer_input = self.driver.find_element(By.CSS_SELECTOR, "input[name='employerAutocomplete']")
        employer_input.send_keys(employer)
        search_button = self.driver.find_element(By.CSS_SELECTOR, "button[data-test='salaries-landing-page-search-btn']")
        search_button.send_keys(Keys.RETURN)

        # scrape salary
        lower, upper = self.driver.find_element(By.CSS_SELECTOR, "div[data-test='total-pay']").text.replace("Base Pay Range", "").split("-")
        lower, upper = lower.strip().split(" ")[-1]+"/yr", upper.strip().split(" ")[-1]
        return (salary_string2annual(lower) + salary_string2annual(upper))/2


    def scrape_glassdoor(self, postings_json_path, save_path):
        """Scrapes glassdoor for salaries of scraped linkedin job postings stored in `json_path`
        
        """
        # login to glassdoor
        scraper.search_url("https://www.glassdoor.ca/")
        scraper.login("glassdoor_credentials.json")
        time.sleep(3)

        # load posting data from json
        with open(postings_json_path) as f:
            data = json.load(f)

        # preprocess json data and convert to 1D list
        all_postings = []
        for search_term in data:
            all_postings.extend(data[search_term])
        
        # scrape all salaries from glassdoor
        scraped_salaries = {}
        for posting in tqdm(all_postings):
            title, employer = posting["title"], posting["employer"]
            salary = self.scrape_salary_by_title_and_employer(title, employer)
            time.sleep(5)
            if salary == -1:
                salary = self.scrape_salary_by_title(title, employer)
            scraped_salaries[posting["url"]] = salary
            time.sleep(5)

            # save scraped salaries to json
            with open(save_path, "w") as f:
                json.dump(scraped_salaries, f, indent=4)
        

if __name__ == "__main__":
    # initialize a linkedin scraper
    #scraper = LinkedinScraper("./chromedriver_mac")

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
    #scraper.scrape_linkedin(search_terms)
    scraper = GlassDoorScraper("./chromedriver_mac", headless=False, undetected=True)
    scraper.scrape_glassdoor("data/linkedin_scraped_posts_0407.json", "data/glassdoor_scraped_salaries_0407.json")