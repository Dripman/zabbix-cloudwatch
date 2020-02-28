#!/usr/bin/env python3
import datetime
import sys
from optparse import OptionParser

import boto.ec2.cloudwatch

parser = OptionParser()
parser.add_option("-i", "--instance-id", dest="instance_id",
                  help="DistributionIdentifier")
parser.add_option("-a", "--access-key", dest="access_key",
                  help="AWS Access Key")
parser.add_option("-k", "--secret-key", dest="secret_key",
                  help="AWS Secret Access Key")
parser.add_option("-m", "--metric", dest="metric",
                  help="CloudFront CloudWatch metric")
parser.add_option("-r", "--region", dest="region",
                  help="CloudFront region")

(options, args) = parser.parse_args()

if options.instance_id is None:
    parser.error("-i DistributionIdentifier is required")
if options.access_key is None:
    parser.error("-a AWS Access Key is required")
if options.secret_key is None:
    parser.error("-k AWS Secret Key is required")
if options.metric is None:
    parser.error("-m CloudWatch metric is required")

metrics = {"BytesUploaded": {"statistic": "Sum", "type": "float", "value": None},
           "BytesDownloaded": {"statistic": "Sum", "type": "float", "value": None},
           "Requests": {"statistic": "Sum", "type": "float", "value": None},
           "4xxErrorRate": {"statistic": "Average", "type": "float", "value": None},
           "5xxErrorRate": {"statistic": "Average", "type": "float", "value": None},
           "TotalErrorRate": {"statistic": "Average", "type": "float", "value": None},
           }
end = datetime.datetime.utcnow()
start = end - datetime.timedelta(minutes=5)

# get the region
if options.region is None:
    # Default region for CloudFront is US East (N. Virginia) since its a global service
    options.region = 'us-east-1'

for r in boto.ec2.cloudwatch.regions():
    if r.name == options.region:
        region = r
        break

conn = boto.ec2.cloudwatch.CloudWatchConnection(options.access_key, options.secret_key, region=region)

for metric_name, values in metrics.items():
    if metric_name == options.metric:

        try:
            res = conn.get_metric_statistics(60,
                                             start,
                                             end,
                                             metric_name,
                                             "AWS/CloudFront",
                                             values.get('statistic'),
                                             {
                                                 "DistributionId": options.instance_id,
                                                 "Region": "Global"
                                             })
        except Exception as e:
            print("status err Error running cloudfront_stats: %s" % e.error_message)
            exit(1)

        if len(res) > 0:
            average = res[-1][values.get('statistic')]  # last item in result set
        else:
            average = 0

        if values.get('type') == "float":
            metrics[metric_name]["value"] = "%.4f" % average
        if values.get('type') == "int" or values.get('type') == "boolean":
            metrics[metric_name]["value"] = "%i" % average

        # print "metric %s %s %s" % (k, vh["type"], vh["value"])
        print("%s" % (values.get('value')))
        exit(0)

print("Unknown metric '%s'" % options.metric)
exit(1)
