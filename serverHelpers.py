# Python Version: 3.8.10
# File for Server.py 's helper fncs
# from server import *
# import server as server
from dataStore import data_store
from server import *
from socket import *
import os
import sys
from datetime import datetime
import time

#################
### MISC Fncs ###
#################

# Wipes the whole data store clean (used when Server is killed)
def dataStoreClear():
    store = data_store.get()
    store['users'] = []
    store['threads'] = []
    data_store.set(store)

# Exits program smoothly, called for ctrl+C detection
def killServer(serverSocket):
    dataStoreClear()
    serverSocket.close()    
    sys.exit("\nKilling server...")

# Checks credentials.txt if the given Username exists
def usernameExists(username):
    f = open("credentials.txt", "r") # open for ONLY reading
    allLinesF = f.readlines()
    numLinesF = len(allLinesF)
    for i in range(0, numLinesF):
        # break up string into user and pass
        brokenLogin = allLinesF[i].split(" ") # "brokenLogin" is a list of strings
        user = brokenLogin[0]
        if (username == user):
            f.close()
            return True # username does indeed exist
    f.close()
    return False

# Checks credentials.txt if the user+pass combo exists
def checkUserPassCombo(username, password):
    f = open("credentials.txt", "r")
    allLinesF = f.readlines()
    numLinesF = len(allLinesF)
    for i in range(0, numLinesF):
        brokenLogin = allLinesF[i].split(" ")
        user = brokenLogin[0].rstrip()
        passW = brokenLogin[1].rstrip() # remove trailing newlines
        if (username == user and password == passW):
            f.close()
            return True # combo is valid
    f.close()
    return False # combo invalid (password wrong, cause user already checked)

# Creates a new user data-struct (Upon detection of a new login) + adds user deets to data store
# AND adds user to credentials.txt IF it's new
def createNewUser(username, password, isActive, isNewUser):
    store = data_store.get()
    userStruct = {"username": username, "password": password, "isActive": isActive}
    store['users'].append(userStruct)
    data_store.set(store)
    # server.changeUserActive(username, True)
    if isNewUser == True: # user is not in credentials.txt yet
        f = open("credentials.txt", "a") # append new user deets to end of file
        strToAppend = "\n" + f"{username}" + f" {password}" # whitespace included before passW
        f.write(strToAppend)
        f.close()

# Make user online or offline
def changeUserActive(username, isActive):
    store = data_store.get()
    for users in store['users']:
        if users["username"] == username:
            users["isActive"] = isActive
            data_store.set(store)
            return

# Returns the whether User is logged in rn or not, if User isn't found, returns None
# Used to prevent multiple logins of the same user
def isUserActive(username):
    store = data_store.get()
    # assumes "username" is valid
    for users in store['users']:
        if users['username'] == username:
            return users['isActive']
    return None

# Breakdown Client's cmd-related msg to be suitable for processing
def breakCmdMsg(clientMsg):
    # break down per whitespace, and join index 2 to end, as one string
    brokenMsg = clientMsg.split(" ")
    lenBrokenMsg = len(brokenMsg)
    if lenBrokenMsg > 3:
        # join the 2nd+ indexes
        newMsg = ''
        for i in range(2, lenBrokenMsg):
            newMsg = newMsg + brokenMsg[i] + ' '
        # combine all needed
        retMsg = [str(brokenMsg[0]), str(brokenMsg[1]), str(newMsg.rstrip())]
        return retMsg
    # ELSE, its one or two or three inputs (e.g "XIT" or "DLT 3331" or "MSG 3331 hi!")
    return brokenMsg


#################
### CMDS fncs ###
#################

# Fnc first checks if CRT threadtitle already exists, If so, returns False
# IF not, file is created, returns True
def CRT(threadtitle, username):
    store = data_store.get()
    # FIRST check CWD for <threadtitle>
    try:
        f = open(f"{threadtitle}")
        f.close()
        return False # If exception isnt raised, that means a file with that title already exists
    except FileNotFoundError:
        # since File does NOT exist, we can continue
        threadID = len(store['threads']) + 1 # start at '1'
        # Store all thread-related information to data store
        store['threads'].append({
            "threadtitle": threadtitle,
            "threadID": threadID,
            "threadOwner": username,
            "threadMembers": [username],
            "threadMsgs": []
        })
        data_store.set(store)
        # Now add file to Server's CWD
        f = open(f"{threadtitle}", "w") # "w" creates file if it doesnt exist
        f.write(f"{username}")
        f.close()
        return True

# deez
def RMV():
    pass

# Fnc assumes file already exists (but still checks for file in Server side)
# Writes user's message to file, and stores it in data store correspondingly.  
def MSG(threadtitle, msg, username):
    store = data_store.get()
    try:
        f = open(f"{threadtitle}", "r") # First grab the no. of lines via readlines() by "r" mode
        allLinesF = f.readlines()
        f.close()
        msgID = len(allLinesF)
        msgToAppend = f"\n{msgID} {username}: {msg}"
        f = open(f"{threadtitle}", "a") # open for appending
        f.write(msgToAppend)
        f.close()
        msgMeta = {
            'msgID': msgID,
            'msgUser': username,
            'msg': msg, 
        }
        for threads in store['threads']:
            if threads['threadtitle'] == threadtitle:
                threads['threadMsgs'].append(msgMeta)
                # also add msg-User to 'members' if not already in thread
                if (username in threads['threadMembers']) is False:
                    threads['threadMembers'].append(username) 
        data_store.set(store)
        return True
    except FileNotFoundError:
        return False

# deez
def RDT():
    pass