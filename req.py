
import requests
import re
from main import get_incident_url

url = 'https://status.cloud.google.com/incidents.json'


def create_threads(text, splitter='. '):
    if len(text) <= 275:
        return [text]
    textr = re.sub(r'\r+\n+|\n+', '\n', text)
    textr = textr.replace('.\n', splitter)
    regex = r"((?:(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)?,?\s?(?:\d{4}-\d{2}-\d{2})\s(?:\d{2}:\d{2})?\s?(?:US/Pacific)?)|(?:\.\s))"
    if splitter != '. ':
        s_temp = textr.split(splitter)
    else:
        s_temp = re.split(regex, textr)

    s = []
    for x in s_temp:
        x = x.strip()
        if not x or x == '.':
            continue
        s.append(x)
    out = []
    t = ""
    prev_date_split = False
    total_s = len(s)
    extra_tweets = None
    for i, item in enumerate(s):
        item = item.strip()
        if extra_tweets:
            extra_tweets_text = ' '.join(extra_tweets)
            item = extra_tweets_text + ' ' + item
            extra_tweets = None
        if not t:
            t_temp = item
        else:
            # t_temp = t + ". " + item
            if prev_date_split and item[0].istitle(): # if date is at the end od sentence and next item is new one
                t_temp = t + '. ' + item
                prev_date_split = False
            elif prev_date_split:
                t_temp = t + ' ' + item
                prev_date_split = False
            elif re.match(regex, item):  # if it's split on date
                prev_date_split = True
                t_temp = t + ' ' + item
            else:
                t_temp = t + splitter + item
                prev_date_split = False

        t_temp = t_temp.strip()
        len_t_temp = len(t_temp)
        if len_t_temp <= 275:
            t = t_temp
            if i == (total_s - 1):
                out.append(t)
        else:
            if not t:
                t = t_temp
            len_t = len(t)
            if len_t > 275:
                mini_tweets = create_threads(t, ' ')
                out.append(mini_tweets[0])
                extra_tweets = mini_tweets[1:]
            else:
                out.append(t)
            if i == (total_s - 1):  # if it's last sentence append also as a tweet
                out.append(item)
            elif not extra_tweets:
                t = item
            else:  # in case there was recursions
                t = ''
    return out


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
        intro_text = f"{severity} {service_name} incident: {desc} {url}"
    elif end:
        intro_text = f"Resolved: {severity} {service_name} incident: {desc} {url}"
    else:
        intro_text = f"Update: {severity} {service_name} incident: {desc} {url}"
    full_text = intro_text + ' ' + update_text
    threads = create_threads(full_text)
    # threads.insert(0, intro_text)
    # print(f"intro text: {intro_text}")
    return threads

def format_multi(data, new=False):
    updates = data['updates']
    severity = data['severity'].capitalize()
    service_name = data['service_name']
    desc = data['external_desc']
    url = get_incident_url(data)
    end = data['end']
    if new:
        intro_text = f"{severity} {service_name} incident: {desc} {url}"
    elif end:
        intro_text = f"Resolved: {severity} {service_name} incident: {desc} {url}"
    else:
        intro_text = f"Update: {severity} {service_name} incident: {desc} {url}"
    for up in updates:
        update_text = up['text']
        full_text = intro_text + ' ' + update_text
        threads = create_threads(full_text)
        for i, t in enumerate(threads):
            l = len(t)
            print(f'#{i} {l} - {t}')
        print(f'{k} ###############################################################################')
    print(f'----------------------------------------------------------------------------------------------------------')



text = """Cloud Spanner has been affected by the Google incident https://status.cloud.google.com/incident/zall/20010 since 2020-09-24 17:58 US/Pacific. The issue was resolved for most traffic at 2020-09-24 18:33 US/Pacific."""
text = """Google Kubernetes Engine has been affected by the Google incident https://status.cloud.google.com/incident/zall/20010 since 2020-09-24 17:58 US/Pacific. The issue was resolved for most traffic at 2020-09-24 18:33 US/Pacific."""
text = """Cloud Networking has been affected by the Google incident https://status.cloud.google.com/incident/zall/20010 since 2020-09-24 17:58 US/Pacific. The issue was resolved for most traffic at 2020-09-24 18:33 US/Pacific."""

text = """Description: We are currently working to mitigate the issue of Cloud Composer create/update environment requests failing in asia-northeast1, asia-northeast2, asia-northeast3, asia-southeast1, europe-west1, europe-west3, europe-west6, europe-west4, northamerica-northeast1,southamerica-east1,us-central1, us-east1, us-west1, us-west2, and us-west4. .\n\nOur engineers are currently rolling back a configuration change to mitigate. \n\nWe will provide more information by Thursday, 2020-10-08 07:00 US/Pacific.\n\nDiagnosis: Create/update environment requests are failing. Existing workloads are unaffected.\n\nWorkaround: None at this time."""

# item = dict()
# item['most-recent-update'] = {'text': text}
# item['external_desc'] = 'We are currently working to mitigate the issue of Cloud Composer create/update environment requests failing in asia-northeast1, asia-northeast2, asia-northeast3, asia-southeast1, europe-west1, europe-west3, europe-west6, europe-west4, northamerica-northeast1, southamerica-east1,us-central1, us-east1, us-west1, us-west2, and us-west4.'
# item['end'] = True
# item['service_name'] = 'Google Cloud Composer'
# item['severity'] = 'Medium'
# item['uri'] = 'https://status.cloud.google.com/incident/cloud-networking/20009'
# ts = format_text(item, False)
# for i, t in enumerate(ts):
#     l = len(t)
#     print(f'#{i} {l} - {t}')


r = requests.get(url)
items = r.json()
items = items[:5]  # proc
for k, item in enumerate(items):
    format_multi(item, False)

    # tweets = format_text(item, False)
    # for i, t in enumerate(tweets):
    #     l = len(t)
    #     print(f'#{i} {l} - {t}')
    # print(f'{k} ###############################################################################')
