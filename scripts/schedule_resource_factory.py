import sys, os, argparse, logging, yaml, json
import json_log_formatter
import pathlib
import boto3
from otfilesystemlibs import yaml_manager
import aws_resources
import k8s_resources
from botocore.exceptions import ClientError
import schedule_resource_logger


CONF_PATH_ENV_KEY = "CONF_PATH"
LOG_PATH = "/ot/aws-resource-scheduler.log"

LOGGER = schedule_resource_logger._get_logging(LOG_PATH)


def _schedule_Resources(args):

    LOGGER.info(f'Fetching properties from conf file: {args.property_file_path}.')

    yaml_loader = yaml_manager.getYamlLoader()
    properties = yaml_loader._loadYaml(args.property_file_path)

    LOGGER.info(f'Properties fetched from conf file.')

    if properties:

        for resources in properties['actions_on']:
            
            if "k8s" in resources.keys():
                if "context" in properties['k8s']:
                    k8s_context = properties['k8s']['context']
                else:
                    k8s_context = "minikube"

                if "deployment" in resources['k8s']:
                    k8s_resources._resourceManagerFactory(properties, k8s_context, "deployment", args)
                if "sts" in resources['k8s']:
                    k8s_resources._resourceManagerFactory(properties, k8s_context, "sts", args)

            elif "aws" in resources.keys():
                if "aws_profile" in properties['aws']:
                    aws_profile = properties['aws']['aws_profile']
                else:
                    aws_profile = "default"
                    
                if "ec2" in resources['aws']:
                    aws_resources._scheduleFactory(properties, aws_profile, "ec2", args)
                if "rds" in resources['aws']:
                    aws_resources._scheduleFactory(properties, aws_profile, "rds", args)
                
       

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--property-file-path", help="Provide path of property file", default = os.environ[CONF_PATH_ENV_KEY], type=str)
    args = parser.parse_args()
    _schedule_Resources(args)