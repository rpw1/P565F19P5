import boto3
from boto3.dynamodb.conditions import Key
from decouple import config


class MessagesDatabase:

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
        self.content_table = self.dynamodb.Table('conversations')

    def insert_conversation(self, sender_id, recipient_id, message):
        self.check_database()
        response = self.content_table.put_item(
            Item = {
                'sender_id': content_id,
                'recipient_id': email,
                #'conversation': content
                #make a new list containing an item that has the first message, as well as who sent it
                #possibly 0 for person who initiated, and 1 for recipient, and it can be stored in a list
                #messages can be "added" to the conversation by anyone, but only clients can create new conversations
            }
        )