from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class JobListing:
    title: str
    company: str
    location: str
    url: str
    source: str
    date_found: str = field(default_factory=lambda: datetime.today().strftime("%Y-%m-%d"))
    description: str = ""

    def to_row(self) -> list:
        """Convert to a flat list for Google Sheets insertion."""
        return [
            self.title,
            self.company,
            self.location,
            self.url,
            self.source,
            self.date_found,
            self.description,
            "New",  # Default status
        ]

    @staticmethod
    def headers() -> list:
        return ["Title", "Company", "Location", "URL", "Source", "Date Found", "Description", "Status"]


class BaseScraper(ABC):
    """
    Abstract base class for all job scrapers.
    Every source (RemoteOK, Indeed, LinkedIn, etc.) must implement this interface.
    Adding a new source = create a new file that extends BaseScraper. Nothing else changes.
    """

    @abstractmethod
    def scrape(self, keywords: list[str]) -> list[JobListing]:
        """
        Scrape job listings matching the given keywords.

        Args:
            keywords: List of search terms e.g. ["python", "automation", "remote"]

        Returns:
            List of JobListing objects. Empty list if scraping fails — never raise.
        """
        pass

    def safe_scrape(self, keywords: list[str]) -> list[JobListing]:
        """
        Wrapper around scrape() that catches all exceptions.
        Use this in production so one broken scraper doesn't kill the whole run.
        """
        try:
            return self.scrape(keywords)
        except Exception as e:
            print(f"[{self.__class__.__name__}] Scraping failed: {e}")
            return []
