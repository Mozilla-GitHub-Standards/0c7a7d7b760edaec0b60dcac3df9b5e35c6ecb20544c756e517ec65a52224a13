import os
import sys
import config
import logging
import json

sys.path.append(os.path.join(os.path.dirname(__file__), "lib"))
sys.path.append(os.path.join(os.path.dirname(__file__), "utilities"))
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
from elasticsearch.exceptions import NotFoundError
from elasticsearch.helpers import bulk, BulkIndexError

from elasticsearch_client import ElasticsearchClient, ElasticsearchBadServer, ElasticsearchInvalidIndex, ElasticsearchException
from utilities.toUTC import toUTC
from query_models import SearchQuery, TermMatch, AggregatedResults, SimpleResults


from flask import (
    Flask,
    redirect,
    render_template,
    request,
    session,
    url_for,
    make_response,
    send_from_directory,
    jsonify
)

# setup the app
app = Flask(__name__)
#app.config.from_pyfile('env.example')

#logging
logger = logging.getLogger(__name__)
if os.environ.get('LOGGING') == 'True':
    logging.basicConfig(level=logging.INFO)


#config
logger.info("Choosing config")
if os.environ.get('ENVIRONMENT') == 'Production':
    # Only cloudwatch log when app is in production mode.
    #handler = watchtower.CloudWatchLogHandler()
    handler = logging.StreamHandler()
    logger.info("Using production config")
    app.logger.addHandler(handler)
    app.config.from_object(config.ProductionConfig())
else:
    # Only log flask debug in development mode.
    logger.info("Using development config")
    logging.basicConfig(level=logging.DEBUG)
    handler = logging.StreamHandler()
    logging.getLogger("werkzeug").addHandler(handler)
    app.config.from_object(config.DevelopmentConfig())


#connect to ES
esConnecton = ElasticsearchClient((list('{0}'.format(s) for s in app.config['ES_SERVERS'].split(','))), 10)
logger.info(app.config['ES_SERVERS'])
logger.info(esConnecton.get_cluster_health())


@app.route('/info')
def info():
    """Return the JSONified user session for debugging."""
    return jsonify(
        clusterstatus=esConnecton.get_cluster_health()
    )

@app.route('/')
def main_page():
    return render_template("main_page.html")


@app.route("/vr/<path:filename>")
def vr_file(filename):
    return send_from_directory('vr/',
                               filename)

@app.route("/assets/<path:filename>")
def assets_file(filename):
    return send_from_directory('assets/',
                               filename)

# We only need this for local development.
if __name__ == '__main__':
    app.run()
