import os
import schedule_resource_logger
from otawslibs import generate_aws_session , aws_resource_tag_factory , aws_ec2_actions_factory , aws_rds_actions_factory
from botocore.exceptions import ClientError

SCHEULE_ACTION_ENV_KEY = "AWS_SCHEDULE_ACTION"
LOG_PATH = "/var/log/ot/aws-resource-scheduler.log"

LOGGER = schedule_resource_logger._get_logging(LOG_PATH)


def _fetch_instance_ids(client, service, tags):

    aws_resource_finder = aws_resource_tag_factory.getResoruceFinder(client,service)
    instance_ids = aws_resource_finder._get_resources_using_tags(tags)

    return instance_ids

def _schedule_ec2(properties, session , args):

    for property in properties['aws']:

        if property == "ec2_tags":

            LOGGER.info(f'Reading Ec2 tags')

            ec2_tags = properties['aws']['ec2_tags']

            if ec2_tags:

                LOGGER.info(f'Found Ec2 tags details for filtering : {ec2_tags}')

                ec2_client = session.client("ec2", region_name=properties['aws']['region'])
                aws_ec2_action = aws_ec2_actions_factory.awsEC2Actions(ec2_client)


                LOGGER.info(f'Scanning AWS EC2 resources in {properties["aws"]["region"]} region based on tags {ec2_tags} provided')

                instance_ids = _fetch_instance_ids(ec2_client, "ec2", ec2_tags)

                if instance_ids:

                    LOGGER.info(f'Found AWS EC2 resources {instance_ids} in  {properties["aws"]["region"]} region based on tags provided: {ec2_tags}',extra={"ec2_ids": instance_ids})

                    if os.environ[SCHEULE_ACTION_ENV_KEY] == "start":

                        aws_ec2_action._ec2_perform_action(instance_ids,action="start")

                    elif os.environ[SCHEULE_ACTION_ENV_KEY] == "stop":

                        aws_ec2_action._ec2_perform_action(instance_ids,action="stop")

                    else:
                        logging.error(f"{SCHEULE_ACTION_ENV_KEY} env not set")

                else:
                    LOGGER.warning(f'No Ec2 instances found on the basis of tag filters provided in conf file in region {properties["aws"]["region"]} ',extra={"ec2_ids": instance_ids})
            else:
                LOGGER.warning(f'Found ec2_tags key in config file but no Ec2 tags details mentioned for filtering',extra={"ec2_ids": instance_ids})


def _schedule_rds(properties, session , args):

    for property in properties['aws']:
        if property == "rds_tags":

            LOGGER.info(f'Reading RDS tags')

            rds_tags = properties['aws']['rds_tags']

            if rds_tags:

                LOGGER.info(f'Found RDS tags details for filtering : {rds_tags}')

                rds_client = session.client("rds", region_name=properties['aws']['region'])

                aws_rds_action = aws_rds_actions_factory.awsRDSActions(rds_client)

                LOGGER.info(f'Scanning AWS RDS resources in {properties["aws"]["region"]} region based on tags {rds_tags} provided')

                instance_ids = _fetch_instance_ids(rds_client, "rds", rds_tags)

                if instance_ids:

                    LOGGER.info(f'Found AWS RDS resources {instance_ids} in  {properties["aws"]["region"]} region based on tags provided: {rds_tags}',extra={"rds_ids": instance_ids})

                    if os.environ[SCHEULE_ACTION_ENV_KEY] == "start":

                        aws_rds_action._rds_perform_action(instance_ids,action="start")

                    elif os.environ[SCHEULE_ACTION_ENV_KEY] == "stop":

                        aws_rds_action._rds_perform_action(instance_ids,action="stop")

                    else:
                        logging.error(f"{SCHEULE_ACTION_ENV_KEY} env not set")

                else:
                    LOGGER.warning(f'No RDS instances found on the basis of tag filters provided in conf file in region {properties["aws"]["region"]} ',extra={"rds_ids": instance_ids})
            else:
                LOGGER.warning(f'Found rds_tags key in config file but no RDS tags details mentioned for filtering',extra={"rds_ids": instance_ids})

        else:
            LOGGER.info("Scanning AWS service details in config")


def _scheduleFactory(properties, aws_profile, resource_type , args):

    instance_ids = []

    try:

        LOGGER.info(f'Connecting to AWS.')

        if aws_profile:
            session = generate_aws_session._create_session(aws_profile)
        else:
            session = generate_aws_session._create_session()

        LOGGER.info(f'Connection to AWS established.')

        if resource_type == "ec2":
            _schedule_ec2(properties, session , args)
        elif resource_type == "rds":
            _schedule_rds(properties, session , args)
        else:
            LOGGER.info(f'Invalid Resource type provided. Valid values: [ec2,rds]')

    except ClientError as e:
        if "An error occurred (AuthFailure)" in str(e):
            raise Exception('AWS Authentication Failure!!!! .. Please mention valid AWS profile in property file or use valid IAM role ').with_traceback(e.__traceback__)    
        else:
            raise e
    except KeyError as e:
        raise Exception(f'Failed fetching env {SCHEULE_ACTION_ENV_KEY} value. Please add this env variable').with_traceback(e.__traceback__)    


