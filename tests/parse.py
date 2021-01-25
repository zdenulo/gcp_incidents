import re
import unittest

from main import create_threads

# def create_threads(text, splitter='. '):
#     """Splits text into list of strings suitable to publish as Twitter message thread
#
#     :param text: Input text which will be tokenized
#     :return: list of strings
#     """
#
#     if len(text) <= 275:
#         return [text]
#     textr = re.sub(r'\r+\n+|\n+', '\n', text)
#     textr = textr.replace('.\n', splitter)
#     regex = r"((?:(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)?,?\s?(?:\d{4}-\d{2}-\d{2})\s(?:\d{2}:\d{2})?\s?(?:US/Pacific)?)|(?:\.\s))"
#     if splitter != '. ':
#         s_temp = textr.split(splitter)
#     else:
#         s_temp = re.split(regex, textr)
#
#     s = []
#     for x in s_temp:
#         x = x.strip()
#         if not x or x == '.':
#             continue
#         s.append(x)
#     out = []
#     t = ""
#     prev_date_split = False
#     total_s = len(s)
#     extra_tweets = None
#     for i, item in enumerate(s):
#         item = item.strip()
#         if extra_tweets:
#             extra_tweets_text = ' '.join(extra_tweets)
#             item = extra_tweets_text + ' ' + item
#             extra_tweets = None
#         if not t:
#             t_temp = item
#         else:
#             # t_temp = t + ". " + item
#             if prev_date_split and item[0].istitle():  # if date is at the end od sentence and next item is new one
#                 t_temp = t + '. ' + item
#                 prev_date_split = False
#             elif prev_date_split:
#                 t_temp = t + ' ' + item
#                 prev_date_split = False
#             elif re.match(regex, item):  # if it's split on date
#                 prev_date_split = True
#                 t_temp = t + ' ' + item
#             else:
#                 t_temp = t + splitter + item
#                 prev_date_split = False
#
#         t_temp = t_temp.strip()
#         len_t_temp = len(t_temp)
#         if len_t_temp <= 272:
#             t = t_temp
#             if i == (total_s - 1):
#                 out.append(t)
#         else:
#             if not t:
#                 t = t_temp
#             len_t = len(t)
#             if len_t > 272:
#                 mini_tweets = create_threads(t, ' ')
#                 out.append(mini_tweets[0])
#                 extra_tweets = mini_tweets[1:]
#             else:
#                 out.append(t)
#             if i == (total_s - 1):  # if it's last sentence append also as a tweet
#                 out.append(item)
#             elif not extra_tweets:
#                 t = item
#             else:  # in case there was recursions
#                 t = ''
#     return out

text = """Medium Google Cloud Functions incident: Some deployments to Google Cloud Functions using go113 runtime are failing https://status.cloud.google.com/incident/cloud-functions/20006 Description: We are experiencing an issue with Google Cloud Functions, affecting deployments using the "go113" runtime, beginning at Thursday, 2020-10-22 15:00 US/Pacific.

Our engineering team continues to investigate the issue.

We will provide an update by Friday, 2020-10-23 08:00 US/Pacific with current details.

We apologize to all who are affected by the disruption.

Diagnosis: Customers affected by this issue may see an error similar to the following:

ERROR: (gcloud.functions.deploy) OperationError: code=3, message=Build failed: # github.com/cloudevents/sdk-go/v2/extensions

src/github.com/cloudevents/sdk-go/v2/extensions/distributed_tracing_extension.go:161:3: cannot use span (type trace.Span) as type *trace.Span in return argument:

*trace.Span is pointer to interface, not interface; Error ID: 1093f764

Workaround: None at this time."""

# text = "High Google Cloud Infrastructure Components incident: Google Cloud services are experiencing issues and we have an other update at 5:30 PDT https://status.cloud.google.com/incident/zall/20013 Google Cloud services are experiencing issues and we have an other update at 5:30 PDT"

# with open('text.txt') as f:
#     text = f.read()

from twitter_threads import Threader
from TwitterAPI import TwitterAPI
from settings import GCP_PROJECT_ID
from settings import TWITTER_API_SECRET, TWITTER_TOKEN_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_API_KEY


