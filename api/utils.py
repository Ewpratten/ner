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

def commitToDiff(repo_name: str, id: int) -> str:
    """Get the diff for a commit

    Args:
        repo_name (str): Repository name
        id (int): Commit id

    Returns:
        str: Diff file
    """

    # Construct URL
    diff_url = f"https://patch-diff.githubusercontent.com/raw/{repo_name}/commit/{id}.diff"

    # Make request
    return requests.get(diff_url).text



def commitToPatch(repo_name: str, id: int) -> str:
    """Get the patch for a commit

    Args:
        repo_name (str): Repository name
        id (int): Commit id

    Returns:
        str: patch file
    """

    # Construct URL
    patch_url = f"https://github.com/{repo_name}/commit/{id}.patch"

    # Make request
    return requests.get(patch_url).text