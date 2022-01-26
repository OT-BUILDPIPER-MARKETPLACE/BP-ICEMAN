import logging

class awsRDSActions:
    def __init__(self, client):
        self.client = client


    def _rds_perform_action(self,instance_ids,action):
        
        self.instance_ids = instance_ids
        self.action = action

        if action == "start":
        
            for id in instance_ids:
                try:
                    logging.info(f'Starting RDS instance : {id}')
                            
                    self.client.start_db_instance(
                                DBInstanceIdentifier=instance_id
                            )
                    
                    logging.info(f"Started rds instance : {id} succesfully")

                except ClientError as e:
                    logging.error(f'Facing issue in starting rds instance {id}. Error message: {e}')
    
        elif action == "stop":

            for instance_id in instance_ids:
                try:
                    logging.info(f'Stopping RDS instance : {instance_id}')

                    self.client.stop_db_instance(
                                DBInstanceIdentifier=instance_id
                            )
                    
                    logging.info(f"Stopped RDS instance : {instance_id}")

                except ClientError as e:
                    logging.error(f'Facing issue in stopping RDS instance {id}. Error message: {e}')

        else:
            logging.warning(f"Either Invalid action {action} provided or action {action} not supported")  
