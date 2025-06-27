import boto3
from config import REGION
from seed_prompts import seed_prompts_data


dynamodb = boto3.resource('dynamodb', region_name=REGION)

def create_users_table():
    try:
        users_table = dynamodb.create_table(
            TableName="Users",
            KeySchema=[
                {
                    "AttributeName": "user_id",
                    'KeyType': 'HASH'
                }
            ],
            AttributeDefinitions=[
                {
                    "AttributeName": "user_id",
                    "AttributeType": "S"
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
    except dynamodb.meta.client.exceptions.ResourceInUseException:
        users_table = dynamodb.Table("Users")


def create_prompts_table():
    try:
        prompts_table = dynamodb.create_table(
            TableName="Prompts",
            KeySchema=[
                {
                    "AttributeName": "prompt_id",
                    "KeyType": "HASH"
                }
            ],
            AttributeDefinitions=[
                {
                    "AttributeName": "prompt_id",
                    "AttributeType": "S"
                },
                {
                    "AttributeName": "user_id",
                    "AttributeType": "S"
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            },
            GlobalSecondaryIndexes=[
                {
                    "IndexName": "UserIndex",
                    "KeySchema":[
                        {
                            "AttributeName": "user_id",
                            "KeyType": "HASH"
                        }
                    ],
                    "Projection" : {
                        "ProjectionType": "ALL"
                    },
                    "ProvisionedThroughput": {
                        "ReadCapacityUnits": 5,
                        "WriteCapacityUnits": 5
                    },
                }
            ]
        )
    except dynamodb.meta.client.exceptions.ResourceInUseException:
        prompts_table = dynamodb.Table("Prompts")


def create_sessions_table():
    try:
        sessions_table = dynamodb.create_table(
            TableName="Sessions",
            KeySchema=[
                {
                    "AttributeName": "user_id",
                    "KeyType": "HASH"
                },
                { 
                    "AttributeName": "session_id", 
                    "KeyType": "RANGE" 
                }
            ],
            AttributeDefinitions=[
                {
                    "AttributeName": "user_id",
                    "AttributeType": "S"
                },
                {
                    "AttributeName": "session_id",
                    "AttributeType": "S"
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            },
            GlobalSecondaryIndexes=[
                {
                    "IndexName": "SessionIndex",
                    "KeySchema":[
                        {
                            "AttributeName": "session_id",
                            "KeyType": "HASH"
                        }
                    ],
                    "Projection" : {
                        "ProjectionType": "ALL"
                    },
                    "ProvisionedThroughput": {
                        "ReadCapacityUnits": 5,
                        "WriteCapacityUnits": 5
                    },
                }
            ]
        )
    except dynamodb.meta.client.exceptions.ResourceInUseException:
        sessions_table = dynamodb.Table("Sessions")


if __name__ == "__main__":
    # Call table creation 
    create_users_table()
    create_prompts_table()
    create_sessions_table()


    # Get table handles for waiters and status
    users_table = dynamodb.Table("Users")
    prompts_table = dynamodb.Table("Prompts")
    sessions_table = dynamodb.Table("Sessions")


    users_table.meta.client.get_waiter('table_exists').wait(TableName='Users')
    prompts_table.meta.client.get_waiter('table_exists').wait(TableName='Prompts')
    sessions_table.meta.client.get_waiter('table_exists').wait(TableName='Sessions')


    print("✅ Table status (Users):", users_table.table_status)
    print("✅ Table status (Prompts):", prompts_table.table_status)
    print("✅ Table status (Sessions):", sessions_table.table_status)


    seed_prompts_data()
