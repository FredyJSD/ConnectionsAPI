import boto3
import os
from config import REGION

# CREATE DB
dynamodb = boto3.resource('dynamodb', region_name=REGION)

users_table = dynamodb.Table('Users')
prompts_table = dynamodb.Table('Prompts')
sessions_table = dynamodb.Table('Sessions')
