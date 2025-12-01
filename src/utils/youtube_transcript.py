"""
YouTube transcript utility
"""
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs
from typing import List, Optional


def extract_video_id(url: str) -> str:
    """Extract YouTube video ID from different URL formats"""
    parsed = urlparse(url)

    # Case 1: https://www.youtube.com/watch?v=VIDEOID
    if parsed.query:
        params = parse_qs(parsed.query)
        if "v" in params:
            return params["v"][0]

    # Case 2: https://youtu.be/VIDEOID
    if parsed.netloc in ["youtu.be", "www.youtu.be"]:
        return parsed.path.lstrip("/")

    # Case 3: embed format
    # https://www.youtube.com/embed/VIDEOID
    if "embed" in parsed.path:
        return parsed.path.split("/")[-1]

    raise ValueError("Could not extract YouTube Video ID from URL")


def fetch_transcript_text(video_id: str, languages: Optional[List[str]] = None) -> str:
    """Fetch transcript text for a given video id. Returns combined plain text.

    Raises Exception on failure so callers can map to domain errors.
    """
    if languages is None:
        languages = ["en"]

    # This returns a list of dicts with 'text' keys
    transcript_list = YouTubeTranscriptApi().list(video_id).find_transcript(['en']).fetch()
    # Combine into a single string separated by newlines
    full_text = "\n".join(snippet.text for snippet in transcript_list.snippets)

    return full_text