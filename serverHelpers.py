# Python Version: 3.8.10
# File for Server.py 's helper fncs
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
    dataStore['users'] = []
    dataStore['threads'] = []

# Exits program, called for ctrl+C detection
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
        passW = brokenLogin[1].rstrip()
        if (username == user and password == passW):
            f.close()
            return True # combo is valid
    f.close()
    return False # combo invalid (password wrong, cause user already checked)

# Creates a new user data-struct (Upon detection of a new login) + adds user deets to data store
# AND adds user to credentials.txt IF it's new
def createNewUser(username, password, isActive, isNewUser):
    userStruct = {"username": username, "password": password, "isActive": isActive}
    dataStore['users'].append(userStruct)
    changeUserActive(username, True)
    if isNewUser == True: # user is not in credentials.txt yet
        f = open("credentials.txt", "a") # append new user deets to end of file
        strToAppend = "\n" + f"{username}" + f" {password}" # whitespace included before passW
        f.write(strToAppend)
        f.close()

# Make user online or offline
def changeUserActive(username, isActive):
    for users in dataStore['users']:
        if users["username"] == username:
            users["isActive"] == isActive
            return

# Returns the whether User is logged in rn or not, if User isn't found, returns None
# Used to prevent multiple logins of the same user
def isUserActive(username):
    # assumes "username" is valid
    for users in dataStore['users']:
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
    # ELSE, its one or two inputs (e.g "XIT" or "DLT 3331")
    return brokenMsg


#################
### CMDS fncs ###
#################

# Fnc first checks if CRT threadtitle already exists, If so, returns False
# IF not, file is created, returns True
def CRT(threadtitle, username):
    # FIRST check CWD for <threadtitle>
    try:
        f = open(f"{threadtitle}")
        f.close()
        return False # If exception isnt raised, that means a file with that title already exists
    except FileNotFoundError:
        # since File does NOT exist, we can continue
        threadID = len(dataStore['threads']) + 1 # start at '1'
        # Store all thread-related information to data store
        dataStore['threads'].append({
            "threadtitle": threadtitle,
            "threadID": threadID,
            "threadOwner": username,
            "threadMembers": [username],
            "threadMsgs": []
        })
        # Now add file to Server's CWD
        f = open(f"{threadtitle}", "w") # "w" creates file if it doesnt exist
        f.write(f"{username}")
        f.close()
        return True
    
# deez
