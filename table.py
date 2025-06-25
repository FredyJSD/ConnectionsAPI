import boto3


dynamodb = boto3.resource('dynamodb', region_name='us-east-1')


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

users_table.meta.client.get_waiter('table_exists').wait(TableName='Users')
prompts_table.meta.client.get_waiter('table_exists').wait(TableName='Prompts')
sessions_table.meta.client.get_waiter('table_exists').wait(TableName='Sessions')

print("✅ Table status (Users):", users_table.table_status)
print("✅ Table status (Prompts):", prompts_table.table_status)
print("✅ Table status (Sessions):", sessions_table.table_status)
