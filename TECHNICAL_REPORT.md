# Technical Report: Speaker Sourcing Pipeline and Recommendation System

---

## 1. Automated Speaker Sourcing Pipeline

### Approach
- The pipeline takes a plain-English query (e.g., "Find senior data science leaders for AI in agriculture") and uses OpenAI's language model to extract structured filters (topic, job titles, expertise).
- It builds a Google search URL and uses a Selenium-based scraper to collect LinkedIn profile links matching the criteria.
- Profiles are deduplicated against an existing database and new records are stored.

### Design Choices
- **OpenAI for Query Parsing:** Ensures flexible, robust extraction of requirements from natural language.
- **Selenium Scraper:** Chosen for flexibility in navigating and extracting from Google search results.
- **.env for Secrets:** API keys are loaded from environment variables for security.
- **Class-based Structure:** Improves modularity and testability.

### Assumptions
- Google search results contain relevant LinkedIn profiles.
- OpenAI model can reliably extract structured filters from queries.
- LinkedIn profile URLs are unique identifiers for deduplication.

### Metrics
- **Recall:** Fraction of relevant speakers found (manual review).
- **Precision:** Fraction of found profiles that match the query intent.
- **Deduplication Rate:** Number of new unique profiles added.

### Future Work
- **Scheduling:** Integrate with a workflow scheduler like Apache Airflow to automate regular runs, monitor pipeline health, and handle retries/failures.
- **Adding New Sources:** Modularize the scraping logic to easily add new data sources (e.g., conference sites, academic databases, or APIs) by implementing new scraper classes and updating the pipeline to aggregate results.
- **Guarding Against Scraping Bans/CAPTCHAs:**
  - Use rotating proxies and user-agents to reduce detection risk.
  - Add randomized delays and human-like browsing patterns.
  - Integrate CAPTCHA-solving services or fallback to manual review if a CAPTCHA is detected.
  - Prefer official APIs or data partnerships where possible.
- Integrate with official LinkedIn or other professional APIs for more reliable data.
- Add more advanced deduplication (e.g., fuzzy name matching).
- Automate validation of speaker expertise using NLP on profile content.
- Add logging, monitoring, and error handling for production.

---

## 2. Speaker Recommendation System

### Approach
- Loads processed speaker data (with expertise topics) from CSV.
- Encodes both speaker expertise and event topics using sentence transformers.
- Uses a weighted one-hot encoding for expertise categories.
- Normalizes embeddings and uses FAISS for fast similarity search.
- Returns the top-N most relevant speakers for a given topic.

### Design Choices
- **Sentence Transformers:** Chosen for semantic understanding of topics and expertise.
- **Weighted Encoding:** Top categories are weighted higher for more relevant matches.
- **FAISS:** Enables fast, scalable similarity search over large speaker datasets.
- **Class-based Design:** Encapsulates logic for easy reuse and extension.

### Assumptions
- The expertise topics extracted for each speaker are accurate and representative.
- The event topic can be mapped to the same set of categories as the speakers.
- Top-N similarity is a good proxy for speaker relevance.

### Metrics
- **Top-N Accuracy:** Fraction of recommended speakers that are relevant (manual review or feedback).
- **Diversity:** Number of unique categories represented in recommendations.
- **Latency:** Time to generate recommendations (measured in seconds).

### Future Work
- **Cold-Start Awareness:** Recognize that new speakers or topics with little data may not be well-represented (cold-start problem). In the future, collaborative filtering (using user feedback or co-occurrence data) or hybrid approaches (combining content-based and collaborative methods) could be used to improve recommendations for new or sparsely represented cases.
- Incorporate feedback loop to improve recommendations over time.
- Add support for multi-lingual queries and profiles.
- Integrate additional data sources (e.g., publications, talks, social media).
- Visualize speaker-topic similarity with interactive dashboards.

---

## Diagrams

### Pipeline Overview

```
Plain-English Query
      |
      v
[OpenAI Query Parser]
      |
      v
[Google Search URL]
      |
      v
[Selenium Scraper] ---> [Deduplication] ---> [Speaker Database]
```

### Recommendation Flow

```
[Speaker Database]         [Event Topic]
        |                      |
        v                      v
[Expertise Embedding]   [Topic Embedding]
        |                      |
        +----------[FAISS Similarity Search]----------+
                                   |
                                   v
                        [Top-N Speaker Recommendations]
```

---

For more details, see the README and code comments.
