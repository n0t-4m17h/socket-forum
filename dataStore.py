# File that holds Sever.py's data structure class for storing all info, an example is down below
# Python Version: 3.8.10
# 10/04/22

initial_object = {
    'users': [],
    'threads': []
}
class Datastore:
    def __init__(self):
        # Initialise data store to empty, as whats above
        self.__store = initial_object

    def get(self):
        # retrieve curr data from data store
        return self.__store

    def set(self, store):
        # Overwites datastore with new data
        self.__store = store

global data_store
data_store = Datastore()


#####
## An example of the Data Structure used in Server.py
#####
'''
data_store = {
    'users': [
        {
            'username': "user2",
            'password': "",
            'isActive': True
        },
        {
            'username': "user2",
            'password': "",
            'isActive': False
        }
    ],
    'threads': [
        {
            'threadtitle': "comp3331",
            'threadID': 1,  # not needed??
            'threadOwner': "user1",
            'threadMembers': ["user1", "user2"], # not needed??
            'threadMsgs': [
                {
                    'msgID': 1,
                    'msgUser': "user1",
                    'msg': "", 
                },
                {
                    'msgID': 2,
                    'msgUser': "user2",
                    'msg': "", 
                }
            ],
            'threadFiles': [
                {
                    'filetitle': "comp3331-shrek.exe",
                    'fileID': 1,
                    'fileUser': "user1"
                }
            ]
        },
        {
            'threadtitle': "",
            'threadID': 2,
            'threadOwner': "user1",
            'threadMembers': ["user1"],
            'threadMsgs': [
                {
                    'msgID': 1,
                    'msgUsername': "user1",
                    'msg': "", 
                }
            ],
            'threadFiles': [
                {
                    'fileTitle': "",
                    'fileID': 1,
                    'fileUser': "user1"
                },
                {
                    'fileTitle': "",
                    'fileID': 2,
                    'fileUser': "user1"
                }
            ]
        }
    ]
}
'''