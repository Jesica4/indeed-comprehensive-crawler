import re
from datetime import datetime, timezone
from typing import Optional

def epoch_ms_to_iso(value: Optional[int]) -> Optional[str]:
    """Convert an epoch timestamp in milliseconds to an ISO 8601 string."""
    if value is None:
        return None
    try: