import boto3
import os

# CREATE DB
dynamodb = boto3.resource('dynamodb', region_name=os.getenv('COGNITO_REGION'))

users_table = dynamodb.Table('Users')
prompts_table = dynamodb.Table('Prompts')
sessions_table = dynamodb.Table('Sessions')
