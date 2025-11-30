from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs

class YouTubeTranscriptFetcher:
    def __init__(self, url: str):
        self.url = url
        self.video_id = self.extract_video_id(url)

    def extract_video_id(self, url: str) -> str:
        """
        Extract YouTube video ID from different YouTube URL formats
        """
        parsed = urlparse(url)

        # Case 1: https://www.youtube.com/watch?v=VIDEOID
        if parsed.query:
            params = parse_qs(parsed.query)
            if "v" in params:
                return params["v"][0]

        # Case 2: https://youtu.be/VIDEOID
        if parsed.netloc in ["youtu.be"]:
            return parsed.path.lstrip("/")

        # Case 3: embed format
        # https://www.youtube.com/embed/VIDEOID
        if "embed" in parsed.path:
            return parsed.path.split("/")[-1]

        raise ValueError("Could not extract YouTube Video ID from URL")

    def fetch_transcript(self) -> str:
        """
        Fetch and return transcript as plain text
        """
        try:
            transcript_list = YouTubeTranscriptApi().list(self.video_id).find_transcript(['en']).fetch()
            print(transcript_list)
            # Combine all text segments
            # full_text = " ".join([item['text'] for item in transcript_list])
            full_text = "\n".join(snippet.text for snippet in transcript_list.snippets)

            return full_text

        except Exception as e:
            return f"Error fetching transcript: {str(e)}"

if __name__ == "__main__":
    url = "https://www.youtube.com/watch?v=PziYflu8cB8"
    fetcher = YouTubeTranscriptFetcher(url)
    transcript = fetcher.fetch_transcript()

    print(dir(YouTubeTranscriptApi))

    print(transcript)