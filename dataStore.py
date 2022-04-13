# An example of the Data Structure used in Server.py

dataStore = {
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
            'threadtitle': "",
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
            ]
        }
    ]
}