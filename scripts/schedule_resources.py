#!/usr/bin/env python3

import os, yaml, argparse, logging, json
import boto3
from botocore.exceptions import ClientError
        

SCHEULE_ACTION_ENV_KEY = "SCHEDULE_ACTION"
CONF_PATH_ENV_KEY = "CONF_PATH"
LOG_PATH = "/var/log/ot/aws-resource-scheduler.log"
ADDITIONAL_LOG_DETAILS={'ec2_ids':'[]', 'rds_ids':'[]'}

LOGGER = logging.getLogger("imported_module")
LOGGER.setLevel(logging.INFO)

FILE_HANDLER = logging.FileHandler(LOG_PATH)
STREAM_HANDLER = logging.StreamHandler()

STREAM_FORMATTER = logging.Formatter(json.dumps(
    {'time': '%(asctime)s', 'level': '%(levelname)s', 'function name ':'%(funcName)s','process': 'p%(process)s','line no':'%(lineno)d','ec2_ids': '%(ec2_ids)s','rds_ids': '%(rds_ids)s','message': '%(message)s'}))
FILE_FORMATTER = logging.Formatter(json.dumps(
    {'time': '%(asctime)s', 'level': '%(levelname)s', 'function name ':'%(funcName)s','process': 'p%(process)s','line no':'%(lineno)d','ec2_ids': '%(ec2_ids)s','rds_ids': '%(rds_ids)s','message': '%(message)s'}))

FILE_HANDLER.setFormatter(FILE_FORMATTER)
STREAM_HANDLER.setFormatter(STREAM_FORMATTER)
LOGGER.addHandler(FILE_HANDLER)
LOGGER.addHandler(STREAM_HANDLER)


def _getProperty(property_file_path):  
    
    try: 
        load_property = open(property_file_path)
        parse_yaml = yaml.load(load_property, Loader=yaml.FullLoader)
        LOGGER.info(f"Loaded conf file succesfully.",extra=ADDITIONAL_LOG_DETAILS)
        return parse_yaml
    except FileNotFoundError:
        LOGGER.error(f"Unable to find conf file {property_file_path}. Please mention correct property file path.",extra=ADDITIONAL_LOG_DETAILS)
        exit()

    return None

def _fetch_instance_ids(client, service, tags):

    filters = []
    instance_ids = []
    
    if service == "ec2":

        for tag in tags:
            filters.append({'Name': 'tag:'+str(tag), 'Values': [str(tags[tag])]})

        response = client.describe_instances(
            Filters=filters
                        )
        
        for reservation in (response["Reservations"]):
            for instance in reservation["Instances"]:
                instance_ids.append(instance["InstanceId"])

    
    elif service == "rds":
        dbs = client.describe_db_instances()
        instance_ids = []

        for db in dbs['DBInstances']:

            db_tags = _get_tags_for_db(client,db)
            tag_found = False
            
            for tag in tags:
                for db_tag in db_tags:
                    if db_tag['Key'] == tag and db_tag['Value'] == tags[tag]:
                        tag_found = True
                        break
                    else:
                        tag_found = False
                        continue

                if not tag_found:
                    break
                else:
                    continue

            if tag_found:
                instance_ids.append(db["DBInstanceIdentifier"])

    else:
        logging.warning(f"Invalid service {service} provided",extra=ADDITIONAL_LOG_DETAILS)            
        
    return instance_ids

def _get_tags_for_db(client, db):

    instance_arn = db['DBInstanceArn']
    instance_tags = client.list_tags_for_resource(ResourceName=instance_arn)
    return instance_tags['TagList']


def _start_ec2(ec2_client,instance_ids,ec2_id_details):

        for id in instance_ids:

            try:

                LOGGER.info(f'Starting EC2 instance : {id}',extra=ec2_id_details)
                        
                start_ec2 = ec2_client.start_instances(
                            InstanceIds=[id]
                        )
                
                LOGGER.info(f"Started ec2 instance : {id} succesfully",extra=ec2_id_details)

            except ClientError as e:
                LOGGER.error(f'Facing issue in starting ec2 instance {id}. Error message: {e}',extra=ec2_id_details)

    
def _stop_ec2(ec2_client,instance_ids,ec2_id_details):

        for id in instance_ids:
            try:      
                LOGGER.info(f'Stopping EC2 instance : {id}',extra=ec2_id_details)
                        
                start_ec2 = ec2_client.stop_instances(
                            InstanceIds=[id]
                        )
                
                LOGGER.info(f"Stopped EC2 instance : {id} succesfully",extra=ec2_id_details)

            except ClientError as e:
                LOGGER.error(f'Facing issue in stopping EC2 instance {id}. Error message: {e}',extra=ec2_id_details)


def _start_rds(rds_client,instance_ids,rds_id_details):

        for instance_id in instance_ids:
            try:
                LOGGER.info(f'Starting RDS instance : {instance_id}',extra=rds_id_details)

                start_rds = rds_client.start_db_instance(
                            DBInstanceIdentifier=instance_id
                        )
                
                LOGGER.info(f"Started RDS instance : {instance_id}",extra=rds_id_details)

            except ClientError as e:
                LOGGER.error(f'Facing issue in starting RDS instance {id}. Error message: {e}',extra=rds_id_details)



