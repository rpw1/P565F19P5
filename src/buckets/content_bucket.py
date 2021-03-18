import boto3, os
from boto3.s3.transfer import S3Transfer
from decouple import config

class ContentBucket:

    def __init__(self, s3 = None):
        self.s3 = s3
        self.client = None
        self.transfer = None
        self.bucket_name = 'fitness-u-users-content'

    def check_bucket(self):
        if not self.s3:
            self.client = boto3.client(
                's3', 
                aws_access_key_id = config('AWS_ACCESS_KEY_ID'), 
                aws_secret_access_key = config('AWS_SECRET_ACCESS_KEY'),
                region_name = config('AWS_REGION')
                )
            self.transfer = S3Transfer(self.client)

    def add_file(self, content_id, email, file_name_with_extension, thumbnail_name):
        self.check_bucket()
        image_type = thumbnail_name.split(".")
        object_name = email + "/" + content_id
        try:
            self.transfer.upload_file(os.path.join(config('UPLOAD_FOLDER'), file_name_with_extension), self.bucket_name, object_name + "/" + file_name_with_extension, extra_args = {
                'ContentType' :"text/html",
            })
            self.transfer.upload_file(os.path.join(config('UPLOAD_FOLDER'), thumbnail_name), self.bucket_name, object_name + "/" + thumbnail_name, extra_args = {
                'ContentType' : "image/" + image_type[len(image_type) - 1],
            })
        except Exception as e:
            print(e)
        self.client.put_object_acl(ACL='public-read', Bucket=self.bucket_name, Key=object_name + "/" + file_name_with_extension)
        self.client.put_object_acl(ACL='public-read', Bucket=self.bucket_name, Key=object_name + "/" + thumbnail_name)
        print("successfully added file")
        return {
            "bucket_name": self.bucket_name,
            "object_name": object_name,
            "file_name": file_name_with_extension,
            "thumbnail_name": thumbnail_name,
            "file_link": "https://" + self.bucket_name + ".s3." + config('AWS_REGION') + ".amazonaws.com/" + object_name + "/" + file_name_with_extension,
            "thumbnail_link": "https://" + self.bucket_name + ".s3." + config('AWS_REGION') + ".amazonaws.com/" + object_name + "/" + thumbnail_name
        }

    def get_file_link(self, s3_dict):
        """
            returns a tuple -> thumbnail_link, file_link
        """
        self.check_bucket()
        if 'thumbnail_link' in s3_dict and 'file_link' in s3_dict:
            return s3_dict['thumbnail_link'], s3_dict['file_link']
        print("Error: s3 dict was not set up correctly")
        return None, None

    def delete_file(self, s3_dict):
        self.check_bucket()
        if 'object_name' in s3_dict:
            response = self.bucket.delete_objects(
                Delete={
                    "Objects" : [
                        {
                            "Key" : s3_dict['object_name']
                        }
                    ]
                }
            )

            if 'Deleted' in response:
                if len(response['Deleted']) > 0:
                    if "Key" in response['Deleted'][0]:
                        if s3_dict['object_name'] == response['Deleted'][0]['Key']:
                            print("File deleted Successfully")
                            return True
        print("Object was not deleted successfully")
        return False

    

        