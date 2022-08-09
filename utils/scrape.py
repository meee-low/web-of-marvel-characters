from utils.ComicSeries import ComicSeries
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


def soup_from_url(url:str, retries=0, max_retries=3):
    """
    Returns the soup from the url. If it fails, tries a maximum of max_retries times.
    """
    response = requests.get(url)    
    soup = BeautifulSoup(response.content, "html.parser")
    
    if response.status_code == 200:
        # All good. Return.
        return soup
    elif retries <= max_retries: #retry at most this many tries
        error_message = f"Tried to scrape and failed.   " \
                        f"Response code: {response.status_code}   " \
                        f"Tries: {retries}   " \
                        f"len(soup): {len(soup)}   " \
                        f"len(response.content()): {len(response.content)}   " \
                        f"URL: {url.split('/')[-1]}"
        logging.warning(error_message)
        return soup_from_url(url, retries=retries+1)
    else:
        logging.error(f"Tried too many times and failed. Exiting.")
        assert False #assert False is bad practice. create an err.