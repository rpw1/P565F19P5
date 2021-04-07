import boto3
from boto3.dynamodb.conditions import Key, Attr
from decouple import config


class MessagesDatabase:

    def __init__(self, dynamodb = None):
        self.dynamodb = dynamodb
        self.messages_table = None

    def check_database(self):
        if not self.dynamodb:
            self.dynamodb = boto3.resource(
                'dynamodb', 
                aws_access_key_id = config('AWS_ACCESS_KEY_ID'), 
                aws_secret_access_key = config('AWS_SECRET_ACCESS_KEY'),
                region_name = config('AWS_REGION')
                )
        self.messages_table = self.dynamodb.Table('conversations')

    def insert_conversation(self, conversation_id, sender_id, recipient_id, message):
        """
        sender_id -> required, string \n
        recipient_id -> required, string \n
        conversation_id -> required, string \n
        conversation -> required, list
        """
        self.check_database()
        response = self.messages_table.put_item(
            Item = {
                'sender_id': sender_id,
                'recipient_id': recipient_id,
                'conversation_id': conversation_id,
                'conversation': [[0, message]]
                #'conversation': content
                #make a new list containing an item that has the first message, as well as who sent it
                #possibly 0 for person who initiated, and 1 for recipient, and it can be stored in a list
                #messages can be "added" to the conversation by anyone, but only clients can create new conversations
            }
        )

    def get_conversation_by_id(self, conversation_id):
        self.check_database()
        response = self.messages_table.scan(
            FilterExpression = Attr('conversation_id').eq(conversation_id)
        )
        if 'Items' in response:
            return response["Items"]
        print("Unable to query content")
        return None

    def get_client_conversations(self, email):
        self.check_database()
        response = self.messages_table.scan(
            FilterExpression = Key('sender_id').eq(email)
        )
        if 'Items' in response:
            return response["Items"]
        print("Unable to query content")
        return None

    def get_professional_conversations(self, email):
        self.check_database()
        response = self.messages_table.scan(
            FilterExpression = Attr('recipient_id').eq(email)
        )
        if 'Items' in response:
            return response["Items"]
        print("Unable to query content")
        return None

    def get_admin_conversations(self):
        self.check_database()
        response = self.messages_table.scan(
            FilterExpression = Attr('recipient_id').eq('admin')
        )
        if 'Items' in response:
            return response["Items"]
        print("Unable to query content")
        return None
    
