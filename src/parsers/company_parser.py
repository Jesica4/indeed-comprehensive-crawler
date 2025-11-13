from typing import Any, Dict, List, Optional

def _get_nested(dct: Dict[str, Any], path: List[str], default: Any = None) -> Any:
    cur: Any = dct
    for key in path:
        if not isinstance(cur, dict) or key not in cur:
            return default
        cur = cur[key]
    return cur

def parse_company_details(company_details: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize companyDetails structure from Indeed into a compact schema.

    Works with structures similar to the README example, but degrades gracefully
    if some keys are missing.
    """
    if not company_details:
        return {}

    ceo_name: Optional[str] = _get_nested(
        company_details,
        ["aboutSectionViewModel", "aboutCeo", "name"],
    )
    ceo_photo_48: Optional[str] = _get_nested(
        company_details,
        ["aboutSectionViewModel", "aboutCeo", "photoUrls", "48px"],
    )
    ceo_photo_96: Optional[str] = _get_nested(
        company_details,
        ["aboutSectionViewModel", "aboutCeo", "photoUrls", "96px"],
    )
    ceo_photo_512: Optional[str] = _get_nested(
        company_details,
        ["aboutSectionViewModel", "aboutCeo", "photoUrls", "512px"],
    )

    founded = _get_nested(
        company_details,
        ["aboutSectionViewModel", "aboutCompany", "founded"],
    )
    revenue = _get_nested(
        company_details,
        ["aboutSectionViewModel", "aboutCompany", "revenue"],
    )
    employee_range = _get_nested(
        company_details,
        ["aboutSectionViewModel", "aboutCompany", "employeeRange"],
    )
    industry = _get_nested(
        company_details,
        ["aboutSectionViewModel", "aboutCompany", "industry"],
    )
    description = _get_nested(
        company_details,
        ["aboutSectionViewModel", "aboutCompany", "description"],
    )
    headquarters = _get_nested(
        company_details,
        ["aboutSectionViewModel", "aboutCompany", "headquarters"],
    )

    total_job_count = _get_nested(
        company_details,
        ["jobsSectionViewModel", "totalJobCount"],
    )

    job_categories_list = _get_nested(
        company_details,
        ["jobsSectionViewModel", "jobCategories"],
        default=[],
    )
    categories = []
    if isinstance(job_categories_list, list):
        for item in job_categories_list:
            if isinstance(item, dict):
                categories.append(
                    {
                        "name": item.get("displayName"),
                        "key": item.get("key"),
                        "job_count": item.get("jobCount"),
                    },
                )

    active_listings_list = _get_nested(
        company_details,
        ["jobsSectionViewModel", "activeListings"],
        default=[],
    )
    active_listings = []
    if isinstance(active_listings_list, list):
        for listing in active_listings_list:
            if isinstance(listing, dict):
                active_listings.append(
                    {
                        "title": listing.get("title"),
                        "location": listing.get("location"),
                        "job_types": listing.get("jobTypes") or [],
                        "post_date": listing.get("postDate"),
                    },
                )

    parsed: Dict[str, Any] = {
        "ceo": {
            "name": ceo_name,
            "photo_48": ceo_photo_48,
            "photo_96": ceo_photo_96,
            "photo_512": ceo_photo_512,
        },
        "about": {
            "founded": founded,
            "revenue_band": revenue,
            "employee_range": employee_range,
            "industry": industry,
            "description": description,
            "headquarters": headquarters,
        },
        "jobs": {
            "total_job_count": total_job_count,
            "categories": categories,
            "active_listings": active_listings,
        },
    }

    # Strip empty nested objects
    if all(v is None for v in parsed["ceo"].values()):
        parsed.pop("ceo")
    if all(v is None for v in parsed["about"].values()):
        parsed.pop("about")
    if (
        parsed["jobs"]["total_job_count"] is None
        and not parsed["jobs"]["categories"]
        and not parsed["jobs"]["active_listings"]
    ):
        parsed.pop("jobs")

    return parsed