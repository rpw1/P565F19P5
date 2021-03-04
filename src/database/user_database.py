import boto3
from boto3.dynamodb.conditions import Key
from decouple import config


class UserDatabase:

    def __init__(self, dynamodb = None):
        self.dynamodb = dynamodb
        self.user_table = None
        self.roles = ['client', 'fitness_professional', 'admin']

    def check_database(self):
        if not self.dynamodb:
            self.dynamodb = boto3.resource(
                'dynamodb', 
                aws_access_key_id = config('AWS_ACCESS_KEY_ID'), 
                aws_secret_access_key = config('AWS_SECRET_ACCESS_KEY'),
                region_name = config('AWS_REGION')
                )
        self.user_table = self.dynamodb.Table('users')

    def insert_client(self, email, password, first_name, last_name, gender, bio = "",
        image = "https://upload.wikimedia.org/wikipedia/en/c/c6/Roisin_Murphy_-_Overpowered.png", 
        client_content = dict()):
        """
            email -> required, string \n
            password -> required, encoded password, string \n
            first_name -> required, string \n
            last_name -> required, string \n
            gender -> required, string \n
            bio -> string \n
            image -> user profile image string \n
            user_content -> 
            {
                timetables: {
                    workout for the day: {
                        workout data
                    },
                    meals: {
                        [
                            {
                                meal data
                            }
                        ]
                    },
                    sleep_cycle: {
                        sleep cycle data
                    }
                },
                plans: {
                    workout_plans: [content_id]
                    diet_plans: [content_ids]
                },
                metrics: {
                    goals: {
                        total_calories burnt: #
                        [
                            {
                                goal data (including goal progress)
                            }
                        ]
                    },
                    daily {
                        day's_date: {
                            calories_burnt: #,
                            eating_habits
                            general_exercise
                            sleep
                        }
                    }
                },
                content: {
                    upcoming_training: [content_ids],
                    recently_watched: [content_ids]
                },
                chats: {
                    user_email {
                        chat_data
                    }
                },
                recommendations: {
                    workout_plans: [content_ids],
                    videos: [content_ids],
                    diet_plans: [content_ids],
                    professionals: [fitness_professional_emails]
                }
            }
        """
        self.check_database()
        response = self.user_table.put_item(
            Item = {
                'email': email,
                'role': self.roles[0],
                'password': password,
                'first_name': first_name,
                'last_name': last_name,
                'gender': gender,
                'bio': bio,
                'image': image,
                'content': client_content
            }
        )

    def get_client(self, email):
        self.check_database()
        result = self.user_table.get_item(
            Key = {
                'email': email,
                'role': self.roles[0]
            }
        )
        if 'Item' in result:
            return result['Item']
        else:
            return None

    def delete_client(self, email):
        self.check_database()
        self.user_table.delete_item(
            Key = {
                'email': email,
                'role': self.roles[0]
            }
        )
    
    def update_client_content(self, email, client_content):
        self.check_database()
        result = self.user_table.update_item(
            Key = {
                'email' : email,
                'role': self.roles[0]
            },
            UpdateExpression = 'SET content = :val',
            ExpressionAttributeValues = {
                ':val' : client_content
            },
            ReturnValues = 'UPDATED_NEW'
        ) 
        if 'Item' in result:
            return result['Item']
        else:
            return dict()

    def insert_fitness_professional(self, email, password, first_name, last_name, gender, location, bio = "",
        image = "https://upload.wikimedia.org/wikipedia/en/c/c6/Roisin_Murphy_-_Overpowered.png",
        specialties = list(), fitness_professional_content = dict()):
        """
            email -> required, string \n
            password -> required, encoded password, string \n
            first_name -> required, string \n
            last_name -> required, string \n
            gender -> required, string \n
            location -> required, string (or json if that is better) \n
            bio -> string \n
            image -> user profile image string \n
            specialties -> [specialty] \n
            fitness_professional_content ->
            {
                workout_plans: [contnet_ids],
                diet_plans: [content_ids],
                videos: [content_ids],
                client_metrics: {
                    data
                },
                appointments {
                    [
                        {
                            data
                        }
                    ]
                },
                chats: {
                    user_email: {
                        chat data
                    }
                }
            }
        """
        self.check_database()
        response = self.user_table.put_item(
            Item = {
                'email': email,
                'role': self.roles[1],
                'password': password,
                'first_name': first_name,
                'last_name': last_name,
                'gender': gender,
                'location': location,
                'bio': bio,
                'image': image,
                'specialties': specialties,
                'content': fitness_professional_content
            }
        )
    
    def get_fitness_professional(self, email):
        self.check_database()
        result = self.user_table.get_item(
            Key = {
                'email': email,
                'role': self.roles[1]
            }
        )
        if 'Item' in result:
            return result['Item']
        else:
            return None

    def delete_fitness_professional(self, email):
        self.check_database()
        self.user_table.delete_item(
            Key = {
                'email': email,
                'role': self.roles[1]
            }
        )


    def update_fitness_professional_content(self, email, fitness_professional_content):
        self.check_database()
        result = self.user_table.update_item(
            Key = {
                'email' : email,
                'role': self.roles[1]
            },
            UpdateExpression = 'SET content = :val',
            ExpressionAttributeValues = {
                ':val' : fitness_professional_content
            },
            ReturnValues = 'UPDATED_NEW'
        ) 
        if 'Item' in result:
            return result['Item']
        else:
            return dict()


    def update_fitness_professional_location(self, email, location):
        self.check_database()
        result = self.user_table.update_item(
            Key = {
                'email' : email,
                'role': self.roles[1]
            },
            UpdateExpression = 'SET location = :val',
            ExpressionAttributeValues = {
                ':val' : location
            },
            ReturnValues = 'UPDATED_NEW'
        ) 
        if 'Item' in result:
            return result['Item']
        else:
            return dict()

    def update_fitness_professional_specialties(self, email, specialties):
        self.check_database()
        result = self.user_table.update_item(
            Key = {
                'email' : email,
                'role': self.roles[1]
            },
            UpdateExpression = 'SET specialties = :val',
            ExpressionAttributeValues = {
                ':val' : specialties
            },
            ReturnValues = 'UPDATED_NEW'
        ) 
        if 'Item' in result:
            return result['Item']
        else:
            return dict()

    def insert_fitness_professional(self, email, password, first_name, last_name, gender, bio,
        image = "https://upload.wikimedia.org/wikipedia/en/c/c6/Roisin_Murphy_-_Overpowered.png",
        admin_content = dict()):
        """
            email -> required, string \n
            password -> required, encoded password, string \n
            first_name -> required, string \n
            last_name -> required, string \n
            gender -> required, string \n
            bio -> string \n
            image -> user profile image string \n
            admin_content ->
            {
                metrics: {
                    metrics data
                }, 
                chats: {
                    user_email {
                        chat data
                    }
                }
            }
        """
        self.check_database()
        response = self.user_table.put_item(
            Item = {
                'email': email,
                'role': self.roles[1],
                'password': password,
                'first_name': first_name,
                'last_name': last_name,
                'gender': gender,
                'bio': bio,
                'image': image,
                'content': admin_content
            }
        )
    
    def get_admin(self, email):
        self.check_database()
        result = self.user_table.get_item(
            Key = {
                'email': email,
                'role': self.roles[2]
            }
        )
        if 'Item' in result:
            return result['Item']
        else:
            return None

    def delete_admin(self, email):
        self.check_database()
        self.user_table.delete_item(
            Key = {
                'email': email,
                'role': self.roles[2]
            }
        )

    def update_admin_content(self, email, admin_content):
        self.check_database()
        result = self.user_table.update_item(
            Key = {
                'email' : email,
                'role': self.roles[1]
            },
            UpdateExpression = 'SET content = :val',
            ExpressionAttributeValues = {
                ':val' : admin_content
            },
            ReturnValues = 'UPDATED_NEW'
        ) 
        if 'Item' in result:
            return result['Item']
        else:
            return dict()

    def update_password(self, email, password):
        self.check_database()
        result = self.user_table.update_item(
            KeyConditionExpression = '#email = :email',
            ExpressionAttributeNames = {
                '#email': email,
            },
            UpdateExpression = 'SET password = :val',
            ExpressionAttributeValues = {
                ':val' : password
            },
            ReturnValues = 'UPDATED_NEW'
        ) 
        if 'Item' in result:
            return result['Item']
        else:
            return dict()


    def update_image(self, email, image):
        self.check_database()
        result = self.user_table.update_item(
            KeyConditionExpression = '#email = :email',
            ExpressionAttributeNames = {
                '#email': email,
            },
            UpdateExpression = 'SET image = :val',
            ExpressionAttributeValues = {
                ':val' : image
            },
            ReturnValues = 'UPDATED_NEW'
        )
        if 'Item' in result:
            return result['Item']
        else:
            return dict()


    def update_bio(self, email, bio):
        self.check_database()
        result = self.user_table.update_item(
            KeyConditionExpression = '#email = :email',
            ExpressionAttributeNames = {
                '#email': email,
            },
            UpdateExpression = 'SET bio = :val',
            ExpressionAttributeValues = {
                ':val' : bio
            },
            ReturnValues = 'UPDATED_NEW'
        ) 
        if 'Item' in result:
            return result['Item']
        else:
            return dict()