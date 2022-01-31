#!/usr/bin/env python3

import sys, os, argparse, logging, yaml, json
import json_log_formatter
import boto3
from botocore.exceptions import ClientError
from otawslibs import generate_aws_session , aws_resource_tag_factory , aws_ec2_actions_factory , aws_rds_actions_factory
from otfilesystemlibs import yaml_manager

SCHEULE_ACTION_ENV_KEY = "SCHEDULE_ACTION"
CONF_PATH_ENV_KEY = "CONF_PATH"
LOG_PATH = "/var/log/ot/aws-resource-scheduler.log"

FORMATTER = json_log_formatter.VerboseJSONFormatter()
LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

FILE_HANDLER = logging.FileHandler(LOG_PATH)
STREAM_HANDLER = logging.StreamHandler(sys.stdout)

FILE_HANDLER.setFormatter(FORMATTER)
STREAM_HANDLER.setFormatter(FORMATTER)

LOGGER.addHandler(FILE_HANDLER)
LOGGER.addHandler(STREAM_HANDLER)


def _awsResourceManagerFactory(properties, aws_profile, args):

    instance_ids = []
            
    try:
        
        LOGGER.info(f'Connecting to AWS.')

        if aws_profile:
            session = generate_aws_session._create_session(aws_profile)
        else:
            session = generate_aws_session._create_session()

        LOGGER.info(f'Connection to AWS established.')

        for resource_type in properties:

            if resource_type == "ec2_tags":
                
                LOGGER.info(f'Reading Ec2 tags')

                ec2_tags = properties['ec2_tags']
                
                if ec2_tags:

                    LOGGER.info(f'Found Ec2 tags details for filtering : {ec2_tags}')

                    ec2_client = session.client("ec2", region_name=properties['region'])

                    LOGGER.info(f'Scanning AWS EC2 resources in {properties["region"]} region based on tags {ec2_tags} provided')

                    aws_resource_finder = aws_resource_tag_factory.getResoruceFinder(ec2_client,"ec2")
                    instance_ids = aws_resource_finder._get_resources_using_tags(ec2_tags)

                    if instance_ids:

                        LOGGER.info(f'Found AWS EC2 resources {instance_ids} in  {properties["region"]} region based on tags provided: {ec2_tags}',extra={"ec2_ids": instance_ids})

                        aws_ec2_action_manager = aws_ec2_actions_factory.awsEC2Actions(ec2_client)         
                        aws_ec2_action_manager._ec2_perform_action(instance_ids,action=os.environ[SCHEULE_ACTION_ENV_KEY])

                    else:
                        LOGGER.warning(f'No Ec2 instances found on the basis of tag filters provided in conf file in region {properties["region"]} ',extra={"ec2_ids": instance_ids})
                else:
                    LOGGER.warning(f'Found ec2_tags key in config file but no Ec2 tags details mentioned for filtering',extra={"ec2_ids": instance_ids})

               

                
            elif resource_type == "rds_tags":

                LOGGER.info(f'Reading RDS tags')

                rds_tags = properties['rds_tags']

                if rds_tags:

                    LOGGER.info(f'Found RDS tags details for filtering : {rds_tags}')

                    rds_client = session.client("rds", region_name=properties['region'])

                    LOGGER.info(f'Scanning AWS RDS resources in {properties["region"]} region based on tags {rds_tags} provided')

                    aws_resource_finder = aws_resource_tag_factory.getResoruceFinder(rds_client,"rds")
                    instance_ids = aws_resource_finder._get_resources_using_tags(rds_tags)

                    if instance_ids:

                        LOGGER.info(f'Found AWS RDS resources {instance_ids} in  {properties["region"]} region based on tags provided: {rds_tags}',extra={"rds_ids": instance_ids})

                        aws_rds_action_manager = aws_rds_actions_factory.awsRDSActions(rds_client)
                        aws_rds_action_manager._rds_perform_action(instance_ids,action=os.environ[SCHEULE_ACTION_ENV_KEY])

                    else:
                        LOGGER.warning(f'No RDS instances found on the basis of tag filters provided in conf file in region {properties["region"]} ',extra={"rds_ids": instance_ids})
                else:
                    LOGGER.warning(f'Found rds_tags key in config file but no RDS tags details mentioned for filtering',extra={"rds_ids": instance_ids})
                
            else:
                LOGGER.info("Scanning AWS service details in config")
                
            

    except ClientError as e:
        if "An error occurred (AuthFailure)" in str(e):
            raise Exception('AWS Authentication Failure!!!! .. Please mention valid AWS profile in property file or use valid IAM role ').with_traceback(e.__traceback__)    
        else:
            raise e
    except KeyError as e:
        raise Exception(f'Failed fetching env {SCHEULE_ACTION_ENV_KEY} value. Please add this env variable').with_traceback(e.__traceback__)    



def _scheduleAWSResources(args):

    LOGGER.info(f'Fetching properties from conf file: {args.property_file_path}.')

    yaml_loader = yaml_manager.getYamlLoader()
    properties = yaml_loader._loadYaml(args.property_file_path)

    LOGGER.info(f'Properties fetched from conf file.')

    if properties:
        if "aws_profile" in properties:
            aws_profile = properties['aws_profile']
        else:
            aws_profile = None
        _awsResourceManagerFactory(properties, aws_profile, args)
       

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--property-file-path", help="Provide path of property file", default = os.environ[CONF_PATH_ENV_KEY], type=str)
    args = parser.parse_args()
    _scheduleAWSResources(args)