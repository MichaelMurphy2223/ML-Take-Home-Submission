# Speaker Recommendation System

This project automates the discovery and recommendation of expert speakers for events or panels using NLP, web scraping, and semantic search.

## Project Structure

- `pipeline/`
  - `pipeline.py`: Main pipeline for parsing plain-English queries, extracting requirements using OpenAI, and sourcing LinkedIn profiles using a web scraper.
  - `scraper.py`: Contains the `LinkedInScraper` class for scraping LinkedIn profile links from Google search results.
- `recommendation/`
  - `preprocess.py`: Preprocesses the speaker dataset, extracts expertise topics, and saves a clean CSV.
  - `main.py`: Contains the `SpeakerRecommender` class for finding the most relevant speakers for a given topic using semantic and category-based similarity search.
- `speakers.csv`: Output file with processed speaker data.

---

## 1. Automated Speaker Sourcing Pipeline (`pipeline/pipeline.py`)

### What it does
- Accepts a plain-English query describing the desired speaker profile.
- Uses OpenAI to extract structured filters (topic, job titles, expertise).
- Builds a Google search URL and uses a LinkedIn scraper to collect candidate profiles.
- (Optionally) Deduplicates and stores new profiles.

### How to run
1. Set your API keys in a `.env` file:
   ```env
   OPENAI_KEY=your_openai_key
   APIFY_TOKEN=your_apify_token
   ```
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. Run the pipeline:
   ```sh
   python pipeline/pipeline.py
   ```

---

## 2. Speaker Recommendation (`recommendation/main.py`)

### What it does
- Loads processed speaker data from `speakers.csv`.
- Encodes speaker expertise and event topics using sentence transformers.
- Finds the most relevant speakers for a given topic using FAISS similarity search.

### How to run
1. Ensure `speakers.csv` exists (run preprocessing if needed).
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. Run the recommender:
   ```sh
   python recommendation/main.py
   ```

---

## Requirements
- Python 3.8+
- See `requirements.txt` for all dependencies (including `sentence-transformers`, `faiss`, `openai`, `selenium`, etc.)

---

## Notes
- Do not commit your `.env` file or any sensitive API keys to version control.
- For production, consider using a secrets manager and robust error handling.

