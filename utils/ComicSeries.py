from dataclasses import dataclass

@dataclass
class ComicSeries:
    """
    Stores information about a comic book series.
    
    Used to generate a list of urls and titles for downloading.
    
    Example:
    Savage Avengers Vol 1 1-28 is entered as:
        ComicSeries(title="Savage Avengers", volume=1, first_issue=1, last_issue=28)
         
        and zipped_titles_and_urls() returns:
            [("Savage Avengers Vol 1 1", "Savage_Avengers_Vol_1_1"),
             ("Savage Avengers Vol 1 2", "Savage_Avengers_Vol_1_2"), ...
             ("Savage Avengers Vol 1 28", "Savage_Avengers_Vol_1_28")]
    """
    
    title:str
    volume:int
    first_issue:int
    last_issue:int
    
    def list_of_issues(self):
        return [f"{self.title} Vol {self.volume} {i}" for i in range(self.first_issue, self.last_issue+1)]
    
    def list_of_urls_of_issues(self):
        def format_to_url(issue):
            issue.replace(" ", "_")
            allowed_characters = "_/:.-?%&()"
            return "".join(c for c in issue if c.isalnum() or c in allowed_characters)
        
        return [format_to_url(issue) for issue in self.list_of_issues()]
    
    def zipped_titles_and_urls(self):
        return zip(self.list_of_issues(), self.list_of_urls_of_issues())