import boto3

def _create_session(aws_profile=None):
    
    if aws_profile:
        session = boto3.Session(profile_name=aws_profile)
    else:
        session = boto3.Session()

    return session