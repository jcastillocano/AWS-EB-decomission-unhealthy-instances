"""Redeploy unhealthy beanstalk instances

Usage:
    redeploy.py <environment_id> [options]

Options:
    -h --help       Show this screen
    -b, --batch N   Batch of instances to redeploy [default: 1]
    -d, --replace   Replace instances in batches
"""

import time
import boto3
from docopt import docopt


MAX_ENV_HEALTH_RETRIES = 10


def review_instances(instances):
    for instance in instances:
        print('Instance %s is in status %s' % (instance['InstanceId'], instance['HealthStatus']))
        if instance['HealthStatus'] in ['Degraded', 'Severe', 'NoData']:
            yield instance['InstanceId']


def get_next_token(response):
    if 'NextToken' in response:
        return response['NextToken']
    return False


def environment_health(client, environment_id):
    response = client.describe_environment_health(EnvironmentId=environment_id, AttributeNames=['HealthStatus'])
    if response['HealthStatus'] == 'Ok':
        print('Environment %s is in good health' % environment_id)
        return True
    return False


def environment_instance_health(client, environment_id):
    response = client.describe_environment_health(EnvironmentId=environment_id, AttributeNames=['InstancesHealth'])
    return response['InstancesHealth']


def query_instance_health(client, environment_id):
    unhealthy_instances = []
    response = client.describe_instances_health(EnvironmentId=environment_id, AttributeNames=['HealthStatus'])
    unhealthy_instances += review_instances(response['InstanceHealthList'])
    next_token = get_next_token(response)
    
    while next_token:
        response = client.describe_instances_health(EnvironmentId=environment_id, AttributeNames=['HealthStatus'], NextToken=next_token)
        unhealthy_instances += review_instances(response['InstanceHealthList'])
        next_token = get_next_token(response)

    print('List of unhealthy instances": %s' % unhealthy_instances)
    return unhealthy_instances

def terminate_unhealthy_instances(eb_client, environment_id, unhealthy_instances, batch_size=1, replace=False):
    instance_states = environment_instance_health(eb_client, environment_id)
    print('Expectiong a total of %d instances' % sum(instance_states.values()))
    total_ok = instance_states['Ok']

    ec2_client = boto3.client('ec2', region_name='us-west-2')
    for unhealthy_instances_batch in [unhealthy_instances[i:i + batch_size] for i in range(0, len(unhealthy_instances), batch_size)]:
        if replace:
            ec2_client.terminate_instances(instance_ids=unhealthy_intsances_batch)
        else:
            print('Please, terminate %s instances' % unhealthy_instances_batch) 

        time.sleep(60)
        retry_total = 0
        while instance_states['Ok'] != total_ok + len(unhealthy_instances_batch):
            print('Total Ok instances %d, desired %s' % ( instance_states['Ok'], total_ok  + len(unhealthy_instances_batch)))
            if retry_total > MAX_ENV_HEALTH_RETRIES:
                Exception('Recovered instances failed, please check env %s' % environment_id)
            time.sleep(30)
            retry_total += 1
            instance_states = environment_instance_health(eb_client, environment_id)
        total_ok += len(unhealthy_instances_batch)


    retry_total = 0
    while not environment_health(eb_client, environment_id):
        if retry_total > MAX_ENV_HEALTH_RETRIES:
            Exception('Cluster is not in a healthy state')
        time.sleep(20)
        retry_total += 1
    print('Everything went good, ready to redeploy')


def main(environment_id, batch_size, replace=False):
    eb_client = boto3.client('elasticbeanstalk', region_name='us-west-2')
    healthy = environment_health(eb_client, environment_id)
    if not healthy:
        print('Cluster %s is not healthy, running recovery' % environment_id)
        unhealthy_instances = query_instance_health(eb_client, environment_id)
        terminate_unhealthy_instances(eb_client, environment_id, unhealthy_instances, batch_size, replace)
    

if __name__ == '__main__':
    args = docopt(__doc__, version='Redeploy 0.1')
    main(args['<environment_id>'], int(args['--batch']), args['--replace'])
