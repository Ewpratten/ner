import flask
from webapputils import Webapp
import re
import markdown2
import requests

from .validation import isValidGitHubRepo
from .webscraper import listAllIssueUrlsForRepo
from .diff2html import diff_prettyHtml
from .utils import pullRequestToDiff

# Config
CACHE_SECONDS = 60

# Set up an app
app = Webapp(__name__, static_directory="static", google_tracking_code=None)

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
        readme_source_md = f"# Summary not available {repo_name}"
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


    # Build the template file
    res = flask.make_response(flask.render_template("log.html", repo_name=repo_name))
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
    # TODO

    # Get proposal diff
    diff = pullRequestToDiff(repo_name, id)

    # Build diff into HTML
    diff_html = diff_prettyHtml(diff)

    # Build the template file
    res = flask.make_response(flask.render_template("proposal.html", repo_name=repo_name, diff=diff_html))
    res.headers.set('Cache-Control', f"s-maxage={CACHE_SECONDS}, stale-while-revalidate")
    return res


if __name__ == "__main__":
    app.run(debug=True)

