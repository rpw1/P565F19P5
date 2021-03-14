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
        self.user_table = self.dynamodb.Table('users_prod')

    def insert_client(self, email, password, username, first_name, last_name, gender = "", bio = "",
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
            content -> 
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
                video_content: {
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
                'username': username,
                'first_name': first_name,
                'last_name': last_name,
                'gender': gender,
                'bio': bio,
                'image': image,
                'content': client_content
            }
        )

    def get_client(self, email):
        return self._get_user(email, self.roles[0])

    def delete_client(self, email):
        self._delete_user(email, self.roles[0])

    def update_client_content(self, email, client_content):
        return self._update_content(email, client_content, self.roles[0])

    def update_client_password(self, email, password):
        return self._update_password(email, password, self.roles[0])

    def update_client_image(self, email, image):
        return self._update_image(email, image, self.roles[0])

    def update_client_bio(self, email, bio):
        return self._update_bio(email, bio, self.roles[0])

    def update_client_gender(self, email, gender):
        return self._update_gender(email, gender, self.roles[0])

    def insert_fitness_professional(self, email, password, username, first_name, last_name, gender = "", location = "", bio = "",
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
            bucket -> path to s3 bucket
            fitness_professional_content ->
            {
                user_content: [content_ids]
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
                'username': username,
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
        return self._get_user(email, self.roles[1])

    def delete_fitness_professional(self, email):
        self._delete_user(email, self.roles[1])

    def update_fitness_professional_content(self, email, fitness_professional_content):
        return self._update_content(email, fitness_professional_content, self.roles[1])

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

    def update_fitness_professional_password(self, email, password):
        return self._update_password(email, password, self.roles[1])

    def update_fitness_professional_image(self, email, image):
        return self._update_image(email, image, self.roles[1])

    def update_fitness_professional_bio(self, email, bio):
        return self._update_bio(email, bio, self.roles[1])

    def update_fitness_professional_gender(self, email, gender):
        return self._update_gender(email, gender, self.roles[1])

    def insert_admin(self, email, password, username, first_name, last_name, gender = "", bio = "",
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
                'role': self.roles[2],
                'password': password,
                'username': username,
                'first_name': first_name,
                'last_name': last_name,
                'gender': gender,
                'bio': bio,
                'image': image,
                'content': admin_content
            }
        )

    def get_admin(self, email):
        return self._get_user(email, self.roles[2])

    def delete_admin(self, email):
        self._delete_user(email, self.roles[2])

    def update_admin_content(self, email, admin_content):
        return self._update_content(email, admin_content, self.roles[2])

    def update_admin_password(self, email, password):
        return self._update_password(email, password, self.roles[2])

    def update_admin_image(self, email, image):
        return self._update_image(email, image, self.roles[2])

    def update_admin_bio(self, email, bio):
        return self._update_bio(email, bio, self.roles[2])

    def update_admin_gender(self, email, gender):
        return self._update_gender(email, gender, self.roles[2])

    
    def _get_user(self, email, role):
        self.check_database()
        result = self.user_table.get_item(
            Key = {
                'email': email,
                'role': role
            }
        )
        if 'Item' in result:
            return result['Item']
        else:
            return None

    def _delete_user(self, email, role):
        self.check_database()
        self.user_table.delete_item(
            Key = {
                'email': email,
                'role': role
            }
        )

    def _update_content(self, email, admin_content, role):
        self.check_database()
        result = self.user_table.update_item(
            Key = {
                'email' : email,
                'role': role
            },
            UpdateExpression = 'SET content = :val',
            ExpressionAttributeValues = {
                ':val' : admin_content
            },
            ReturnValues = 'UPDATED_NEW'
        ) 
        if 'Attributes' in result:
            return result['Attributes']
        else:
            return dict()

    def _update_password(self, email, password, role):
        self.check_database()
        result = self.user_table.update_item(
            Key = {
                'email' : email,
                'role': role
            },
            UpdateExpression = 'SET password = :val',
            ExpressionAttributeValues = {
                ':val' : password
            },
            ReturnValues = 'UPDATED_NEW'
        ) 
        if 'Attributes' in result:
            return result['Attributes']
        else:
            return dict()


    def _update_image(self, email, image, role):
        self.check_database()
        result = self.user_table.update_item(
            Key = {
                'email' : email,
                'role': role
            },
            UpdateExpression = 'SET image = :val',
            ExpressionAttributeValues = {
                ':val' : image
            },
            ReturnValues = 'UPDATED_NEW'
        )
        if 'Attributes' in result:
            return result['Attributes']
        else:
            return dict()


    def _update_bio(self, email, bio, role):
        self.check_database()
        result = self.user_table.update_item(
            Key = {
                'email' : email,
                'role': role
            },
            UpdateExpression = 'SET bio = :val',
            ExpressionAttributeValues = {
                ':val' : bio
            },
            ReturnValues = 'UPDATED_NEW'
        ) 
        if 'Attributes' in result:
            return result['Attributes']
        else:
            return dict()

    def _update_gender(self, email, gender, role):
        self.check_database()
        result = self.user_table.update_item(
            Key = {
                'email' : email,
                'role': role
            },
            UpdateExpression = 'SET gender = :val',
            ExpressionAttributeValues = {
                ':val' : gender
            },
            ReturnValues = 'UPDATED_NEW'
        ) 
        if 'Attributes' in result:
            return result['Attributes']
        else:
            return dict()

    def query_user(self, email):
        self.check_database()
        response = self.user_table.query(
            KeyConditionExpression=Key('email').eq(email)
        )
        if 'Items' in response:
            if len(response["Items"]) > 0:
                return response["Items"][0]
        print("Unable to query user")
        return None
    
    def query_delete_user(self, email):
        response = self.query_user(email)
        if response:
            self._delete_user(email, response['role'])


    def query_update_content(self, email, content):
        response = self.query_user(email)
        if response:
            return self._update_content(email, content, response['role'])
        return response

    def query_update_bio(self, email, bio):
        response = self.query_user(email)
        if response:
            return self._update_bio(email, bio, response['role'])
        return response

    def query_update_password(self, email, password):
        response = self.query_user(email)
        if response:
            return self._update_password(email, password, response['role'])
        return response

    def query_update_image(self, email, image):
        response = self.query_user(email)
        if response:
            return self._update_image(email, image, response['role'])
        return response

    def query_update_gender(self, email, gender):
        response = self.query_user(email)
        if response:
            return self._update_gender(email, gender, response['role'])
        return None

    def search_user_by_email(self, email):
        self.check_database()
        response = self.user_table.query(
            KeyConditionExpression=Key('email').begins_with(email)
        )
        if 'Items' in response:
            return response['Items']
        print("Unable to query content")
        return None

    """
     context.writeDateTime(this.dueDate, "dueDate", element);
      context.writeDateTime(this.startDate, "startDate", element);
      context.writeDateTime(this.actualEnd, "actualEnd", element);
      context.writeDateTime(this.actualStart, "actualStart", element);

      context.writeBool(this.allDayEvent, "allDayEvent", element);

      context.writeString(this.subject, "subject", element);
      context.writeString(this.details, "details", element);
      context.writeString(this.status.toString(), "status", element);
      context.writeString(this.priority.oString(), "priority", element);
      context.writeFloat(this.progress, "progress", element);
      context.writeInt(this.estimatedDuration, "estimatedDuration", element);
      context.writeInt(this.actualDuration, "actualDuration", element);
      context.writeFloat(this.estimatedCost, "estimatedCost", element);
      context.writeFloat(this.actualCost, "actualCost", element);

      context.writeReminder(this.reminder, "reminder", element);



      key: 'dueDate',
    get: function get$$1() {
      return this._dueDate;
    }
    /**
     * Sets the task's due date.
     * @param {DateTime} value The new property value.
     */
    ,
    set: function set$$1(value) {
      this._dueDate = value;
    }

    /**
     * Gets the task's start date.
     */

  }, {
    key: 'startDate',
    get: function get$$1() {
      return this._startDate;
    }
    /**
     * Sets the task's start date.
     * @param {DateTime} value The new property value.
     */
    ,
    set: function set$$1(value) {
      this._startDate = value;
    }

    /**
     * Gets the task's actual completion date.
     */

  }, {
    key: 'actualEnd',
    get: function get$$1() {
      return this._actualEnd;
    }
    /**
     * Sets the task's actual completion date.
     * @param {DateTime} value The new property value.
     */
    ,
    set: function set$$1(value) {
      this._actualEnd = value;
    }

    /**
     * Gets the task's actual start date.
     */

  }, {
    key: 'actualStart',
    get: function get$$1() {
      return this._actualStart;
    }
    /**
     * Sets the task's actual start date.
     * @param {DateTime} value The new property value.
     */
    ,
    set: function set$$1(value) {
      this._actualStart = value;
    }

    /**
     * Gets the subject of the task.
     */

  }, {
    key: 'subject',
    get: function get$$1() {
      return this._subject;
    }
    /**
     * Sets the subject of the task.
     * @param {String} value The new property value.
     */
    ,
    set: function set$$1(value) {
      this._subject = value;
    }

    /**
     * Gets the detailed description of the Task.
     */

  }, {
    key: 'details',
    get: function get$$1() {
      return this._details;
    }
    /**
     * Sets the detailed description of the Task.
     * @param {String} value The new property value.
     */
    ,
    set: function set$$1(value) {
      this._details = value;
    }
    """
    