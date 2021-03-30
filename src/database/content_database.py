import boto3
from boto3.dynamodb.conditions import Key, Attr
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
                approved: "false"
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
                'content': content,
                'approved': False
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

    def update_content(self, content_id, email, content):
        self.check_database()
        result = self.content_table.update_item(
            Key = {
                'content_id': content_id,
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

    def scan_content_by_email(self, email):
        self.check_database()
        response = self.content_table.scan(
            FilterExpression=Key('email').eq(email) & Attr('approved').eq(True),
        )
        if 'Items' in response:
            return response["Items"]
        print("Unable to scan content")
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

    def query_content_unapproved(self):
        self.check_database()
        response = self.content_table.scan(
            FilterExpression = Attr('approved').eq(False)
        )
        if 'Items' in response:
            return response["Items"]
        print("Unable to query content")
        return None

    def query_content_approved(self):
        self.check_database()
        response = self.content_table.scan(
            FilterExpression = Attr('approved').eq(True)
        )
        if 'Items' in response:
            return response["Items"]
        print("Unable to query content")
        return None

    def query_content_by_user(self, email):
        self.check_database()
        response = self.content_table.scan(
            FilterExpression = Key('email').eq(email) & Attr('approved').eq(True)
        )
        if 'Items' in response:
            return response["Items"]
        print("Unable to query content")
        return None

    def query_unapproved_content_by_user(self, email):
        self.check_database()
        response = self.content_table.scan(
            FilterExpression = Key('email').eq(email) & Attr('approved').eq(False)
        )
        if 'Items' in response:
            return response["Items"]
        print("Unable to query content")
        return None

    def get_content_count(self):
        self.check_database()
        return self.content_table.item_count

    def get_uploaded_today_count(self, date):
        self.check_database()
        response = self.content_table.scan(
            FilterExpression = Attr('date').eq(date)
        )
        if 'Items' in response:
            return response["Items"]
        print("Unable to query content")
        return None

    def update_approval(self, content_id, email, approved):
        self.check_database()
        result = self.content_table.update_item(
            Key = {
                'content_id': content_id,
                'email' : email,
            },
            UpdateExpression = 'SET approved = :val',
            ExpressionAttributeValues = {
                ':val' : approved
            },
            ReturnValues = 'UPDATED_NEW'
        ) 
        if 'Attributes' in result:
            return result['Attributes']
        else:
            return dict()

    def scan_content_by_instruction(self, is_diet_plan):
        self.check_database()
        response = dict()
        if is_diet_plan:
            response = self.content_table.scan(
                FilterExpression = Attr('mode_of_instruction').eq('diet_plan') & Attr('approved').eq(True)
            )
        else:
            response = self.content_table.scan(
                FilterExpression = Attr('mode_of_instruction').ne('diet_plan') & Attr('approved').eq(True)
            )
        if 'Items' in response:
            return response["Items"]
        print("Unable to query content")
        return None

    def scan_everything(self):
        self.check_database()
        response = self.content_table.scan()
        if 'Items' in response:
            return response["Items"]
        print("Unable to query content")
        return None