import boto3
from boto3.dynamodb.conditions import Key
from decouple import config


class FitnessProfessionalDatabase:

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
        self.user_table = self.dynamodb.Table('fitness_professionals')

    def insert_user(self, email, first_name, last_name, appointments, metrics, content_id_list, gender, location, specialty):
        """
            appointments -> list of dictionaries
            metrics -> dictionary
            content_id_list -> list of content_ids
        """
        self.check_database()
        response = self.user_table.put_item(
            Item = {
                'email' : email,
                'first_name' : first_name,
                'last_name' : last_name,
                'appointments': appointments,
                'metrics': metrics,
                'content_ids': content_id_list,
                'gender': gender,
                'location': location,
                'specialty': specialty
            }
        )

    def get_fitness_professional(self, email):
        self.check_database()
        result = self.user_table.get_item(
            Key = {
                'email': email
            }
        )
        if 'Item' in result:
            return result['Item']
        else:
            return None

    def update_content(self, email, content_id):
        self.check_database()
        result = self.user_table.get_item(
            Key = {
                'email' : email
            }
        ) 
        if 'Item' in result:
            content_list = result['Item']['content_ids']
            content_list.append(content_id)
            self.user_table.update_item(
                Key = {
                    'email' : email
                },
                UpdateExpression = 'SET content_ids = :val',
                ExpressionAttributeValues = {
                ':val' : content_list
            }
        ) 

    def update_appointments(self, email, appointment):
        self.check_database()
        result = self.user_table.get_item(
            Key = {
                'email' : email
            }
        ) 
        if 'Item' in result:
            appointments = result['Item']['appointments']
            appointments.append(appointment)
            self.user_table.update_item(
                Key = {
                    'email' : email
                },
                UpdateExpression = 'SET appointments = :val',
                ExpressionAttributeValues = {
                ':val' : appointments
            }
        ) 


    def update_metrics(self, email, metrics):
        self.check_database()
        self.user_table.update_item(
            Key = {
                'email' : email
            },
            UpdateExpression = 'SET metrics = :val',
            ExpressionAttributeValues = {
                ':val' : metrics
            }
        ) 

    def delete_fitness_professional(self, email):
        self.check_database()
        self.user_table.delete_item(
            Key = {
                'email' : email
            }
        )

