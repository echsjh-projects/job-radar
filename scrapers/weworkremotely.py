import feedparser
import httpx
from .base import BaseScraper, JobListing


WWR_RSS_FEEDS = {
    "programming": "https://weworkremotely.com/categories/remote-programming-jobs.rss",
    "devops":      "https://weworkremotely.com/categories/remote-devops-sysadmin-jobs.rss",
    "data":        "https://weworkremotely.com/categories/remote-data-science-jobs.rss",
    "full_stack":  "https://weworkremotely.com/categories/remote-full-stack-programming-jobs.rss",
}


class WeWorkRemotelyScraper(BaseScraper):
    """
    Scrapes We Work Remotely via their public RSS feeds.
    Uses feedparser — no browser automation needed.
    """

    def scrape(self, keywords: list[str]) -> list[JobListing]:
        keywords_lower = [kw.lower() for kw in keywords]
        results = []
        seen_urls = set()

        for feed_name, feed_url in WWR_RSS_FEEDS.items():
            feed = feedparser.parse(feed_url)

            for entry in feed.entries:
                title = entry.get("title", "")
                summary = entry.get("summary", "")
                link = entry.get("link", "")

                # Deduplicate within this scraper run
                if link in seen_urls:
                    continue
                seen_urls.add(link)

                searchable = f"{title} {summary}".lower()
                if not any(kw in searchable for kw in keywords_lower):
                    continue

                # WWR title format is usually "Company: Job Title"
                parts = title.split(":", 1)
                company = parts[0].strip() if len(parts) > 1 else "N/A"
                job_title = parts[1].strip() if len(parts) > 1 else title

                results.append(JobListing(
                    title=job_title,
                    company=company,
                    location="Remote",
                    url=link,
                    source="WeWorkRemotely",
                    description=summary[:300],
                ))

        print(f"[WeWorkRemotely] Found {len(results)} matching jobs.")
        return results
