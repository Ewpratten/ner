import flask
from webapputils import Webapp
import re
import markdown2
import requests

from .validation import isValidGitHubRepo
from .webscraper import listAllIssueUrlsForRepo, getPullRequestMetadata, getIssueMetadata, getListOfRecentCommits
from .diff2html import diff_prettyHtml
from .utils import pullRequestToDiff, commitToPatch

# Config
CACHE_SECONDS = 60

# Set up an app
app = Webapp(__name__, static_directory="static", google_tracking_code=None)

@app.errorhandler(404)
def page_not_found(e):
    return flask.render_template('404.html'), 404

@app.route("/")
def serveIndex() -> flask.Response:
    """Handles serving the index page

    Returns:
        flask.Response: Index.html
    """

    # Build response
    res = flask.make_response(flask.render_template("index.html"))
    res.headers.set('Cache-Control', f"s-maxage={CACHE_SECONDS}, stale-while-revalidate")
    return res

@app.route("/gh/<org>/<repo>")
def serveRepoMainPage(org: str, repo: str) -> flask.Response:

    # Build repo name
    repo_name = f"{org}/{repo}"

    # If invalid, go to 404
    if not isValidGitHubRepo(repo_name):
        flask.abort(404)

    # Load the README file
    readme_source = requests.get(f"https://raw.githubusercontent.com/{repo_name}/master/README.md")
    if readme_source.status_code != 200:
        readme_source_md = f"# Summary not available for {repo_name}"
    else:
        readme_source_md = readme_source.text

    # Substitute any relative links
    readme_source_md = readme_source_md.replace("(assets/", "(./assets/").replace(f"(/{repo_name}", f"(https://raw.githubusercontent.com/{repo_name}/master/").replace(f"(./", f"(https://raw.githubusercontent.com/{repo_name}/master/")

    # Render README
    readme_html = markdown2.markdown(readme_source_md)

    # Build the template file
    res = flask.make_response(flask.render_template("summary.html", repo_name=repo_name, readme=readme_html))
    res.headers.set('Cache-Control', f"s-maxage={CACHE_SECONDS}, stale-while-revalidate")
    return res

@app.route("/gh/<org>/<repo>/log")
def serveRepoCommitLog(org: str, repo: str) -> flask.Response:

    # Build repo name
    repo_name = f"{org}/{repo}"

    # If invalid, go to 404
    if not isValidGitHubRepo(repo_name):
        flask.abort(404)

    # Get most recent commits
    commits = list(getListOfRecentCommits(repo_name))

    # Build the template file
    res = flask.make_response(flask.render_template("log.html", repo_name=repo_name, commits=commits))
    res.headers.set('Cache-Control', f"s-maxage={CACHE_SECONDS}, stale-while-revalidate")
    return res

@app.route("/gh/<org>/<repo>/commit/<id>")
def serveRepoCommit(org: str, repo: str, id: int) -> flask.Response:

    # Build repo name
    repo_name = f"{org}/{repo}"

    # If invalid, go to 404
    if not isValidGitHubRepo(repo_name):
        flask.abort(404)

    # Get commit diff
    patch = commitToPatch(repo_name, id)

    # Build diff into HTML
    patch_html = diff_prettyHtml(patch)

    # Build the template file
    res = flask.make_response(flask.render_template("commit.html", repo_name=repo_name, patch=patch_html, commit_id=id))
    res.headers.set('Cache-Control', f"s-maxage={CACHE_SECONDS}, stale-while-revalidate")
    return res

@app.route("/gh/<org>/<repo>/issues")
def serveRepoIssues(org: str, repo: str) -> flask.Response:

    # Build repo name
    repo_name = f"{org}/{repo}"

    # If invalid, go to 404
    if not isValidGitHubRepo(repo_name):
        flask.abort(404)

    # Get all issues
    all_issues = list(listAllIssueUrlsForRepo(repo_name))

    # Build the template file
    res = flask.make_response(flask.render_template("issues.html", repo_name=repo_name, issues=all_issues))
    res.headers.set('Cache-Control', f"s-maxage={CACHE_SECONDS}, stale-while-revalidate")
    return res

