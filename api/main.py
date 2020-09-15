import flask
from webapputils import Webapp

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

    # Load the index
    with open("templates/index.html", "r") as fp:
        index_file = fp.read()
        fp.close()

    # Build response
    res = flask.make_response(index_file)
    res.headers.set('Cache-Control', f"s-maxage={CACHE_SECONDS}, stale-while-revalidate")
    return res



if __name__ == "__main__":
    app.run(debug=True)

