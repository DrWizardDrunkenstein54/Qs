class InboxQueue:

    def __init__(self):  # user
        self.unread_messages = []  # Unread
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