import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel, Field


class BrowseURLArgs(BaseModel):
    """Input model for the browse_url tool."""

    url: str = Field(..., description="The full URL of the webpage to browse.")


def scrape_url(args: BrowseURLArgs) -> str:
    """Fetches the content from a given URL, parses the HTML, and returns the clean text content.
    Use this tool to read the content of a specific webpage for analysis or summarization.
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(args.url, headers=headers, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")

        for script_or_style in soup(["script", "style"]):
            script_or_style.decompose()

        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        clean_text = "\n".join(chunk for chunk in chunks if chunk)

        return f"Successfully browsed URL '{args.url}'. Content:\n\n{clean_text}"

    except requests.exceptions.RequestException as e:
        return f"Error browsing URL '{args.url}': {e}"
    except Exception as e:
        return f"An unexpected error occurred while browsing '{args.url}': {e}"
