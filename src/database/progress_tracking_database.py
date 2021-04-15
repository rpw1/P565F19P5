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
    
    def insert_content(self, email, content = dict()):
        """
            email -> required, string \n
            content ->
            {
                weekly_cals: ""
                weekly_calorie_goal: ""
                weekly_calorie_total: ""
                has_been_reset: ""
                history: ""
            }
        """
        self.check_database()
        response = self.tracking_table.put_item(
            Item = {
                'email': email,
                'content': content
            }
        )

    def get_content(self, email):
        self.check_database
        result = self.tracking_table.get_item(
            Key = {
                "email": email
            }
        )
        if 'Item' in result:
            return result['Item']
        else:
            return None
    
    def delete_content(self, email):
        self.check_database()
        self.tracking_table.delete_item(
            Key = {
                "email": email
            }
        )

    def scan_everything(self):
        self.check_database()
        response = self.tracking_table.scan()
        if 'Items' in response:
            return response["Items"]
        print("Unable to query content")
        return None

    def query_user(self, email):
        self.check_database()
        response = self.tracking_table.query(
            KeyConditionExpression=Key('email').eq(email)
        )
        if 'Items' in response:
            if len(response["Items"]) > 0:
                return response["Items"][0]
        print("Unable to query user")
        return None
    
    def update_content(self, content_id, email, content):
        self.check_database()
        result = self.tracking_table.update_item(
            Key = {
                'email' : email
            },
            UpdateExpression = 'SET content = :val',
            ExpressionAttributeValues = {
                ':val' : content
            },
            ReturnValues = 'UPDATED_NEW'
        ) 
        if 'Attributes' in result:
            return result['Attributes']
        else:
            return dict()