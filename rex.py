import re

text = 'asdasd Saturday 2020-10-08 asdas Friday, 2020-01-01 20:00 US/Pacific asds asdasd 2020-10-10 qqqqq wwwwww 2020-09-24 17:58 US/Pacific erqweqw\ndfasdfads\r\nasdadas'
# '( |(?:(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)? ?\d{4}-\d{2}-\d{2}))
# ((?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)?,?\s?(?:\d{4}-\d{2}-\d{2})\s(?:\d{2}:\d{2})?\s?(?:US/Pacific)?)  # good
regex = r"((?:(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)?,?\s?(?:\d{4}-\d{2}-\d{2})\s(?:\d{2}:\d{2})?\s?(?:US/Pacific)?)|(?:\s))"

text = """Resolved: Medium Cloud Machine Learning incident: Cloud ML was experiencing elevated errors https://status.cloud.google.com/incident/cloud-ml/20003 We were experiencing an issue with Cloud Machine Learning where deployments may fail and prediction operations were failing at elevated rates in us-central1 beginning on Tuesday, 2020-10-06 06:45 US/Pacific.

The issue with Cloud Machine Learning has been resolved for all affected users as of Tuesday, 2020-10-06 09:13 US/Pacific.

We thank you for your patience while we worked on resolving the issue."""
pattern = re.compile(r"""((?:(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)?,?\s?(?:\d{4}-\d{2}-\d{2})\s(?:\d{2}:\d{2})?\s?(?:US/Pacific)?)|(?:\.\s))""")

print(re.split(pattern, text))