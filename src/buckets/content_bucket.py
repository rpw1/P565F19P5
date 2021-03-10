import boto3
from decouple import config

class ContentBucket:

    def __init__(self, s3 = None):
        self.s3 = s3
        self.bucket = None
        self.bucket_name = 'fitness-u-users-content'

    def check_bucket(self):
        if not self.s3:
            self.s3 = boto3.resource(
                's3', 
                aws_access_key_id = config('AWS_ACCESS_KEY_ID'), 
                aws_secret_access_key = config('AWS_SECRET_ACCESS_KEY'),
                region_name = config('AWS_REGION')
                )
            self.bucket = self.s3.Bucket(self.bucket_name)

    def add_file(self, email, file_name_with_extension):
        self.check_bucket()
        object_name = email + "/" + file_name_with_extension
        self.bucket.upload_file(object_name, file_name_with_extension)
        print("successfully added file")
        return {
            "bucket_name": self.bucket_name,
            "object_name": object_name,
        }

    def get_file_link(self, s3_dict):
        self.check_bucket()
        if 'bucket_name' in s3_dict and 'object_name' in s3_dict:
            return "http://" + s3_dict['bucket_name'] + ".s3-website." + config('AWS_REGION') + ".amazonaws.com" + s3_dict['object_name']
        print("Error: s3 dict was not set up correctly")
        return None

    

        