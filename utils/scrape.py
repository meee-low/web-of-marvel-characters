import requests
from bs4 import BeautifulSoup
import logging

#set up logging
logging.basicConfig(filename = "error.log", encoding='utf-8', level=logging.INFO)

TITLES_TO_DOWNLOAD = [{"title": "X-Men Vol 1",         "first_issue": 94,  "last_issue": 141},
                      {"title": "Uncanny X-Men Vol 1", "first_issue": 142, "last_issue": 280},
                      {"title": "New Mutants Vol 1",   "first_issue": 1,   "last_issue": 100},
                      {"title": "X-Factor Vol 1",      "first_issue": 1,   "last_issue": 70},
                      {"title": "Excalibur Vol 1",     "first_issue": 1,   "last_issue": 41},
                      {"title": "X-Force Vol 1",       "first_issue": 1,   "last_issue": 15},
                      {"title": "Fallen Angels Vol 1", "first_issue": 1,   "last_issue": 8},
                      {"title": "X-Terminators Vol 1", "first_issue": 1,   "last_issue": 4}]

def build_full_list_of_issues(titles_to_download:list=TITLES_TO_DOWNLOAD) -> list:
    """
    Returns a list of issues for each title in TITLES_TO_DOWNLOAD.
    Each issue is a dictionary with the keys "title" and "url".
    """
    full_list_of_issues = []
    for t in titles_to_download:
        title, first_issue, last_issue = t["title"], t["first_issue"], t["last_issue"]
        for issue in list_issues(title, first_issue, last_issue):
            full_list_of_issues.append(issue)
    return full_list_of_issues

def list_issues(title:str, first_issue:int, last_issue:int) -> list:
    """
    Returns a list of issues for a given title.
    Each issue is a dictionary with the keys "title" and "url".
    """
    marvel_wiki_url = "https://marvel.fandom.com/wiki/"
    issues = []
    
    for i in range(first_issue, last_issue+1):
        issue_name = title + " " + str(i)
        url = marvel_wiki_url + issue_name
        url = url.replace(" ", "_") # change spaces to underscores
        url = remove_special_characters_from_url(url)
        issues.append({"title": issue_name, "url": url})
    return issues

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

def space_to_underscores(string):
    """Replace spaces with underscores."""
    return string.replace(" ", "_")

def remove_special_characters_from_url(string):
    """Remove special characters from a string. """
    allowed_characters = "_/:.-?%&()"
    return "".join(c for c in string if c.isalnum() or c in allowed_characters)