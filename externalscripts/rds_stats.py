#!/usr/bin/env python3
import datetime
import sys
from optparse import OptionParser

import boto.ec2.cloudwatch

### Arguments
parser = OptionParser()
parser.add_option("-i", "--instance-id", dest="instance_id",
                  help="DBInstanceIdentifier")
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
    parser.error("-i DBInstanceIdentifier is required")
if options.access_key is None:
    parser.error("-a AWS Access Key is required")
if options.secret_key is None:
    parser.error("-k AWS Secret Key is required")
if options.metric is None:
    parser.error("-m RDS cloudwatch metric is required")

metrics = {"CPUUtilization": {"type": "float", "value": None},
           "CPUCreditUsage": {"type": "int", "value": None},
           "CPUCreditBalance": {"type": "int", "value": None},
           "ReadLatency": {"type": "float", "value": None},
           "DatabaseConnections": {"type": "int", "value": None},
           "FreeableMemory": {"type": "float", "value": None},
           "ReadIOPS": {"type": "int", "value": None},
           "WriteLatency": {"type": "float", "value": None},
           "WriteThroughput": {"type": "float", "value": None},
           "WriteIOPS": {"type": "int", "value": None},
           "BinLogDiskUsage": {"type": "float", "value": None},
           "SwapUsage": {"type": "float", "value": None},
           "ReadThroughput": {"type": "float", "value": None},
           "ReplicaLag": {"type": "int", "value": None},
           "DiskQueueDepth": {"type": "float", "value": None},
           "NetworkReceiveThroughput": {"type": "float", "value": None},
           "NetworkTransmitThroughput": {"type": "float", "value": None},
           "FreeStorageSpace": {"type": "float", "value": None}}
end = datetime.datetime.utcnow()
start = end - datetime.timedelta(minutes=5)

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

        try:
            res = conn.get_metric_statistics(60, start, end, metric_name, "AWS/RDS", "Average",
                                             {"DBInstanceIdentifier": options.instance_id})
        except Exception as e:
            print("status err Error running rds_stats: %s" % e.error_message)
            exit(1)

        if len(res) > 0:
            average = res[-1]["Average"]  # last item in result set
        else:
            average = 0

        if metric_name == "FreeStorageSpace" or metric_name == "FreeableMemory":
            average = average / 1024.0 ** 3.0
        if values.get('type') == "float":
            metrics[metric_name]["value"] = "%.4f" % average
        if values.get('type') == "int":
            metrics[metric_name]["value"] = "%i" % average

        # print "metric %s %s %s" % (k, vh["type"], vh["value"])
        print("%s" % (values.get('value')))
        exit(0)

print("Unknown metric '%s'" % options.metric)
exit(1)