def _stop_rds(rds_client,instance_ids,rds_id_details):

        for instance_id in instance_ids:
            try:
                LOGGER.info(f'Stopping RDS instance : {instance_id}',extra=rds_id_details)

                stop_rds = rds_client.stop_db_instance(
                            DBInstanceIdentifier=instance_id
                        )
                
                LOGGER.info(f"Stopped RDS instance : {instance_id}",extra=rds_id_details)

            except ClientError as e:
                LOGGER.error(f'Facing issue in stopping RDS instance {id}. Error message: {e}',extra=rds_id_details)



def _scheduleFactory(properties, aws_profile, args):

    instance_ids = []

    try:
        
        LOGGER.info(f'Connecting to AWS.',extra=ADDITIONAL_LOG_DETAILS)
        
        if aws_profile:
            session = boto3.Session(profile_name=aws_profile)
        else:
            session = boto3.Session()

        LOGGER.info(f'Connection to AWS established.',extra=ADDITIONAL_LOG_DETAILS)

        for property in properties:

            if property == "ec2_tags":
                
                LOGGER.info(f'Reading Ec2 tags',extra=ADDITIONAL_LOG_DETAILS)

                ec2_tags = properties['ec2_tags']
                
                if ec2_tags:

                    LOGGER.info(f'Found Ec2 tags details for filtering : {ec2_tags}',extra=ADDITIONAL_LOG_DETAILS)

                    ec2_client = session.client("ec2", region_name=properties['region'])

                    LOGGER.info(f'Scanning AWS EC2 resources in {properties["region"]} region based on tags {ec2_tags} provided',extra=ADDITIONAL_LOG_DETAILS)

                    instance_ids = _fetch_instance_ids(ec2_client, "ec2", ec2_tags)

                    ec2_id_details= {'ec2_ids' : f'{instance_ids}' , 'rds_ids': '[]'}

                    if instance_ids:

                        LOGGER.info(f'Found AWS EC2 resources {instance_ids} in  {properties["region"]} region based on tags provided: {ec2_tags}',extra=ec2_id_details)

                        if os.environ[SCHEULE_ACTION_ENV_KEY] == "start":
                            
                            _start_ec2(ec2_client,instance_ids,ec2_id_details)

                        elif os.environ[SCHEULE_ACTION_ENV_KEY] == "stop":

                            _stop_ec2(ec2_client,instance_ids,ec2_id_details)

                        else:
                            logging.error(f"{SCHEULE_ACTION_ENV_KEY} env not set",extra=ec2_id_details)

                    else:
                        LOGGER.warning(f'No Ec2 instances found on the basis of tag filters provided in conf file in region {properties["region"]} ',extra=ec2_id_details)
                else:
                    LOGGER.warning(f'Found ec2_tags key in config file but no Ec2 tags details mentioned for filtering',extra=ec2_id_details)

               

                
            elif property == "rds_tags":

                LOGGER.info(f'Reading RDS tags',extra=ADDITIONAL_LOG_DETAILS)

                rds_tags = properties['rds_tags']

                if rds_tags:

                    LOGGER.info(f'Found RDS tags details for filtering : {rds_tags}',extra=ADDITIONAL_LOG_DETAILS)

                    rds_client = session.client("rds", region_name=properties['region'])

                    LOGGER.info(f'Scanning AWS RDS resources in {properties["region"]} region based on tags {rds_tags} provided',extra=ADDITIONAL_LOG_DETAILS)

                    instance_ids = _fetch_instance_ids(rds_client, "rds", rds_tags)

                    rds_id_details= {'ec2_ids' : '[]' , 'rds_ids' : instance_ids }

                    if instance_ids:

                        if os.environ[SCHEULE_ACTION_ENV_KEY] == "start":

                            _start_rds(rds_client,instance_ids,rds_id_details)

                        elif os.environ[SCHEULE_ACTION_ENV_KEY] == "stop":
                            
                            _stop_rds(rds_client,instance_ids,rds_id_details)

                        else:
                            logging.error(f"{SCHEULE_ACTION_ENV_KEY} env not set",extra=rds_id_details)
                    
                    else:
                        LOGGER.warning(f'No RDS instances found on the basis of tag filters provided in conf file in region {properties["region"]} ',extra=ADDITIONAL_LOG_DETAILS)
                else:
                    LOGGER.warning(f'Found rds_tags key in config file but no RDS tags details mentioned for filtering',extra=ADDITIONAL_LOG_DETAILS)
                
            else:
                LOGGER.info("Scanning AWS service details in config",extra=ADDITIONAL_LOG_DETAILS)
                
            

    except ClientError as e:
        if "An error occurred (AuthFailure)" in str(e):
            raise Exception('AWS Authentication Failure!!!! .. Please mention valid AWS profile in property file or use valid IAM role ').with_traceback(e.__traceback__)    
        else:
            raise e
    except KeyError as e:
        raise Exception(f'Failed fetching env {SCHEULE_ACTION_ENV_KEY} value. Please add this env variable').with_traceback(e.__traceback__)    



def _scheduleResources(args):

    LOGGER.info(f'Fetching properties from conf file: {args.property_file_path}.',extra=ADDITIONAL_LOG_DETAILS)

    properties = _getProperty(args.property_file_path)

    LOGGER.info(f'Properties fetched from conf file.',extra=ADDITIONAL_LOG_DETAILS)

    if properties:
        if "aws_profile" in properties:
            aws_profile = properties['aws_profile']
        else:
            aws_profile = None
        _scheduleFactory(properties, aws_profile, args)
       

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--property-file-path", help="Provide path of property file", default = os.environ[CONF_PATH_ENV_KEY], type=str)
    args = parser.parse_args()
    _scheduleResources(args)

