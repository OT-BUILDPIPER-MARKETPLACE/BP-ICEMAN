import sys, os, argparse, logging, yaml, json
import json_log_formatter
import pathlib
import boto3
from botocore.exceptions import ClientError
SCRIPT_PATH = pathlib.Path(__file__).parent.resolve()
sys.path.insert(1, f'{SCRIPT_PATH}/../lib')
import load_yaml_config


CONF_PATH_ENV_KEY = "CONF_PATH"
LOG_PATH = "/ot/aws-resource-scheduler.log"

FORMATTER = json_log_formatter.VerboseJSONFormatter()
LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

FILE_HANDLER = logging.FileHandler(LOG_PATH)
STREAM_HANDLER = logging.StreamHandler(sys.stdout)

FILE_HANDLER.setFormatter(FORMATTER)
STREAM_HANDLER.setFormatter(FORMATTER)

LOGGER.addHandler(FILE_HANDLER)
LOGGER.addHandler(STREAM_HANDLER)

# import file
import aws_resources
import k8s_resources




def _schedule_Resources(args):

    LOGGER.info(f'Fetching properties from conf file: {args.property_file_path}.')

    properties = load_yaml_config._getProperty(args.property_file_path)

    LOGGER.info(f'Properties fetched from conf file.')

    if properties:

        for x in properties['actions_on']:
            
            if "k8s" in x.keys():
                if "context" in properties['k8s']:
                    k8s_context = properties['k8s']['context']
                else:
                    k8s_context = "minikube"
                k8s_resources._resourceManagerFactory(properties, k8s_context, args)

            elif "aws" in x.keys():
                if "aws_profile" in properties['aws']:
                    aws_profile = properties['aws']['aws_profile']
                else:
                    aws_profile = "default"
                aws_resources._scheduleFactory(properties, aws_profile, args)
       

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--property-file-path", help="Provide path of property file", default = os.environ[CONF_PATH_ENV_KEY], type=str)
    args = parser.parse_args()
    _schedule_Resources(args)