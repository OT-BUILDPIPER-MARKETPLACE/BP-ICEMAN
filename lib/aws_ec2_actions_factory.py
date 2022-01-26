import logging

class awsEC2Actions:
    def __init__(self, client):
        self.client = client


    def _ec2_perform_action(self,instance_ids,action):
        
        self.instance_ids = instance_ids
        self.action = action

        if action == "start":
        
            for id in instance_ids:
                try:
                    logging.info(f'Starting EC2 instance : {id}')
                            
                    self.client.start_instances(
                                InstanceIds=[id]
                            )
                    
                    logging.info(f"Started ec2 instance : {id} succesfully")

                except ClientError as e:
                    logging.error(f'Facing issue in starting ec2 instance {id}. Error message: {e}')
    
        elif action == "stop":

            for id in instance_ids:
                try:
                    logging.info(f'Stopping EC2 instance : {id}')
                            
                    self.client.start_instances(
                                InstanceIds=[id]
                            )
                    
                    logging.info(f"Stopped ec2 instance : {id} succesfully")

                except ClientError as e:
                    logging.error(f'Facing issue in stopping ec2 instance {id}. Error message: {e}')

        else:
            logging.warning(f"Either Invalid action {action} provided or action {action} not supported")  
