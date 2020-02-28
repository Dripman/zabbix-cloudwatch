# Zabbix AWS CloudWatch Monitoring
We make extensive use of AWS for several services.
Even though it provides monitoring on their platform we'd like to make use of our centralized monitoring & alerting based on Zabbix.

For this we have created several scripts to pull in information using the AWS CloudWatch API.

## Requirements
- Python 3
- boto (`pip install boto`)

## Usage
Add the desired scripts to externalscripts on your Zabbix Server

These macros are required for all templates.

|Macro|Example|Description|
|---	            |---	|---	|
|{$AWS_REGION}    |eu-west-1|The region the instance is located in|
|{$AWS_ACCESS_KEY}|AKAAAAAAAAAAAAAAAAAA|The accesskey of a user Cloudwatch permissions|
|{$AWS_SECRET_KEY}|xyzwefwejfijwefoijwefroiwjewef|The secret key for this IAM user|

### Application Loadbalancer
* Import the template
* Create a Zabbix Host for the Application Loadbalancer instance to monitor.
* Configure the global macros

In addition to the global macros, this template also requires the macros:

|Macro|Example|Description|
|---	            |---	|---	|
|{$AWS_ALB_LOADBALANCER_NAME}}    |app/example/2345892urwiejhrw|Name of the loadbalancer to monitor|
|{$AWS_ALB_TARGET_GROUP}}    |targetgroup/example/wefu238u23f2j3f|Name of the targetgroup to monitor|

### CloudFront
* Import the template
* Create a Zabbix Host with the Cloudwatch distribution to monitor.
* Configure the global macros

In addition to the global macros, this template also requires the macros:

|Macro|Example|Description|
|---	            |---	|---	|
|{$AWS_CF_DISTRIBUTION}    |test-distribution|Name of the Cloudfront distribution to monitor|
|{$AWS_CF_REGION}    |eu-west-1|The region the distribution is in|

### Elasticache (Redis)
* Import the template
* Create a Zabbix Host with the Elasticache (Redis) instance to monitor as "Host Name" (e.g. `myredis`). Visible name can be anything you'd like.
* Configure the global macros

### Elasticache
* Import the template
* Create a Zabbix Host with the Elasticache instance to monitor as "Host Name" (e.g. `mycache`). Visible name can be anything you'd like.
* Configure the global macros

### RDS
* Import the template
* Create a Zabbix Host for the RDS instance to monitor.
* Configure the global macros

In addition to the global macros, this template also requires the macros:

|Macro|Example|Description|
|---	            |---	|---	|
|{$RDS_INSTANCE_DISK}    |10|Provisioned size of the instance in GB (used in percentage counting)|

### S3
* Import the template
* Create a Zabbix Host with the S3 Bucket to monitor as "Host Name" (e.g. `mybucket`). Visible name can be anything you'd like.
* Configure the global macros

### VPC IPSec VPN
* Import the template
* Create a Zabbix Host with the VPN tunnel to monitor as "Host Name" (e.g. `vpn-di12491i4`). Visible name can be anything you'd like.
* Configure the global macros

## PR's
PR's are welcome to extend / improve functionality.

## Todo
* [ ] Implement dependent items instead of individual item polling
* [ ] Add Low Level Discovery functionality
