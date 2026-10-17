from .ComicSeries import ComicSeries
import requests
from bs4 import BeautifulSoup
import logging

#set up logging
logging.basicConfig(filename = "error.log", encoding='utf-8', level=logging.INFO)


# just a list to test with. corresponds to Claremont Era X-comics
TITLES_TO_DOWNLOAD = [ComicSeries(title="X-Men",         volume=1, first_issue=94, last_issue=141),
                      ComicSeries(title="Uncanny X-Men", volume=1, first_issue=142,last_issue=280),
                      ComicSeries(title="New Mutants",   volume=1, first_issue=1, last_issue=100),
                      ComicSeries(title="X-Factor",      volume=1, first_issue=1, last_issue=70),
                      ComicSeries(title="Excalibur",     volume=1, first_issue=1, last_issue=41),
                      ComicSeries(title="X-Force",       volume=1, first_issue=1, last_issue=15),
                      ComicSeries(title="Fallen Angels", volume=1, first_issue=1, last_issue=8),
                      ComicSeries(title="X-Terminators", volume=1, first_issue=1, last_issue=4)]

def build_full_list_of_issues(titles_to_download:list[ComicSeries]=TITLES_TO_DOWNLOAD) -> list[dict]:
    """
    Returns a list of issues for each title in TITLES_TO_DOWNLOAD.
    Each issue is a dictionary with the keys "title" and "url".
    """
    if type(titles_to_download) == ComicSeries:
        # only one title to download, so just return its issues
        return titles_to_download.issue_url_pairs()
    # else, multiple titles to download, so append their issues to the list
    full_list_of_issues = []
    for t in titles_to_download:
        full_list_of_issues.extend(t.issue_url_pairs())

    return full_list_of_issues


def soup_from_url(url: str, max_retries: int = 3) -> BeautifulSoup:
    """
    Returns the soup from the url. If it fails, tries a maximum of max_retries times.
    """
    for attempt in range(max_retries + 1):
        response = requests.get(url, timeout=30)
        if response.ok:
            return BeautifulSoup(response.content, "html.parser")

        logging.warning(
            "Request failed: status=%s attempt=%s url=%s",
            response.status_code,
            attempt + 1,
            url,
        )

    raise RuntimeError(f"Could not fetch {url} after {max_retries + 1} attempts")