#!/usr/bin/env python3
import datetime
from optparse import OptionParser

import boto.ec2.cloudwatch

# Arguments
parser = OptionParser()
parser.add_option("-i", "--instance-id", dest="instance_id",
                  help="CacheClusterId")
parser.add_option("-n", "--node-id", dest="node_id",
                  help="CacheNodeId")
parser.add_option("-a", "--access-key", dest="access_key",
                  help="AWS Access Key")
parser.add_option("-k", "--secret-key", dest="secret_key",
                  help="AWS Secret Access Key")
parser.add_option("-m", "--metric", dest="metric",
                  help="Elasticache cloudwatch metric")
parser.add_option("-r", "--region", dest="region",
                  help="Elasticache region")

(options, args) = parser.parse_args()

if options.instance_id is None:
    parser.error("-i CacheClusterId is required")
if options.access_key is None:
    parser.error("-a AWS Access Key is required")
if options.secret_key is None:
    parser.error("-k AWS Secret Key is required")
if options.metric is None:
    parser.error("-m Elasticache cloudwatch metric is required")

metrics = {
    # Host level
    "CPUUtilization": {"statistic": "Average", "type": "float", "value": None},
    "FreeableMemory": {"statistic": "Average", "type": "float", "value": None},
    "NetworkBytesIn": {"statistic": "Sum", "type": "float", "value": None},
    "NetworkBytesOut": {"statistic": "Sum", "type": "float", "value": None},
    "SwapUsage": {"statistic": "Average", "type": "float", "value": None},

    # Shared between Redis and Memcached
    "CurrConnections": {"statistic": "Average", "type": "int", "value": None},
    "Evictions": {"statistic": "Sum", "type": "int", "value": None},
    "Reclaimed": {"statistic": "Sum", "type": "int", "value": None},

    # Memcached
    "BytesReadIntoMemcached": {"statistic": "Sum", "type": "float", "value": None},
    "BytesUsedForCacheItems": {"statistic": "Average", "type": "float", "value": None},
    "BytesWrittenOutFromMemcached": {"statistic": "Sum", "type": "float", "value": None},
    "CasBadval": {"statistic": "Sum", "type": "int", "value": None},
    "CasHits": {"statistic": "Sum", "type": "int", "value": None},
    "CasMisses": {"statistic": "Sum", "type": "int", "value": None},
    "CmdFlush": {"statistic": "Average", "type": "int", "value": None},
    "CmdGet": {"statistic": "Average", "type": "int", "value": None},
    "CmdSet": {"statistic": "Average", "type": "int", "value": None},
    "CurrItems": {"statistic": "Average", "type": "int", "value": None},
    "DecrHits": {"statistic": "Sum", "type": "int", "value": None},
    "DecrMisses": {"statistic": "Sum", "type": "int", "value": None},
    "DeleteHits": {"statistic": "Sum", "type": "int", "value": None},
    "DeleteMisses": {"statistic": "Sum", "type": "int", "value": None},
    "GetHits": {"statistic": "Sum", "type": "int", "value": None},
    "GetMisses": {"statistic": "Sum", "type": "int", "value": None},
    "IncrHits": {"statistic": "Sum", "type": "int", "value": None},
    "IncrMisses": {"statistic": "Sum", "type": "int", "value": None},

    # For Memcached 1.4.14, the following additional metrics are provided.
    "BytesUsedForHash": {"statistic": "Average", "type": "float", "value": None},
    "CmdConfigGet": {"statistic": "Average", "type": "int", "value": None},
    "CmdConfigSet": {"statistic": "Average", "type": "int", "value": None},
    "CmdTouch": {"statistic": "Average", "type": "int", "value": None},
    "CurrConfig": {"statistic": "Average", "type": "int", "value": None},
    "EvictedUnfetched": {"statistic": "Sum", "type": "int", "value": None},
    "ExpiredUnfetched": {"statistic": "Sum", "type": "int", "value": None},
    "SlabsMoved": {"statistic": "Sum", "type": "int", "value": None},
    "TouchHits": {"statistic": "Sum", "type": "int", "value": None},
    "TouchMisses": {"statistic": "Sum", "type": "int", "value": None},

    # The AWS/ElastiCache namespace includes the following calculated cache-level metrics.
    "NewConnections": {"statistic": "Sum", "type": "int", "value": None},  # Also used by Redis
    "NewItems": {"statistic": "Sum", "type": "int", "value": None},
    "UnusedMemory": {"statistic": "Average", "type": "float", "value": None},

    # Redis
    "ActiveDefragHits": {"statistic": "Sum", "type": "int", "value": None},
    "BytesUsedForCache": {"statistic": "Average", "type": "float", "value": None},
    "CacheHits": {"statistic": "Sum", "type": "int", "value": None},
    "CacheMisses": {"statistic": "Sum", "type": "int", "value": None},
    "EngineCPUUtilization": {"statistic": "Average", "type": "float", "value": None},
    "HyperLogLogBasedCmds": {"statistic": "Average", "type": "int", "value": None},
    "ReplicationBytes": {"statistic": "Average", "type": "float", "value": None},
    "ReplicationLag": {"statistic": "Average", "type": "float", "value": None},
    "SaveInProgress": {"statistic": "Average", "type": "int", "value": None},

}
end = datetime.datetime.utcnow()
start = end - datetime.timedelta(minutes=5)

# get the region
if options.region is None:
    options.region = 'eu-west-1'

for r in boto.ec2.cloudwatch.regions():
    if r.name == options.region:
        region = r
        break

dimensions = dict()
if options.instance_id is not None:
    dimensions.update({"CacheClusterId": options.instance_id})
if options.node_id is not None:
    dimensions.update({"CacheNodeId": options.node_id})

conn = boto.ec2.cloudwatch.CloudWatchConnection(options.access_key, options.secret_key, region=region)

for metric_name, values in metrics.items():

    if metric_name == options.metric:

        try:
            res = conn.get_metric_statistics(60,
                                             start,
                                             end,
                                             metric_name,
                                             "AWS/ElastiCache",
                                             values.get('statistic'),
                                             dimensions
                                             )
        except Exception as err:
            print("status err Error running elasticache_stats: %s" % err)
            exit(1)

        if len(res) > 0:
            average = res[-1][values.get('statistic')]  # last item in result set
        else:
            average = 0

        if values.get('type') == "float":
            metrics[metric_name]["value"] = "%.4f" % average
        if values.get('type') == "int":
            metrics[metric_name]["value"] = "%i" % average

        # print("metric %s %s %s" % (metric_name, values.get('type'), values.get('value')))
        print("%s" % (values.get('value')))
        exit(0)

print("Unknown metric '%s'" % options.metric)
exit(1)
