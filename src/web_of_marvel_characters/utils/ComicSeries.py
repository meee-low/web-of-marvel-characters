from dataclasses import dataclass

@dataclass
class ComicSeries:
    """
    Stores information about a comic book series.
    
    Used to generate a list of urls and titles for downloading.
    
    Example:
    Savage Avengers Vol 1 #1-28 is entered as:
        ComicSeries(title="Savage Avengers", volume=1, first_issue=1, last_issue=28)
    """
    
    title:str
    volume:int
    first_issue:int
    last_issue:int
    
    def list_of_issues(self) -> list[str]:
        return [f"{self.title} Vol {self.volume} {i}" for i in range(self.first_issue, self.last_issue+1)]
    
    def list_of_urls_of_issues(self) -> list[str]:
        return [format_to_url(issue) for issue in self.list_of_issues()]
    
    def issue_url_pairs(self) -> list[dict]:
        """Returns a list of dictionaries with the keys "title" and "url"."""
        issue_url_pairs = []
        for title, url in zip(self.list_of_issues(), self.list_of_urls_of_issues()):
            issue_url_pairs.append({"title": title, "url": url})
        return issue_url_pairs
    

def format_to_url(issue): 
    no_apostrophes = issue.replace("'", "%27") #replaces apostrophes
    no_spaces = no_apostrophes.replace(" ", "_") #replace spaces with underscores
    

    #remove special characters from url
    allowed_characters = "_/:.-?%&()"
    relative_url = "".join(c for c in no_spaces if c.isalnum() or c in allowed_characters)

    marvel_wiki_url = "https://marvel.fandom.com/wiki/"
    full_url = marvel_wiki_url + relative_url #prepend marvel_wiki_url
    return full_url

def from_csv(csv_file_path):
    #TODO
    pass