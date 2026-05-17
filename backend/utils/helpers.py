"""
Utility Helper Functions
"""

import hashlib
import logging
from datetime import datetime
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


def generate_hash(text: str) -> str:
    """Generate MD5 hash from text"""
    return hashlib.md5(text.encode()).hexdigest()


def truncate_text(text: str, max_length: int = 1000) -> str:
    """Truncate text to max length"""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."


def format_timestamp(dt: datetime) -> str:
    """Format datetime as string"""
    if not dt:
        return "unknown"
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def safe_get(dictionary: Dict, *keys, default=None) -> Any:
    """Safely get nested dictionary value"""
    value = dictionary
    for key in keys:
        if isinstance(value, dict):
            value = value.get(key)
        else:
            return default
        if value is None:
            return default
    return value


def deduplicate_list(items: List) -> List:
    """Remove duplicates while preserving order"""
    seen = set()
    result = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def extract_filename(filepath: str) -> str:
    """Extract filename from path"""
    return filepath.split('/')[-1] if '/' in filepath else filepath


def is_valid_python_file(filepath: str) -> bool:
    """Check if file is a Python file"""
    return filepath.endswith('.py')


def merge_dicts(*dicts) -> Dict:
    """Merge multiple dictionaries"""
    result = {}
    for d in dicts:
        if d:
            result.update(d)
    return result
