#!/usr/bin/env python3
import datetime
from optparse import OptionParser

import boto.ec2.cloudwatch

# Arguments
parser = OptionParser()
parser.add_option("-i", "--instance-id", dest="instance_id",
                  help="BucketName")
parser.add_option("-s", "--storage-type", dest="storage_type",
                  help="StorageType")
parser.add_option("-a", "--access-key", dest="access_key",
                  help="AWS Access Key")
parser.add_option("-k", "--secret-key", dest="secret_key",
                  help="AWS Secret Access Key")
parser.add_option("-m", "--metric", dest="metric",
                  help="RDS cloudwatch metric")
parser.add_option("-r", "--region", dest="region",
                  help="RDS region")

(options, args) = parser.parse_args()

if options.instance_id is None:
    parser.error("-i BucketName is required")
if options.storage_type is None:
    parser.error("-s StorageType is required")
if options.access_key is None:
    parser.error("-a AWS Access Key is required")
if options.secret_key is None:
    parser.error("-k AWS Secret Key is required")
if options.metric is None:
    parser.error("-m RDS cloudwatch metric is required")

metrics = {
    # Amazon S3 CloudWatch Daily Storage Metrics for Buckets
    "BucketSizeBytes": {"statistic": "Average", "type": "float", "value": None, "minutes": 1440, "units": "Bytes"},
    "NumberOfObjects": {"statistic": "Average", "type": "float", "value": None, "minutes": 1440, "units": "Count"},

    # Amazon S3 CloudWatch Request metrics
    "AllRequests": {"statistic": "Sum", "type": "float", "value": None, "minutes": 5, "units": "Count"},
    "GetRequests": {"statistic": "Sum", "type": "float", "value": None, "minutes": 5, "units": "Count"},
    "PutRequests": {"statistic": "Sum", "type": "float", "value": None, "minutes": 5, "units": "Count"},
    "DeleteRequests": {"statistic": "Sum", "type": "float", "value": None, "minutes": 5, "units": "Count"},
    "HeadRequests": {"statistic": "Sum", "type": "float", "value": None, "minutes": 5, "units": "Count"},
    "PostRequests": {"statistic": "Sum", "type": "float", "value": None, "minutes": 5, "units": "Count"},
    "ListRequests": {"statistic": "Sum", "type": "float", "value": None, "minutes": 5, "units": "Count"},
    "BytesDownloaded": {"statistic": "Average", "type": "float", "value": None, "minutes": 5, "units": "Count"},
    "BytesUploaded": {"statistic": "Average", "type": "float", "value": None, "minutes": 5, "units": "Count"},
    "4xxErrors": {"statistic": "Average", "type": "int", "value": None, "minutes": 5, "units": "Count"},
    "5xxErrors": {"statistic": "Average", "type": "int", "value": None, "minutes": 5, "units": "Count"},
    "FirstByteLatency": {"statistic": "Average", "type": "float", "value": None, "minutes": 5, "units": "Milliseconds"},
    "TotalRequestLatency": {"statistic": "Average", "type": "float", "value": None, "minutes": 5,
                            "units": "Milliseconds"},
}

# get the region
if options.region is None:
    options.region = 'eu-west-1'

for r in boto.ec2.cloudwatch.regions():
    if r.name == options.region:
        region = r
        break

conn = boto.ec2.cloudwatch.CloudWatchConnection(options.access_key, options.secret_key, region=region)

for metric_name, values in metrics.items():

    if metric_name == options.metric:
        minutes = values.get('minutes', 5)
        end = datetime.datetime.utcnow()

        # Daily statistics can only be queried between 00:00 and 00:00, not based on the current hh:mm
        if values.get('minutes') == 1440:
            end = end.replace(hour=0, minute=0, second=0, microsecond=0)

        start = end - datetime.timedelta(minutes=values.get('minutes', 5))

        try:
            res = conn.get_metric_statistics(60,
                                             start,
                                             end,
                                             metric_name,
                                             "AWS/S3",
                                             values.get('statistic'),
                                             {
                                                 "BucketName": options.instance_id,
                                                 "StorageType": options.storage_type
                                             }
                                             )
        except Exception as e:
            print("status err Error running s3_stats: %s" % e.error_message)
            exit(1)

        if len(res) > 0:
            average = res[-1][values.get('statistic')]  # last item in result set
        else:
            average = 0

        if values.get('type') == "float":
            metrics[metric_name]["value"] = "%.4f" % average
        if values.get('type') == "int" or values.get('type') == "boolean":
            metrics[metric_name]["value"] = "%i" % average

        print("%s" % (values.get('value')))
        exit(0)

print("Unknown metric '%s'" % options.metric)
exit(1)
