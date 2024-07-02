import os
from dotenv import load_dotenv
load_dotenv()

PATH_TO_OBSIDIAN = 'smt'
OUTPUT_PATH_ANKI_GENERATED_CARDS = 'smt'

AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID','')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY','')
REGION_NAME = os.environ.get('REGION_NAME','us-east-1')
RDS_TABLE_NAME = os.environ.get('RDS_TABLE_NAME',None)

boto3_configuration = {
    'aws_access_key_id': AWS_ACCESS_KEY_ID,
    'aws_secret_access_key': AWS_SECRET_ACCESS_KEY,
    'region_name': REGION_NAME,
    #'rds_name': RDS_TABLE_NAME
}
