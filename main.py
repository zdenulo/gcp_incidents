import logging
import datetime
import requests
from TwitterAPI import TwitterAPI
from threader import Threader

from google.cloud import firestore
from flask import Flask

from settings import GCP_PROJECT_ID
from settings import TWITTER_API_SECRET, TWITTER_TOKEN_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_API_KEY

db = firestore.Client(project=GCP_PROJECT_ID)

api = TwitterAPI(consumer_key=TWITTER_API_KEY,
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
    :return: list of strings which can be published as Twitter messages
    """

    update_text = data['most-recent-update']['text']
    severity = data['severity'].capitalize()
    service_name = data['service_name']
    desc = data['external_desc']
    url = get_incident_url(data)
    end = data['end']
    if new:
        intro_text = f"{severity} {service_name} incident: {desc} #googlecloud {url}"
    elif end:
        intro_text = f"Resolved: {severity} {service_name} incident: {desc} #googlecloud {url}"
    else:
        intro_text = f"Update: {severity} {service_name} incident: {desc} #googlecloud {url}"

    threads = create_threads(intro_text + ' ' + update_text)
    # threads.insert(0, intro_text)
    print(f"intro text: {intro_text}")
    return threads


def tweet_message(tweets):
    """Post text to Twitter profile and saves info from Twitter to Firestore

    :param tweets: list of tweets
    :return:
    """

    print("tweets :{}".format(tweets))
    to_save = []
    if len(tweets) > 1:
        # send threaded tweets
        th = Threader(tweets, api, wait=1)
        th.send_tweets()
        responses = th.responses_
        for r in responses:
            resp = r.response
            json_data = resp.json()
            print("twitter response".format(json_data))
            to_save.append(json_data)
    else:
        params = {'status': tweets[0]}
        r = api.request('statuses/update', params=params)
        resp = r.response
        json_data = resp.json()
        to_save.append(json_data)
    tweet_ref = db.collection('tweets').document()
    tweet_ref.set({'threads': to_save, 'created': datetime.datetime.utcnow()})


def tweet(data, new):
    text_lst = format_text(data, new)
    print(text_lst)
    tweet_message(text_lst)


def create_threads(text):
    """Splits text into list of strings suitable to publish as Twitter message thread

    :param text: Input text which will be tokenized
    :return: list of strings
    """

    words = text.split(' ')
    threads = []
    t = ""
    run = True
    while run:
        while True:
            if not words:
                run = False
                threads.append(t)
                break
            w = words.pop(0).strip()
            if not w:
                continue
            if len(t) + len(w) < 275:
                t += w
                t += " "
            else:
                threads.append(t)
                t = w
                t += " "
                break
    return threads


@app.route('/tasks/status')
def status():
    r = requests.get(STATUS_URL)
    if r.status_code != 200:
        # status website is not working
        tweet_text = f"GCP status website returned response: {r.status_code} "
        error_msg = r.text[0:280 - len(tweet_text)]
        tweet_text += error_msg
        tweet_message([tweet_text])
        return 'ok'

    items = r.json()
    items = items[0:11]  # process only 10 most recent incidents
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
