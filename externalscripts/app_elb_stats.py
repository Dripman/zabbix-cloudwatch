#!/usr/bin/env python3
import datetime
from optparse import OptionParser

import boto.ec2.cloudwatch

# Arguments
parser = OptionParser()
parser.add_option("-i", "--instance-id", dest="instance_id",
                  help="Filter the metric data by load balancer.")
parser.add_option("-g", "--target-group", dest="target_group",
                  help="Filter the metric data by target group")
parser.add_option("-z", "--availability-zone", dest="availability_zone",
                  help="Filter the metric data by Availability Zone.")
parser.add_option("-a", "--access-key", dest="access_key",
                  help="AWS Access Key")
parser.add_option("-k", "--secret-key", dest="secret_key",
                  help="AWS Secret Access Key")
parser.add_option("-m", "--metric", dest="metric",
                  help="ELB cloudwatch metric")
parser.add_option("-r", "--region", dest="region",
                  help="AWS region")

(options, args) = parser.parse_args()

if options.instance_id is None and options.target_group is None and options.availability_zone is None:
    parser.error("At least LoadBalancerName, TargetGroup or AvailabilityZone is required")
if options.access_key is None:
    parser.error("-a AWS Access Key is required")
if options.secret_key is None:
    parser.error("-k AWS Secret Key is required")
if options.metric is None:
    parser.error("-m ELB cloudwatch metric is required")

metrics = {
    # ELB level
    "RequestCount": {"statistic": "Sum", "type": "int", "value": None},
    "ProcessedBytes": {"statistic": "Sum", "type": "float", "value": None},
    "IPv6RequestCount": {"statistic": "Sum", "type": "int", "value": None},
    "IPv6ProcessedBytes": {"statistic": "Sum", "type": "int", "value": None},
    "NewConnectionCount": {"statistic": "Sum", "type": "int", "value": None},
    "ActiveConnectionCount": {"statistic": "Sum", "type": "float", "value": None},
    "RejectedConnectionCount": {"statistic": "Sum", "type": "int", "value": None},
    "ClientTLSNegotiationErrorCount": {"statistic": "Sum", "type": "int", "value": None},
    "HTTPCode_ELB_4XX": {"statistic": "Sum", "type": "int", "value": None},
    "HTTPCode_ELB_5XX": {"statistic": "Sum", "type": "int", "value": None},

    # Target group level
    "HealthyHostCount": {"statistic": "Average", "type": "int", "value": None},
    "UnHealthyHostCount": {"statistic": "Average", "type": "int", "value": None},
    "TargetResponseTime": {"statistic": "Average", "type": "float", "value": None},
    "TargetConnectionErrorCount": {"statistic": "Sum", "type": "int", "value": None},
    "TargetTLSNegotiationErrorCount": {"statistic": "Sum", "type": "int", "value": None},
    "HTTPCode_Target_2XX_Count": {"statistic": "Sum", "type": "int", "value": None},
    "HTTPCode_Target_3XX_Count": {"statistic": "Sum", "type": "int", "value": None},
    "HTTPCode_Target_4XX_Count": {"statistic": "Sum", "type": "int", "value": None},
    "HTTPCode_Target_5XX_Count": {"statistic": "Sum", "type": "int", "value": None},
}

end = datetime.datetime.utcnow()
start = end - datetime.timedelta(minutes=5)

dimensions = dict()
if options.instance_id is not None:
    dimensions.update({"LoadBalancer": options.instance_id})
if options.availability_zone is not None:
    dimensions.update({"AvailabilityZone": options.availability_zone})
if options.target_group is not None:
    dimensions.update({"TargetGroup": options.target_group})

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
            res = conn.get_metric_statistics(60,
                                             start,
                                             end,
                                             metric_name,
                                             "AWS/ApplicationELB",
                                             values.get('statistic'),
                                             dimensions)
        except Exception as e:
            print("status err Error running elb_stats: %s" % e.error_message)
            exit(1)

        if len(res) > 0:
            average = res[-1][values.get('statistic')]  # last item in result set
        else:
            average = 0

        if values.get('type') == "float":
            metrics[metric_name]["value"] = "%.4f" % average
        if values.get('type') == "int":
            metrics[metric_name]["value"] = "%i" % average

        # print "metric %s %s %s" % (metric_name, values.get('type'), values.get('value'))
        print("%s" % (values.get('value')))
        exit(0)

print("Unknown metric '%s'" % options.metric)
exit(1)
