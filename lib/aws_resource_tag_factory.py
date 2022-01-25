
class getResoruceFinder:
    def __init__(self, client, service):
        self.service = service
        self.client = client


    def _get_resources_using_tags(self,tags):
        
        self.tags = tags

        if self.service == "ec2":
            return self._get_ec2_ids_using_tags(tags)
        
        elif self.service == "rds":
            return self._get_rds_ids_using_tags(tags)

        else:
            logging.warning(f"Invalid service {service} provided",extra=ADDITIONAL_LOG_DETAILS)            

    
    def _get_ec2_ids_using_tags(self,tags):
        
        filters = []
        ec2_ids = []

        for tag in tags:
            filters.append({'Name': 'tag:'+str(tag), 'Values': [str(tags[tag])]})

        response = self.client.describe_instances(
            Filters=filters
                        )
        
        for reservation in (response["Reservations"]):
            for ec2 in reservation["Instances"]:
                ec2_ids.append(ec2["InstanceId"])
        
        return ec2_ids
    
    def _get_rds_ids_using_tags(self,tags):

        dbs = self.client.describe_db_instances()
        rds_ids = []

        for db in dbs['DBInstances']:

            db_tags = self._get_tags_for_db(db)
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
                rds_ids.append(db["DBInstanceIdentifier"])
        
        return rds_ids


    def _get_tags_for_db(self, db):

        instance_arn = db['DBInstanceArn']
        instance_tags = self.client.list_tags_for_resource(ResourceName=instance_arn)
        return instance_tags['TagList']