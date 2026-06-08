import hashlib
from scrapers.base import JobListing


def _fingerprint(job: JobListing) -> str:
    """
    Create a stable unique hash for a job listing.
    Based on URL only — most reliable unique identifier.
    Falls back to title+company if URL is missing.
    """
    key = job.url.strip() if job.url else f"{job.title}|{job.company}".lower()
    return hashlib.md5(key.encode()).hexdigest()


def deduplicate(
    new_jobs: list[JobListing],
    existing_urls: set[str],
) -> list[JobListing]:
    """
    Filter out jobs that are already in the sheet.

    Two-layer deduplication:
      1. Against existing_urls from Google Sheets (already persisted)
      2. Within the current batch (same job from two different scrapers)

    Args:
        new_jobs: All jobs scraped in this run
        existing_urls: URLs already stored in Google Sheets

    Returns:
        Only jobs that are genuinely new
    """
    seen_in_batch = set()
    unique_jobs = []

    for job in new_jobs:
        # Skip if already in the sheet
        if job.url in existing_urls:
            continue

        # Skip duplicates within this batch
        fp = _fingerprint(job)
        if fp in seen_in_batch:
            continue

        seen_in_batch.add(fp)
        unique_jobs.append(job)

    total = len(new_jobs)
    dupes = total - len(unique_jobs)
    print(f"[Deduplicator] {total} scraped → {dupes} duplicates removed → {len(unique_jobs)} new jobs.")

    return unique_jobs
