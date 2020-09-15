import requests

def isValidGitHubRepoName(name: str) -> bool:
    """Checks if a name is a valid GitHub repo name

    Args:
        name (str): Name

    Returns:
        bool: Is valid?
    """
    return len(name.split("/")) == 2

def isValidGitHubRepo(name: str) -> bool:
    """Checks against the GitHub servers if a repository exists

    Args:
        name (str): Name

    Returns:
        bool: Exists?
    """

    # Make web request to GitHub
    res = requests.get(f"https://github.com/{name}")

    return isValidGitHubRepoName(name) and res.status_code == 200

