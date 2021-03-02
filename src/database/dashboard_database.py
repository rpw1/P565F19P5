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
        self.user_table = self.dynamodb.Table('content')

    def insert_content(self, content_id, email, title, mode_of_instruction, workout_type, age_of_content, description, thumbnail, date):
        self.check_database()
        response = self.user_table.put_item(
            Item = {
                'content_id': content_id,
                'email': email,
                'title': title,
                'instruction': mode_of_instruction,
                'type': workout_type,
                'age_range': age_of_content,
                'description': description,
                'thumbnail': thumbnail,
                'date': date
            }
        )

    def get_content(self, content_id, email):
        self.check_database()
        result = self.user_table.get_item(
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
        self.user_table.delete_item(
            Key = {
                'content_id': content_id,
                "email": email
            }
        )

