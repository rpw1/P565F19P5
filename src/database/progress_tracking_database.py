import boto3
from boto3.dynamodb.conditions import Key
from decouple import config

class ProgressTrackingDatabase:

    def __init__(self, dynamodb = None):
        self.dynamodb = dynamodb
        self.tracking_table = None

    def check_database(self):
        if not self.dynamodb:
            self.dynamodb = boto3.resource(
                'dynamodb', 
                aws_access_key_id = config('AWS_ACCESS_KEY_ID'), 
                aws_secret_access_key = config('AWS_SECRET_ACCESS_KEY'),
                region_name = config('AWS_REGION')
                )
        self.tracking_table = self.dynamodb.Table('progress_tracking')