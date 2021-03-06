import boto3
from boto3.dynamodb.conditions import Key
from decouple import config


class ContentDatabase:

    def __init__(self, dynamodb = None):
        self.dynamodb = dynamodb
        self.user_table = None

    def check_database(self):
        if not self.dynamodb:
            self.dynamodb = boto3.resource(
                'dynamodb', 
                aws_access_key_id = config('AWS_ACCESS_KEY_ID'), 
                aws_secret_access_key = config('AWS_SECRET_ACCESS_KEY'),
                region_name = config('AWS_REGION')
                )
        self.content_table = self.dynamodb.Table('content')

    def insert_content(self, content_id, email, content = dict()):
        """
            content_id -> required, string \n
            email -> required, string \n
            content -> 
            {
                content_type: "",
                title: "",
                description: "",
                thumbnail: "",
                date: "",
                bucket -> "path to bucket"
                file_path -> "path to content file"
                view_count: ""
            }
        """
        self.check_database()
        response = self.content_table.put_item(
            Item = {
                'content_id': content_id,
                'email': email,
                'content': content
            }
        )

    def get_content(self, content_id, email):
        self.check_database()
        result = self.content_table.get_item(
            Key = {
                'content_id': content_id,
                "email": email
            }
        )
        if 'Item' in result:
            return result['Item']
        else:
            return None

    def delete_content(self, content_id, email):
        self.check_database()
        self.content_table.delete_item(
            Key = {
                'content_id': content_id,
                "email": email
            }
        )

    def update_content(self, contnet_id, email, content):
        self.check_database()
        result = self.content_table.update_item(
            Key = {
                'content_id': contnet_id,
                'email' : email,
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

    def query_content_by_email(self, email):
        self.check_database()
        response = self.content_table.query(
            KeyConditionExpression=Key('email').eq(email)
        )
        if 'Items' in response:
            return response["Items"]
        print("Unable to query content")
        return None

    def query_content_by_id(self, content_id):
        self.check_database()
        response = self.content_table.query(
            KeyConditionExpression=Key('content_id').eq(content_id)
        )
        if 'Items' in response:
            if len(response["Items"]) > 0:
                return response["Items"][0]
        print("Unable to query content")
        return None
