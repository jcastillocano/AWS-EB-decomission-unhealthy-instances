# AWS-EB-decomission-unhealthyd-instances

Script to decomission unhealthy instances in a given AWS ElasticBeanstalk environment

## Requirements

 * AWS profile configured (see [Configuring the AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html)

## Install instructions

1. Create virtualenv `virtualenv -p python3 .venv`
2. Enable virtualenv `source .venv/bin/activate`
3. Install dependencies `pip install -r requirements.txt`

## Usage

```bash
$ python decomission.py -h
Terminate unhealthy beanstalk instances

Usage:
    decomission.py <environment_id> [options]

Options:
    -h --help       Show this screen
    -b, --batch N   Batch of instances to terminate [default: 1]
    -t, --terminate Terminate instances
```

Example without terminating the instances (done manually):

```bash
AWS_PROFILE=test  python decomission.py e-0000000 -b 1
Cluster e-0000000 is not healthy, running recovery
Instance i-1234 is in status Severe
Instance i-5678 is in status Severe
List of unhealthy instances": ['i-1234', 'i-5678']
Expectiong a total of 1 instances
Please, terminate ['i-1234'] instances
Total Ok instances 0, desired 1
Total Ok instances 0, desired 1
Total Ok instances 0, desired 1
Total Ok instances 0, desired 1
Please, terminate ['i-5678'] instances
Total Ok instances 1, desired 2
Total Ok instances 1, desired 2
Total Ok instances 1, desired 2
Total Ok instances 1, desired 2
Total Ok instances 1, desired 2
Environment e-0000000 is in good health
Everything went good, ready to redeploy
```

Add _-t_ (or _--terminate_) to leverage instance termination to the script.

## License

AGPL

## Authors

Juan Carlos Castillo <jccastillocano@gmail.com>
