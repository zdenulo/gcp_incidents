
from settings import GCP_PROJECT_ID
from google.cloud import firestore
url = "https://status.cloud.google.com/incidents.json"

db = firestore.Client(project=GCP_PROJECT_ID)

item = {u'begin': u'2019-04-17T22:33:21Z',
        u'created': u'2019-04-17T22:33:21Z',
        u'end': u'2019-04-17T23:43:22Z',
        u'external_desc': u'OAuth login issues',
        u'modified': u'2019-04-18T00:07:05Z',
        u'most-recent-update': {u'created': u'2019-04-17T23:43:26Z',
                                u'modified': u'2019-04-17T23:43:26Z',
                                u'text': u'The issue with OAuth login has been resolved for all affected projects as of Wednesday, 2019-04-17 16:37 US/Pacific. We will conduct an internal investigation of this issue and make appropriate improvements to our systems to help prevent or minimize future recurrence.',
                                u'when': u'2019-04-17T23:43:26Z'},
        u'number': 19001,
        u'public': True,
        u'service_key': u'cloud-iam',
        u'service_name': u'Identity & Security',
        u'severity': u'medium',
        u'updates': [{u'created': u'2019-04-17T23:43:26Z',
                      u'modified': u'2019-04-17T23:43:26Z',
                      u'text': u'The issue with OAuth login has been resolved for all affected projects as of Wednesday, 2019-04-17 16:37 US/Pacific. We will conduct an internal investigation of this issue and make appropriate improvements to our systems to help prevent or minimize future recurrence.',
                      u'when': u'2019-04-17T23:43:26Z'},
                     {u'created': u'2019-04-17T23:33:16Z',
                      u'modified': u'2019-04-17T23:33:16Z',
                      u'text': u'The issue with OAuth login should be resolved for the majority of projects and we expect a full resolution in the near future. We will provide another status update by Wednesday, 2019-04-17 17:00 US/Pacific with current details.',
                      u'when': u'2019-04-17T23:33:16Z'},
                     {u'created': u'2019-04-17T22:55:12Z',
                      u'modified': u'2019-04-17T22:55:12Z',
                      u'text': u'The rate of OAuth login errors is decreasing. We will provide another status update by Wednesday, 2019-04-17 16:30 US/Pacific with current details.',
                      u'when': u'2019-04-17T22:55:12Z'},
                     {u'created': u'2019-04-17T22:33:23Z',
                      u'modified': u'2019-04-17T22:33:23Z',
                      u'text': u'We are continuing to investigate an issue with OAuth login. We will provide an update by Wednesday, 2019-04-17 16:00 US/Pacific.',
                      u'when': u'2019-04-17T22:33:23Z'},
                     {u'created': u'2019-04-17T22:33:22Z',
                      u'modified': u'2019-04-17T22:33:22Z',
                      u'text': u'OAuth login issues',
                      u'when': u'2019-04-17T22:33:22Z'}],
        u'uri': u'/incident/cloud-iam/19001'}

# service_key = item['service_key']
# number = item['number']
# key = '{}-{}'.format(service_key, number)
# col_ref = db.collection('incidents')
# doc_ref = col_ref.document(key)
# x = doc_ref.get()
#
# print(x.exists)
# print(x.to_dict())
# #
# # doc_ref.set(item)
# most_recent_new = item[u'most-recent-update']
# most_recent_db = x[u'most-recent-update']

import datetime
doc_ref = db.collection('tweets').document()
doc_ref.set({
    'text': 'hello',
    'created': datetime.datetime.utcnow()
})
