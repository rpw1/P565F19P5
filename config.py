import os

class Config(object):
    DEBUG = True
    AWS_DEFAULT_REGION = os.environ.get("AWS_REGION")
    AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
    DUO_A_KEY = os.environ.get("DUO_A_KEY")
    DUO_I_KEY = os.environ.get("DUO_I_KEY")
    DUO_S_KEY = os.environ.get("DUO_S_KEY")
    SMTP_USERNAME = os.environ.get('SMTP_USERNAME')
    SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD')