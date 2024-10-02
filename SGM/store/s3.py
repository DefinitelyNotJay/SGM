import boto3
import os
from dotenv import load_dotenv
from botocore.exceptions import ClientError
import logging


def get_client():
    load_dotenv()
    return boto3.client(
        's3',
        aws_access_key_id= os.getenv('aws_access_key_id'),
        aws_secret_access_key=os.getenv('aws_secret_access_key'),

            )

def get_resource():
    load_dotenv()
    return boto3.resource(
        's3',
        aws_access_key_id= os.getenv('aws_access_key_id'),
        aws_secret_access_key=os.getenv('aws_secret_access_key'),
        
            )

def upload_file(file_obj, bucket, object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    if object_name is None:
        object_name = file_obj.name

    s3_client = get_client()

    try:
        response = s3_client.upload_fileobj(file_obj, bucket, object_name)
        print(response)
    except ClientError as e:
        logging.error(e)
        return False
    return True


