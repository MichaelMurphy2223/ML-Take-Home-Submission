from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from apify_client import ApifyClient
import time
import pandas as pd

class LinkedInScraper:
    def __init__(self, token, search_url, csv_path='new_speakers.csv'):
        self.token = token
        self.search_url = search_url
        self.csv_path = csv_path
        self.chrome_options = Options()
        # self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        self.driver = webdriver.Chrome(options=self.chrome_options)
        self.total = []

    def scrape_links(self):
        self.driver.get(self.search_url)
        while len(self.total) < 50:
            time.sleep(5)
            print("Scraping current page...")
            results = self.driver.find_elements(By.TAG_NAME, "a")
            links = [element.get_attribute("href").split('#')[0] for element in results if element.get_attribute("href") and "linkedin.com/in/" in element.get_attribute("href")]
            print(links)
            self.total.extend(links)
            print(f"Found {len(self.total)} LinkedIn profiles.")
            try:
                next_page_link = self.driver.find_element(By.ID, "pnnext")
                if next_page_link:
                    time.sleep(5)
                    next_page_link.click()
            except NoSuchElementException:
                print("No more pages available")
                break
        self.driver.quit()

    def filter_existing(self):
        try:
            existing_df = pd.read_csv(self.csv_path)
        except FileNotFoundError:
            existing_df = pd.DataFrame(columns=['linkedinUrl'])
        self.total = [link for link in self.total if link not in existing_df['linkedinUrl'].tolist()]
        self.total = list(set(self.total))  # Remove duplicates
        self.total = self.total[:3]
        print(self.total)

    def run_apify(self):
        apify_client = ApifyClient(self.token)
        actor_client = apify_client.actor('dev_fusion/Linkedin-Profile-Scraper')
        run_input = {"profileUrls": self.total}
        call_result = actor_client.call(run_input=run_input)
        if call_result is None:
            print('Actor run failed.')
            return
        print("💾 Check your data here: https://console.apify.com/storage/datasets/" + call_result['defaultDatasetId'])
        columns = ['linkedinUrl', 'fullName', 'headline', 'email', 'jobTitle', 'addressCountryOnly', 'topSkillsByEndorsements', 'companyName', 'companyIndustry', 'experiences']
        df = pd.DataFrame(columns=columns)
        for item in apify_client.dataset(call_result['defaultDatasetId']).iterate_items():
            sub_df = pd.json_normalize(item)
            if not sub_df.empty and not sub_df.isna().all(axis=None):
                df = pd.concat([df, sub_df], ignore_index=True)
        df = df[columns]
        try:
            existing_df = pd.read_csv(self.csv_path)
        except FileNotFoundError:
            existing_df = pd.DataFrame(columns=columns)
        existing_df = pd.concat([existing_df, df], ignore_index=True)
        existing_df.drop_duplicates(subset=['linkedinUrl'], inplace=True)
        existing_df.reset_index(drop=True, inplace=True)
        existing_df.to_csv(self.csv_path, index=False)
        print("Data saved to new_speakers.csv")

    def run(self):
        self.scrape_links()
        self.filter_existing()
        self.run_apify()