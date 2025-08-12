import json
from typing import Dict
from openai import OpenAI
import re
from scraper import LinkedInScraper
from dotenv import load_dotenv
import os

class SpeakerPipeline:
    def __init__(self, apify_token_env='APIFY_TOKEN', openai_key_env='OPENAI_KEY'):
        # Load environment variables
        load_dotenv()
        self.apify_token = os.getenv(apify_token_env, '')
        self.openai_key = os.getenv(openai_key_env, '')

    def parse_query(self, query: str) -> Dict[str, str]:
        """
        Use OpenAI to extract structured filters from a plain-English query.
        Returns a dict with topic, job_titles, and expertise fields.
        """
        prompt = (
            "Extract structured filters from this speaker sourcing query:\n"
            f'"{query}"' + "\n\n"
            "Return only one JSON object with folling schema, nothing else.\n"
            "{" +
            '"topic": "",\n' +
            '"job_titles": [],\n' +
            '"expertise": []\n' +
            "}"
        )
        client = OpenAI(api_key=self.openai_key)
        response = client.completions.create(
            model="gpt-4o-mini",
            prompt=prompt,
            max_tokens=150
        )
        text = response.choices[0].text
        print(text)
        match = re.search(r'\{.*', text, re.DOTALL)
        if match:
            json_str = match.group(0)
            if not json_str.strip().endswith('}'):  # Try to auto-complete if cut off
                json_str += '}'
            try:
                return json.loads(json_str)
            except Exception as e:
                print("Error parsing model output:", e)
                print("Raw output:", text)
                return {}
        else:
            print("No JSON found in model output.")
            print("Raw output:", text)
            return {}

    def search_web(self, parsed_query):
        """
        Use LinkedInScraper to search for relevant LinkedIn profiles based on the parsed query.
        """
        search_url = f"https://www.google.com/search?q=site%3Alinkedin.com%2Fin+{'+'.join(parsed_query['job_titles'])}+{'+'.join(parsed_query['expertise'])}"
        scraper = LinkedInScraper(self.apify_token, search_url)
        scraper.run()

    def run(self, query):
        """
        Main pipeline entry point: parses the query and runs the web search.
        """
        parsed_query = self.parse_query(query)
        print("Parsed Query:", parsed_query)
        if not parsed_query:
            return {"statusCode": 400, "body": "Invalid query format."}
        self.search_web(parsed_query)
        return {"statusCode": 200, "body": "Search completed."}

if __name__ == "__main__":
    # Example usage
    event = {"query": "Find highly relevant speakers for a new virtual panel on ‘2026 Chinese Economy’.  We want senior leaders (Director level or above) with demonstrated expertise in Economics, Finance, or Data Science.  They should have a strong track record of public speaking and be able to share insights on the future of the Chinese economy."}
    pipeline = SpeakerPipeline()
    pipeline.run(event['query'])