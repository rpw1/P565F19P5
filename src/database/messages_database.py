import boto3
from boto3.dynamodb.conditions import Key, Attr
from decouple import config
import time


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
        conversation_id -> required, string \n
        sender_id -> required, string \n
        recipient_id -> required, string \n
        conversation -> required, list \n
        update_time -> required, float \n
        sender_unread -> required, boolean \n
        recipient_unread -> required, boolean
        """
        self.check_database()
        response = self.messages_table.put_item(
            Item = {
                'conversation_id': conversation_id,
                'sender_id': sender_id,
                'recipient_id': recipient_id,
                'conversation': [[0, message]],
                'update_time': int(time.time()),
                'sender_unread': False,
                'recipient_unread': True
                #'conversation': content
                #make a new list containing an item that has the first message, as well as who sent it
                #possibly 0 for person who initiated, and 1 for recipient, and it can be stored in a list
                #messages can be "added" to the conversation by anyone, but only clients can create new conversations
            }
        )

    def get_conversation_by_id(self, conversation_id):
        self.check_database()
        response = self.messages_table.scan(
            FilterExpression = Key('conversation_id').eq(conversation_id)
        )
        if 'Items' in response:
            return response["Items"]
        print("Unable to query content")
        return None

    def delete_conversation(self, id):
        self.check_database()
        self.messages_table.delete_item(
            Key = {
                'conversation_id': id,
            }
        )

    def get_client_conversations(self, email):
        self.check_database()
        response = self.messages_table.scan(
            FilterExpression = Attr('sender_id').eq(email)
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

    def add_message(self, id, sender, message):
        current_conversation = self.get_conversation_by_id(id)
        sender_value = 0
        if sender != (current_conversation[0]['sender_id']):
            sender_value = 1
        sender_status = current_conversation[0]['sender_unread']
        recipient_status = current_conversation[0]['recipient_unread']
        if sender_value == 0:
            recipient_status = True
        else:
            sender_status = True
        conversation = current_conversation[0]['conversation']
        new_message = [sender_value, message]
        conversation.append(new_message)
        current_conversation[0]['conversation'] = conversation
        result = self.messages_table.update_item(
            Key = {
                'conversation_id' : id,
            },
            UpdateExpression = 'SET conversation = :val, update_time = :val2, sender_unread = :val3, recipient_unread = :val4' ,
            ExpressionAttributeValues = {
                ':val' : current_conversation[0]['conversation'],
                ':val2' : int(time.time()),
                ':val3' : sender_status,
                ':val4' : recipient_status
            }
        )

    def read_conversation(self, id, email):
        current_conversation = self.get_conversation_by_id(id)
        sender_status = current_conversation[0]['sender_unread']
        recipient_status = current_conversation[0]['recipient_unread']
        if email == current_conversation[0]['sender_id']:
            sender_status = False
        elif email == current_conversation[0]['recipient_id']:
            recipient_status = False
        result = self.messages_table.update_item(
            Key = {
                'conversation_id' : id,
            },
            UpdateExpression = 'SET sender_unread = :val, recipient_unread = :val2' ,
            ExpressionAttributeValues = {
                ':val' : sender_status,
                ':val2' : recipient_status
            }
        )

    
