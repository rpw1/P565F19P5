import boto3


class Login_Database:

    def __init__(self, dynamodb = None):
        self.dynamodb = dynamodb
        self.user_table = None

    def check_database(self):
        if not self.dynamodb:
            self.dynamodb = boto3.resource(
                'dynamodb', 
                aws_access_key_id = "", 
                aws_secret_access_key = "",
                region_name = 'us-east-2'
                )
        self.user_table = self.dynamodb.Table('users')

    def insert_user(self, email, user_id, password, first_name, last_name, role, image):
        self.check_database()
        response = self.user_table.put_item(
            Item = {
                'email' : email,
                'user_id' : user_id,
                'password' : password,
                'first_name' : first_name,
                'last_name' : last_name,
                'role' : role,
                'image' : image
            }
        )
        print(response)

    def get_user(self, email):
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

    def update_password(self, email, password):
        self.check_database()
        self.user_table.update_item(
            Key = {
                'email' : email
            },
            UpdateExpression = 'SET password = :val',
            ExpressionAttributeValues = {
                ':val' : password
            }
        ) 

    def delete_user(self, email):
        self.check_database()
        self.user_table.delete_item(
            Key = {
                'email' : email
            }
        )

if __name__ == '__main__':
    database = Login_Database()
    database.insert_user("rpw@iu.edu", "123", "123", "Ryan", "Williams", 1, "image_string")
    print(database.get_user("rpw@iu.edu"))
    database.delete_user("rpw@iu.edu")