@app.route("/gh/<org>/<repo>/issue/<id>")
def serveRepoIssue(org: str, repo: str, id: int) -> flask.Response:

    # Build repo name
    repo_name = f"{org}/{repo}"

    # If invalid, go to 404
    if not isValidGitHubRepo(repo_name):
        flask.abort(404)

    # Get issue data
    issue_data = list(getIssueMetadata(repo_name, id))

    # Build the template file
    res = flask.make_response(flask.render_template("issue.html", repo_name=repo_name, messages = issue_data, issue_id=id))
    res.headers.set('Cache-Control', f"s-maxage={CACHE_SECONDS}, stale-while-revalidate")
    return res

@app.route("/gh/<org>/<repo>/proposals")
def serveRepoProposals(org: str, repo: str) -> flask.Response:

    # Build repo name
    repo_name = f"{org}/{repo}"

    # If invalid, go to 404
    if not isValidGitHubRepo(repo_name):
        flask.abort(404)

    # Get all issues
    all_issues = list(listAllIssueUrlsForRepo(repo_name, pull_request=True))

    # Build the template file
    res = flask.make_response(flask.render_template("proposals.html", repo_name=repo_name, proposals=all_issues))
    res.headers.set('Cache-Control', f"s-maxage={CACHE_SECONDS}, stale-while-revalidate")
    return res

@app.route("/gh/<org>/<repo>/proposals/<id>")
def serveRepoProposal(org: str, repo: str, id: int) -> flask.Response:

    # Build repo name
    repo_name = f"{org}/{repo}"

    # If invalid, go to 404
    if not isValidGitHubRepo(repo_name):
        flask.abort(404)

    # Get proposal data
    metadata = getPullRequestMetadata(repo_name, id)

    # Get proposal diff
    diff = pullRequestToDiff(repo_name, id)

    # Build diff into HTML
    diff_html = diff_prettyHtml(diff)

    # Build the template file
    res = flask.make_response(flask.render_template("proposal.html", repo_name=repo_name, diff=diff_html, metadata=metadata, pull_id=id))
    res.headers.set('Cache-Control', f"s-maxage={CACHE_SECONDS}, stale-while-revalidate")
    return res

@app.route("/gh/<org>/<repo>/dashboard")
def serveRepoDashboard(org: str, repo: str) -> flask.Response:

    # Build repo name
    repo_name = f"{org}/{repo}"

    # If invalid, go to 404
    if not isValidGitHubRepo(repo_name):
        flask.abort(404)

    # Build output data
    all_data = {
        "prs": [],
        "issues": [],
        "commits":[]
    }

    # Get all prs
    all_data["prs"] += list(listAllIssueUrlsForRepo(repo_name, pull_request=True, open=True))
    all_data["prs"] += list(listAllIssueUrlsForRepo(repo_name, pull_request=True, open=False))

    # Get all issues
    all_data["issues"] += list(listAllIssueUrlsForRepo(repo_name, pull_request=False, open=True))
    all_data["issues"] += list(listAllIssueUrlsForRepo(repo_name, pull_request=False, open=False))

    # Get all commits
    all_data["commits"] += list(getListOfRecentCommits(repo_name))

    # Make one large array combining all sources
    combined_data = []
    for pr in all_data["prs"]:
        pr["url"] = f"/gh/{repo_name}/proposals/" + str(pr["number"])
        combined_data.append(pr)
    for issue in all_data["issues"]:
        issue["url"] = f"/gh/{repo_name}/issue/" + str(issue["number"])
        combined_data.append(issue)
    for commit in all_data["commits"]:
        commit["url"] = f"/gh/{repo_name}/commit/" + str(commit["number"])
        commit["number"] = commit["number"][:14]
        combined_data.append(commit)

    combined_data.sort(key=lambda x: x["date"])
    combined_data.reverse()

    # Build the template file
    res = flask.make_response(flask.render_template("dashboard.html", repo_name=repo_name, events=combined_data))
    res.headers.set('Cache-Control', f"s-maxage={CACHE_SECONDS}, stale-while-revalidate")
    return res

if __name__ == "__main__":
    app.run(debug=True)