# api = TwitterAPI(consumer_key=TWITTER_API_KEY,
#                  consumer_secret=TWITTER_API_SECRET,
#                  access_token_key=TWITTER_ACCESS_TOKEN,
#                  access_token_secret=TWITTER_TOKEN_SECRET)

class TestParsing(unittest.TestCase):

    def test_parse_1(self):
        text = """Description: Mitigation work is currently underway by our engineering team.

            The following zones are known to be impacted:
            
            asia-east1-a
            asia-east2-c
            asia-northeast1-a
            asia-northeast2-c
            asia-northeast3-c
            asia-south1-a
            asia-southeast1-a
            asia-southeast2-c
            australia-southeast1-a
            europe-west1-c
            europe-west2-a
            europe-west3-a
            europe-west6-c
            southamerica-east1-a
            us-central1-d
            us-east1-d
            us-west1-a
            us-west2-c
            us-west3-c
            us-west4-c
            
            We do not have an ETA for mitigation at this point.
            
            We will provide more information by Thursday, 2021-01-21 17:30 US/Pacific.
            
            Diagnosis: CNAME chasing between private zone to private zone is not working.
            
            Workaround: None at this time."""
        tweets = create_threads(text)
        self.assertEqual(len(tweets), 4)
        self.assertEqual(tweets[0], 'Description: Mitigation work is currently underway by our engineering team')
        self.assertEqual(tweets[1],
                         'The following zones are known to be impacted: asia-east1-a asia-east2-c asia-northeast1-a asia-northeast2-c asia-northeast3-c asia-south1-a asia-southeast1-a asia-southeast2-c australia-southeast1-a europe-west1-c europe-west2-a europe-west3-a europe-west6-c')
        self.assertEqual(tweets[2],
                         'southamerica-east1-a us-central1-d us-east1-d us-west1-a us-west2-c us-west3-c us-west4-c We do not have an ETA for mitigation at this point Thursday, 2021-01-21 17:30 US/Pacific. Diagnosis: CNAME chasing between private zone to private zone is not working')
        self.assertEqual(tweets[3], 'Workaround: None at this time.')

    def test_parse_2(self):
        text = "High Google Cloud Infrastructure Components incident: Google Cloud services are experiencing issues and we have an other update at 5:30 PDT https://status.cloud.google.com/incident/zall/20013 Google Cloud services are experiencing issues and we have an other update at 5:30 PDT"
        tweets = create_threads(text)
        self.assertEqual(len(tweets), 2)
        self.assertEqual(tweets[0],
                         'High Google Cloud Infrastructure Components incident: Google Cloud services are experiencing issues and we have an other update at 5:30 PDT https://status.cloud.google.com/incident/zall/20013 Google Cloud services are experiencing issues and we have an other update at',
                         'High Google Cloud Infrastructure Components incident: Google Cloud services are experiencing issues and we have an other update at 5:30 PDT https://status.cloud.google.com/incident/zall/20013 Google Cloud services are experiencing issues and we have an other update at 5:30 PDT')
        self.assertEqual(tweets[1], '5:30 PDT')
        # print(len(tweets[0]))
        # print(tweets)

    def test_parse_3(self):
        """ this should be keep newlines, i.e. function needs to be done better"""
        text = """Medium Google Cloud Functions incident: Some deployments to Google Cloud Functions using go113 runtime are failing https://status.cloud.google.com/incident/cloud-functions/20006 Description: We are experiencing an issue with Google Cloud Functions, affecting deployments using the "go113" runtime, beginning at Thursday, 2020-10-22 15:00 US/Pacific.

        Our engineering team continues to investigate the issue.

        We will provide an update by Friday, 2020-10-23 08:00 US/Pacific with current details.

        We apologize to all who are affected by the disruption.

        Diagnosis: Customers affected by this issue may see an error similar to the following:

        ERROR: (gcloud.functions.deploy) OperationError: code=3, message=Build failed: # github.com/cloudevents/sdk-go/v2/extensions

        src/github.com/cloudevents/sdk-go/v2/extensions/distributed_tracing_extension.go:161:3: cannot use span (type trace.Span) as type *trace.Span in return argument:

        *trace.Span is pointer to interface, not interface; Error ID: 1093f764

        Workaround: None at this time."""

        tweets = create_threads(text)
        self.assertEqual(len(tweets), 5)
        #
        self.assertEqual(tweets[0],
                         'Medium Google Cloud Functions incident: Some deployments to Google Cloud Functions using go113 runtime are failing https://status.cloud.google.com/incident/cloud-functions/20006 Description: We are experiencing an issue with Google Cloud Functions, affecting deployments')
        self.assertEqual(tweets[1],
                         'using the "go113" runtime, beginning at Thursday, 2020-10-22 15:00 US/Pacific. Our engineering team continues to investigate the issue. We will provide an update by Friday, 2020-10-23 08:00 US/Pacific with current details')
        self.assertEqual(tweets[2], 'We apologize to all who are affected by the disruption')
        self.assertEqual(tweets[3],
                         'Diagnosis: Customers affected by this issue may see an error similar to the following: ERROR: (gcloud.functions.deploy) OperationError: code=3, message=Build failed: # github.com/cloudevents/sdk-go/v2/extensions')
        self.assertEqual(tweets[4],
                         'src/github.com/cloudevents/sdk-go/v2/extensions/distributed_tracing_extension.go:161:3: cannot use span (type trace.Span) as type *trace.Span in return argument: *trace.Span is pointer to interface, not interface; Error ID: 1093f764 Workaround: None at this time.')


    def test_parse_4(self):
        text = """Description: We are experiencing an intermittent issue with Google Cloud infrastructure components, the issue manifests itself as periods of increased latency every 30 minutes, beginning at Tuesday, 2021-01-19 07:50:00 US/Pacific.

                     Our engineering team continues to investigate the issue.

                     We will provide an update by Tuesday, 2021-01-19 13:30 US/Pacific with current details.

                     Diagnosis: Cloud Networking traffic going through us-central1 and us-east1 shows increased latency.

                     Workaround: None at this time."""
        tweets = create_threads(text)
        # print(tweets)
        self.assertEqual(len(tweets), 3)
        self.assertEqual(tweets[0], 'Description: We are experiencing an intermittent issue with Google Cloud infrastructure components, the issue manifests itself as periods of increased latency every 30 minutes, beginning at Tuesday, 2021-01-19 07:50 :00 US/Pacific')
        self.assertEqual(tweets[1], 'Our engineering team continues to investigate the issue. We will provide an update by Tuesday, 2021-01-19 13:30 US/Pacific with current details. Diagnosis: Cloud Networking traffic going through us-central1 and us-east1 shows increased latency')
        self.assertEqual(tweets[2], 'Workaround: None at this time.')


    def test_parse_5(self):
        text = """Description: Mitigation work is still underway by our engineering team.

        The mitigation is expected to complete by Tuesday, 2021-01-19 12:00 US/Pacific.
        
        Please see the workaround section below for more details.
        
        Diagnosis: The command "gcloud components update" fails for Cloud SDK versions 321, 322 and 323 installed on Windows.
        
        Workaround: Please run the following commands in a PowerShell window:
        
        $gcloudDir = Get-Command gcloud | Select -ExpandProperty "Source" | Split-Path | Split-Path
        attrib -r "$gcloudDir\platform\kuberun_licenses*.*" /s
        attrib -r "$gcloudDir\lib\kuberun*.*" /s
        attrib -r "$gcloudDir..\google-cloud-sdk.staging\platform\kuberun_licenses*.*" /s
        attrib -r "$gcloudDir..\google-cloud-sdk.staging\lib\kuberun*.*" /s
        Remove-Item "$gcloudDir..\google-cloud-sdk.staging" -Recurse
        
        If any of the commands fail, proceed with running the remaining commands.
        
        After running the PowerShell script, run the following in a regular Command Prompt (not PowerShell):
        
        gcloud components update --version 320.0.0
        
        Please note, after applying this workaround, do not run 'gcloud components update' as this will re-trigger the issue. Please wait until the fix is released before updating components."""

        tweets = create_threads(text)
        print(tweets)

# Threader(tweets, api, wait=1)
# for l in tweets:
#     print(len(l), l)


if __name__ == '__main__':
    unittest.main()
