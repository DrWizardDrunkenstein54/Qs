

from flask import Flask, render_template, url_for, request, redirect
import boto3
from botocore.exceptions import ClientError
import random

"""
QUEUES BEGIN
"""


class InboxQueue:

    def __init__(self):  # user
        self.unread_messages = ["hello world", "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."]  # Unread
        self.read_messages = []  # Read
        self.message_capacity = 10000

    def refreshMessageQueue(self):
        # Send queue to database, reset unread/read messages
        self.unread_messages = []
        self.read_messages = []

    def acknowledgeRead(self):  # user
        prompt_user = input("~")
        if prompt_user is not None:
            return True

    def enqueMessage(self, message):
        if (len(self.unread_messages) + len(self.read_messages) + 1) <= self.message_capacity:
            self.unread_messages.append(message)
        else:
            self.refreshMessageQueue()

    def readMessage(self):  # user
        if len(self.unread_messages) == 0:
            print("You have no new messages")
        else:
            print(self.unread_messages[-1])

            acknowledged = False
            while acknowledged is not True:
                acknowledged = self.acknowledgeRead()

            self.read_messages.append(self.unread_messages[-1])
            self.unread_messages.pop(-1)

    def readMessages(self, total_messages):  # user
        if len(self.unread_messages) == 0:
            print("You have no new messages")
        else:
            if total_messages > len(self.unread_messages):
                for message in self.unread_messages[::-1]:
                    print(message)

                acknowledged = False
                while acknowledged is not True:
                    acknowledged = self.acknowledgeRead()

                while len(self.unread_messages) > 0:
                    self.read_messages.append(self.unread_messages[-1])
                    self.unread_messages.pop(-1)

            else:
                messagesRead = 0
                for message in self.unread_messages[::-1]:
                    if messagesRead > total_messages:
                        break
                    else:
                        print(message)
                        messagesRead += 1

                acknowledged = False
                while acknowledged is not True:
                    acknowledged = self.acknowledgeRead()

                while total_messages > 0:
                    self.read_messages.append(self.unread_messages[-1])
                    self.unread_messages.pop(-1)
                    total_messages -= 1


    def retrieve_message(self, total_messages):
        if len(self.read_messages) == 0:
            print("There are currently no retrievable messages")
        else:
            retrievedMessages = []
            while total_messages > 0:
                currentMessage = self.read_messages.pop(-1)
                retrievedMessages.append(currentMessage)
                total_messages -= 1

            for message in retrievedMessages:
                self.unread_messages.append(message)


"""
QUEUES END
"""

"""
USER TEMPLATE BEGIN
"""
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
        self.inbox = InboxQueue()
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

"""
USER TEMPLATE END
"""

"""
DEMO BEGIN
"""



name = "User"
new_user = User(name)
new_user.addUserToTable()
user_id = new_user.id
user_id = int(user_id)



"""
DEMO END
"""


application = Flask(__name__)


@application.route("/", methods=["GET", "POST"])
def home():
    return render_template("index.html")


@application.route("/read_message", methods=["GET", "POST"])
def read_message():
    message = "You have no new messages"
    if len(new_user.inbox.unread_messages) > 0:
        message = new_user.inbox.unread_messages[-1]
        new_user.inbox.read_messages.append(new_user.inbox.unread_messages[-1])
        new_user.inbox.unread_messages.pop()
    if request.method == "POST":
        mssg = new_user.inbox.read_messages[-1]
        new_user.inbox.unread_messages.append(mssg)
        new_user.inbox.unread_messages.pop()
        return redirect(url_for("/"))
    return render_template("read_message.html", message=message)


@application.route("/send_message", methods=["GET", "POST"])
def send_message():
    if request.method == "POST":
        req = request.form
        receiver = req['receiver']
        receiver_id = req['receiver_id']
        message = req['message']
        if receiver in new_user.contacts:
            new_user.sendMessage(receiver, receiver_id, message)
        return redirect(request.url)
    return render_template("send_message.html")


@application.route("/add_contact", methods=["GET", "POST"])
def add_contact():
    if request.method == "POST":
        req = request.form
        username = req["username"]
        id = int(req["id"])
        new_user.addContact(username, id)
        return redirect(request.url)


    return render_template("add_contact.html")



if __name__ == "__main__":
    application.run(debug=True)


