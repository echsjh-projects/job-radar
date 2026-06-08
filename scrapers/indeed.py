import feedparser
from urllib.parse import urlencode
from .base import BaseScraper, JobListing


class IndeedScraper(BaseScraper):
    """
    Scrapes Indeed via their public RSS feed.
    Indeed RSS: https://www.indeed.com/rss?q=<query>&l=<location>
    No auth required. Keywords are passed as query params.
    """

    BASE_URL = "https://www.indeed.com/rss"

    def scrape(self, keywords: list[str]) -> list[JobListing]:
        query = " ".join(keywords)
        params = urlencode({"q": query, "l": "remote", "sort": "date"})
        feed_url = f"{self.BASE_URL}?{params}"

        feed = feedparser.parse(feed_url)
        results = []

        for entry in feed.entries:
            title = entry.get("title", "N/A")
            link = entry.get("link", "")
            summary = entry.get("summary", "")

            # Indeed includes company in title: "Job Title - Company Name"
            parts = title.rsplit(" - ", 1)
            job_title = parts[0].strip() if len(parts) > 1 else title
            company = parts[1].strip() if len(parts) > 1 else "N/A"

            results.append(JobListing(
                title=job_title,
                company=company,
                location="Remote",
                url=link,
                source="Indeed",
                description=summary[:300],
            ))

        print(f"[Indeed] Found {len(results)} matching jobs.")
        return results
