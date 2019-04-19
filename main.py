
import logging

import requests
import twitter

from google.cloud import firestore
from flask import Flask

from settings import GCP_PROJECT_ID
from settings import TWITTER_API_SECRET, TWITTER_TOKEN_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_API_KEY

db = firestore.Client(project=GCP_PROJECT_ID)

api = twitter.Api(consumer_key=TWITTER_API_KEY,
                  consumer_secret=TWITTER_API_SECRET,
                  access_token_key=TWITTER_ACCESS_TOKEN,
                  access_token_secret=TWITTER_TOKEN_SECRET)

STATUS_URL = "https://status.cloud.google.com/incidents.json"

app = Flask(__name__)


def get_key(data):
    """construct key for Firestore document
    :param data: Dictionary containing info about incident
    :return string containing key
    """

    service_key = data['service_key']
    number = data['number']
    key = '{}-{}'.format(service_key, number)
    return key


def get_incident_url(data):
    """construct full url for incident detail
    :param data: Dictionary containing info about incident
    :return url
    """

    uri = data['uri']
    full_url = 'https://status.cloud.google.com{}'.format(uri)
    return full_url


def format_text(data, new):
    """Formats text which will be posted to Twitter, shortens if necessary

    :param data: Dictionary containing info about incident
    :param new: boolean, if True it means that incident is new
    :return: text which be posted to Twitter
    """

    update_text = data['most-recent-update']['text']
    severity = data['severity'].capitalize()
    service_name = data['service_name']
    url = get_incident_url(data)
    if new:
        man_len = len(" #googlecloud") + len(url) + 1 + len(severity) + 1 + len(service_name) + len(" incident:")
        status_text = update_text[0:280 - man_len]
        tweet_text = f"{severity} {service_name} incident: {status_text} #googlecloud {url}"
    else:
        man_len = len(" #googlecloud") + len(url) + 1 + len(service_name) + len(" incident:")
        status_text = update_text[0:280 - man_len]
        tweet_text = f"Update: {service_name} incident {status_text} #googlecloud {url}"
    return tweet_text


def tweet_message(tweet_text):
    """Post text to Twitter profile and saves info from Twitter to Firestore

    :param tweet_text: text of message
    :return:
    """

    try:
        twitter_response = api.PostUpdate(tweet_text)
        twitter_data_dict = twitter_response.AsDict()
        tweet_ref = db.collection('tweets').document()
        tweet_ref.set(twitter_data_dict)
    except Exception as e:
        logging.error(e)


def tweet(data, new):
    text = format_text(data, new)
    tweet_message(text)


@app.route('/tasks/status')
def status():
    r = requests.get(STATUS_URL)
    if r.status_code != 200:
        # status website is not working
        tweet_text = f"GCP status website returned response: {r.status_code} "
        error_msg = r.text[0:280 - len(tweet_text)]
        tweet_text += error_msg
        tweet_message(tweet_text)
        return 'ok'

    items = r.json()
    items = items[0:11]  # process only 10 most recent
    incidents_ref = db.collection('incidents')
    for item in items:
        key = get_key(item)
        doc_ref = incidents_ref.document(key)
        doc = doc_ref.get()
        if not doc.exists:
            # create new incident in db and tweet
            logging.info("new incident")
            logging.info(item)
            tweet(item, True)
            doc_ref.set(item)
        else:
            db_data = doc.to_dict()
            most_recent_new = item[u'most-recent-update']
            most_recent_db = db_data[u'most-recent-update']

            item_created = most_recent_new['created']
            db_created = most_recent_db['created']
            if item_created != db_created:
                # there is new update for existing incident, update db, tweet
                logging.info("updating incident")
                logging.info(item)
                tweet(item, False)
                doc_ref.set(item)

    return 'ok'


@app.route('/')
def main():
    return 'hello'


if __name__ == '__main__':
    app.run(port=8080)
