import boto3, os, json, tempfile
from datetime import datetime
from boto3.s3.transfer import S3Transfer
from decouple import config

class MetricsBucket:

    def __init__(self, s3 = None):
        self.s3 = s3
        self.bucket = None
        self.bucket_name = 'fitness-u-metrics'

    def check_bucket(self):
        if not self.s3:
            self.s3 = boto3.resource(
                's3', 
                aws_access_key_id = config('AWS_ACCESS_KEY_ID'), 
                aws_secret_access_key = config('AWS_SECRET_ACCESS_KEY'),
                region_name = config('AWS_REGION')
                )
            self.bucket = self.s3.Bucket(self.bucket_name)

    def get_json(self):
        self.check_bucket()
        tf = tempfile.NamedTemporaryFile()
        self.bucket.download_file('metrics.json', tf.name)
        json_file = open(tf.name)
        metrics = json.load(json_file)
        json_file.close()
        tf.close()
        return metrics

    def save_json(self, metrics):
        with tempfile.TemporaryDirectory() as td:
            f_name = os.path.join(td, 'metrics')
            with open(f_name, 'w') as fh:
                json.dump(metrics, fh)
            self.bucket.upload_file(f_name, 'metrics.json')

    def add_daily_view(self):
        metrics = self.get_json()
        if 'total_views' in metrics:
            metrics['total_views'] += 1
        else:
            metrics['total_views'] = 1
        now = datetime.now()
        today = now.strftime("%m/%d/%Y")
        if 'daily_views' in metrics:
            daily_views = metrics['daily_views']
            if today in daily_views:
                daily_views[today] += 1
            else:
                daily_views[today] = 1
        else:
            metrics['daily_views'] = dict()
            metrics['daily_views'][today] = 1
        self.save_json(metrics)

    def get_total_view_count(self):
        metrics = self.get_json()
        if 'total_views' in metrics:
            return metrics['total_views']
        else:
            return[0]

    def get_todays_views(self):
        metrics = self.get_json()
        now = datetime.now()
        today = now.strftime("%m/%d/%Y")
        if 'daily_views' in metrics:
            if today in metrics['daily_views']:
                return metrics['daily_views'][today]
        return 0


    def check_most_viewed_content(self, content_id, view_count):
        metrics = self.get_json()
        if 'most_viewed_content' in metrics:
            most_views = metrics['most_viewed_content']['views']
            if view_count > most_views:
                metrics['most_viewed_content']['views'] = view_count
                metrics['most_viewed_content']['content_id'] = content_id
        else:
            metrics['most_viewed_content'] = dict()
            metrics['most_viewed_content']['content_id'] = content_id
            metrics['most_viewed_content']['views'] = view_count
        self.save_json(metrics)
        

    def check_most_viewed_user(self, email, view_count):
        metrics = self.get_json()
        if 'most_viewed_user' in metrics:
            most_views = metrics['most_viewed_user']['views']
            if view_count > most_views:
                metrics['most_viewed_user']['views'] = view_count
                metrics['most_viewed_user']['email'] = email
        else:
            metrics['most_viewed_user'] = dict()
            metrics['most_viewed_user']['email'] = email
            metrics['most_viewed_user']['views'] = view_count
        self.save_json(metrics)

    
def get_most_viewed_content(self):
        metrics = self.get_json()
        if 'most_viewed_content' in metrics:
            return metrics['most_viewed_content']['content_id']
        return ""
        

def get_most_viewed_user(self):
    metrics = self.get_json()
    if 'most_viewed_user' in metrics:
        return metrics['most_viewed_user']['email']
    return ""
        