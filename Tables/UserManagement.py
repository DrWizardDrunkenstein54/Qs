import boto3

dynamodb = boto3.resource('dynamodb')

user_management_table = dynamodb.create_table(
    TableName='UserManagement',
    KeySchema=[
        {
            'AttributeName': 'name',
            'KeyType': 'HASH'
        },
        {
            'AttributeName': 'id',
            'KeyType': 'RANGE'
        }
    ],
    AttributeDefinitions=[
        {
            'AttributeName': 'name',
            'AttributeType': 'S'
        },
        {
            'AttributeName': 'id',
            'AttributeType': 'N'
        },
    ],
    ProvisionedThroughput={
        'ReadCapacityUnits': 10,
        'WriteCapacityUnits': 10
    }
)

user_management_table.meta.client.get_waiter('table_exists').wait(TableName='UserManagement')