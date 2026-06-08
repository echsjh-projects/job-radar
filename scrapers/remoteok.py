import httpx
from .base import BaseScraper, JobListing


REMOTEOK_API = "https://remoteok.com/api"


class RemoteOKScraper(BaseScraper):
    """
    Scrapes RemoteOK via their public JSON API.
    No auth required. Rate limit: be respectful, one call per run is fine.
    API docs: https://remoteok.com/api
    """

    def scrape(self, keywords: list[str]) -> list[JobListing]:
        headers = {
            # RemoteOK requires a User-Agent or returns 403
            "User-Agent": "job-tracker-bot/1.0 (personal CV project)"
        }

        response = httpx.get(REMOTEOK_API, headers=headers, timeout=15)
        response.raise_for_status()

        # First item is metadata, skip it
        raw_jobs = response.json()[1:]

        results = []
        keywords_lower = [kw.lower() for kw in keywords]

        for job in raw_jobs:
            # Match against title, tags, and description
            searchable = " ".join([
                job.get("position", ""),
                job.get("company", ""),
                " ".join(job.get("tags", []) or []),
                job.get("description", ""),
            ]).lower()

            if not any(kw in searchable for kw in keywords_lower):
                continue

            results.append(JobListing(
                title=job.get("position", "N/A"),
                company=job.get("company", "N/A"),
                location=job.get("location") or "Remote",
                url=job.get("url", ""),
                source="RemoteOK",
                description=job.get("description", "")[:300],  # Truncate long descriptions
            ))

        print(f"[RemoteOK] Found {len(results)} matching jobs.")
        return results
