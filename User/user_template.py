import boto3
from botocore.exceptions import ClientError
from Queues import inbox
import random

taken_id = []


class User:

    def __init__(self, name):
        self.name = name
        self.id = random.randint(1000, 9999)
        while True:
            if taken_id.count(self.id) == 0:
                break
            else:
                self.id = random.randint(1000, 9999)
        self.inbox = inbox.InboxQueue()
        self.contacts = {}  # id: [name, user_object]

    def addUserToTable(self, dynamodb=None):
        if not dynamodb:
            # dynamodb = boto3.resource('dynamodb', endpoint_url="http://localhost:8000")
            dynamodb = boto3.resource('dynamodb')

        management_table = dynamodb.Table('UserManagement')
        res = management_table.put_item(
            Item={
                'name': str(self.name),
                'id': self.id,
                'info': {
                    'contacts': self.contacts,
                    'inbox': self.inbox.unread_messages,
                    'read_messages': self.inbox.read_messages
                }
            }
        )

        return res

    def addContact(self, name, id, dynamodb=None):
        if not dynamodb:
            # dynamodb = boto3.resource('dynamodb', endpoint_url="http://localhost:8000")
            dynamodb = boto3.resource('dynamodb')

        management_table = dynamodb.Table('UserManagement')
        try:
            res = management_table.get_item(Key={'name': name, 'id': id})
        except ClientError as error:
            print(error.response['Error']['Message'])
        else:
            self.contacts[res['Item']['id']] = [res['Item']['name'], res]
            print(f"{name} with id: {id} successfully added to contacts")


    def sendMessage(self, name, receiver_id, message, dynamodb=None):  # receiver_id
        if not dynamodb:
            # dynamodb = boto3.resource('dynamodb', endpoint_url="http://localhost:8000")
            dynamodb = boto3.resource('dynamodb')

        if receiver_id not in self.contacts:  # receiver_id
            print(f"{receiver_id} is not one of your current contacts")
        else:
            new_messages = self.inbox.unread_messages
            new_messages.append(message)
            management_table = dynamodb.Table('UserManagement')
            response = management_table.update_item(
                Key={
                    'name': name,  # self.contacts[receiver_id][0]
                    'id': receiver_id  # receiver_id
                },
                UpdateExpression="set info.inbox = :i",
                ExpressionAttributeValues={
                    ':i': new_messages
                },
                ReturnValues="UPDATED_NEW"
            )
            return response
