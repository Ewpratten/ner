import requests

def pullRequestToDiff(repo_name: str, pr_number: int) -> str:
    """Get the diff for a pull request

    Args:
        repo_name (str): Repository name
        pr_number (int): PR id

    Returns:
        str: Diff file
    """

    # Construct URL
    diff_url = f"https://patch-diff.githubusercontent.com/raw/{repo_name}/pull/{pr_number}.diff"

    # Make request
    return requests.get(diff_url).text
