from typing import Any, Dict, List, Optional

from .company_parser import parse_company_details
from .helpers_time import epoch_ms_to_iso, relative_time_to_days_ago

def _get_nested(dct: Dict[str, Any], path: List[str], default: Any = None) -> Any:
    cur: Any = dct
    for key in path:
        if not isinstance(cur, dict) or key not in cur:
            return default
        cur = cur[key]
    return cur

def parse_job(raw_job: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize a single Indeed job record into a structured schema.

    Expected to work with objects similar to the example payload in the README.
    """
    job_id = raw_job.get("jobkey") or raw_job.get("adId") or raw_job.get("adBlob")

    title = raw_job.get("title") or raw_job.get("displayTitle")
    company = raw_job.get("company")
    location = raw_job.get("formattedLocation")
    source_link = raw_job.get("source_link")

    # Time fields
    create_date_ms: Optional[int] = raw_job.get("createDate")
    pub_date_ms: Optional[int] = raw_job.get("pubDate")

    created_at = epoch_ms_to_iso(create_date_ms) if create_date_ms else None
    published_at = epoch_ms_to_iso(pub_date_ms) if pub_date_ms else None

    formatted_relative_time = raw_job.get("formattedRelativeTime")
    days_ago = relative_time_to_days_ago(formatted_relative_time) if formatted_relative_time else None

    # Salary details
    salary = raw_job.get("salarySnippet") or {}
    salary_currency = salary.get("currency")
    salary_text_formatted = salary.get("salaryTextFormatted")
    salary_raw = {k: v for k, v in salary.items() if k not in {"currency", "salaryTextFormatted"}}

    job_types = raw_job.get("jobTypes") or []
    if not isinstance(job_types, list):
        job_types = [job_types]

    company_details_raw = raw_job.get("companyDetails") or {}
    company_details = parse_company_details(company_details_raw)

    advn = raw_job.get("advn")
    location_count = raw_job.get("locationCount")
    additional_location_link = raw_job.get("additionalLocationLink") or {}

    snippet = raw_job.get("snippet")
    description = raw_job.get("description") or snippet

    record: Dict[str, Any] = {
        "id": job_id,
        "title": title,
        "company": company,
        "location": location,
        "source_link": source_link,
        "created_at": created_at,
        "published_at": published_at,
        "posted_relative": formatted_relative_time,
        "posted_days_ago": days_ago,
        "job_types": job_types,
        "salary": {
            "currency": salary_currency,
            "is_text_formatted": salary_text_formatted,
            "raw": salary_raw or None,
        },
        "metadata": {
            "advn": advn,
            "location_count": location_count,
            "additional_location_label": additional_location_link.get("label"),
            "additional_location_url": additional_location_link.get("url"),
        },
        "summary": snippet,
        "description": description,
        "company_details": company_details or None,
        "raw_reference": {
            "jobkey": raw_job.get("jobkey"),
            "adId": raw_job.get("adId"),
        },
    }

    # Remove keys with only None values in nested objects
    if record["salary"]["raw"] is None:
        record["salary"].pop("raw")

    return record