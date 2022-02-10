import boto3
from User import user_template

users = {}


def help_actions():
    print("Here are some of the actions that you can do: ")
    print("Add contact: add contact")
    print("Send message: send message")
    print("Read message: read message")
    print("Read messages: read messages")
    print("Retrieve messages: retrieve messages")


def prompt_user(user):
    prompt = input(f"What would you like to do, {user}? ")
    return prompt.lower()


def acknowledgeRead2():
    prompt_user2 = input("Please confirm you've read the message ~ ")
    if prompt_user2 == "yes":
        return True
    return False


def chat(id, user_name, has_account):
    if has_account:
        dynamodb = boto3.resource('dynamodb')
        management_table = dynamodb.Table('UserManagement')
        res = management_table.get_item(Key={'name': user_name, 'id': id})

        chatting = prompt_user(user_name)

        while chatting != "quit":
            if chatting == "help":
                help_actions()
            elif chatting == "add contact":   # get_item
                contact_name, contact_id = input("Please enter the name and id of your new contact: ").split(" ")
                contact_id = int(contact_id)
                contact = management_table.get_item(Key={'name': contact_name, 'id': contact_id})
                res['Item']['info']['contacts'][contact_id] = [contact_name, contact]
            elif chatting == "send message":  # get_item
                receiver_name, receiver_id = input("Please enter the receiver name and id: ").split(" ")
                mssg = input("Please enter your message: ")  # brianq 2198
                receiver_id = int(receiver_id)
                if receiver_id not in res['Item']['info']['contacts']:
                    print(f"{receiver_name} is not one of your contacts")
                else:
                    receiver = management_table.get_item(Key={'name': receiver_name, 'id': receiver_id})
                    receiver['Item']['info']['inbox'].append(mssg)
            elif chatting == "read message":
                if len(res['Item']['info']['inbox']) == 0:
                    print("You have no new messages")
                else:
                    message = res['Item']['info']['inbox'][-1]
                    print(message)
                    acknowledged = False
                    while acknowledged is False:
                        acknowledged = acknowledgeRead2()

                    res['Item']['info']['inbox'].pop()
                    res['Item']['info']['read_messages'].append(message)
            elif chatting == "read messages":
                if len(res['Item']['info']['inbox']) == 0:
                    print("You have no new messages")
                else:
                    amount_of_messages = min(int(input("How many messages would you like to read? ")), len(res['Item']['info']['inbox']))
                    messages_read = 0
                    for message in res['Item']['info']['inbox'][::-1]:
                        if messages_read == amount_of_messages:
                            break
                        else:
                            print(message)
                            messages_read += 1

                    acknowledged = False
                    while acknowledged is not True:
                        acknowledged = acknowledgeRead2()

                    messages_to_delete = amount_of_messages
                    while messages_to_delete > 0:
                        res['Item']['info']['inbox'].pop()
                        messages_to_delete -= 1

            elif chatting == "retrieve message":
                if len(res['Item']['info']['read_messages']) == 0:
                    print("You currently cannot retrieve any messages")
                else:
                    retrieval_messages = min(int(input("How many messages would you like to retrieve? ")), len(res['Item']['info']['read_messages']))
                    while retrieval_messages > 0:
                        res['Item']['info']['inbox'].append(res['Item']['info']['read_messages'][-1])
                        res['Item']['info']['read_messages'].pop()
                        retrieval_messages -= 1

            chatting = prompt_user(user_name)
        else:
            print(f"Hope to see yous soon, {user_name}")



    else:
        current_user = users[id][1]
        chatting = prompt_user(user_name)

        while chatting != "quit":
            if chatting == "help":
                help_actions()
            elif chatting == "add contact":
                contact, contact_id = input("Please enter in the name and id of your new contact: ").split(" ")
                contact_id = int(contact_id)
                current_user.addContact(contact, contact_id)
            elif chatting == "send message":
                name, receiver_id = input("Please enter the receiver name and id: ").split(" ")
                message = input("Please enter your message: ")  # alex 9715
                receiver_id = int(receiver_id)
                current_user.sendMessage(name, receiver_id, message)
            elif chatting == "read message":
                current_user.inbox.readMessage()
            elif chatting == "read messages":
                number_messages = int(input("How many messages would you like to read? "))
                current_user.inbox.readMessages(number_messages)
            elif chatting == "retrieve message":
                retrieval_messages = int(input("How many messages would you like to retrieve? "))
                current_user.inbox.retrieve_message(retrieval_messages)

            chatting = prompt_user(user_name)
        else:
            print(f"Hope to see yous soon, {user_name}")


if __name__ == '__main__':
    sign_in = input("Welcome! Do you currently have an account? ")
    if sign_in.lower() == "yes":
        username, user_id = input("Please enter your name and id, separated by a space: ").split(" ")
        user_id = int(user_id)
        users[user_id] = [username, user_id]  # change user_id to user object using table get item
        chat(user_id, username, True)
    else:
        name = input("Welcome! Please enter your name: ")
        new_user = user_template.User(name)
        new_user.addUserToTable()
        user_id = new_user.id
        user_id = int(user_id)
        print(f"Welcome {new_user.name}! Your id is {str(user_id)}.")
        users[user_id] = [new_user.name, new_user]  # id: [name, user object]
        chat(user_id, name, False)

# flask run -h localhost -p 3000
