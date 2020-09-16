import requests
import re
from typing import Generator
from bs4 import BeautifulSoup

def listAllIssueUrlsForRepo(repo_name: str, pull_request: bool=False, open: bool=True) -> Generator[dict, None, None]:
    """Makes a call to GitHub, and returns all issues

    Args:
        repo_name (str): Name of repo
        pull_request [bool]: Pull requests or issues?
        open [bool]: Open issues or closed issues?

    Yields:
        Generator[str, None, None]: All issues
    """

    # Counter for page number
    page = 1

    # Collection of known issue numbers
    known_issues = []

    # Search identifier
    searchid = "is%3A"
    if pull_request:
        searchid += "pr+is%3A"
    else:
        searchid += "issue+is%3A"
    if open:
        searchid += "open+sort%3Aupdated-desc"
    else:
        searchid += "closed+sort%3Aupdated-desc"

    # Search type
    search_type = "pull" if pull_request else "issues"
        
    # Loop until we run out of pages
    while True:

        # Tracker for if this page is a duplicate
        is_duplicate = True

        # Make web request
        res = requests.get(f"https://github.com/{repo_name}/issues?q={searchid}&page={page}")

        # If the request fails, return
        if res.status_code != 200:
            return

        # Parse out issues
        soup = BeautifulSoup(res.text, 'html.parser')
        all_issues: list = soup.find_all(class_='js-issue-row')
        # all_issues = re.findall(f"{repo_name}\/{search_type}\/([0-9][0-9]*)", res.text, re.M)

        # If there are no links to issues, return
        if len(all_issues) == 0:
            break

        # Iter every issue
        for issue in all_issues:

            # Parse out the issue name
            possible_names = issue.find_all(class_="js-navigation-open")
            issue_name: str = ""
            issue_number: str = ""
            issue_author = issue.find(class_="opened-by").find("a").contents[0]
            possible_dates = issue.find_all("relative-time")
            issue_date: str = ""

            # Ensure there is data to read
            if len(possible_names) >= 1:
                issue_name = possible_names[0].contents[0]
                issue_number = re.findall(r"issue_([0-9][0-9]*)_link", possible_names[0].get("id"))[0]
            if len(possible_dates) >= 1:
                issue_date = possible_dates[0].contents[0]
        

            # If we have seen this issue before, skip
            if issue_number in known_issues:
                continue
            else:
                # This page is unique
                is_duplicate = False

                # Emit the number
                yield {
                    "name": issue_name,
                    "number": int(issue_number),
                    "author": issue_author,
                    "date": issue_date,
                    "url": f"htttps://github.com/{repo_name}/{search_type}/{issue_number}"
                }

            # Add to known issues
            known_issues.append(issue_number)

        # Break on duplicate page
        if is_duplicate:
            break
        else:
            # Incr the page number
            page += 1
        
    return


if __name__ == "__main__":

    print(list(listAllIssueUrlsForRepo("frc5024/lib5k")))