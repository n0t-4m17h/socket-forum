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

# Creates a new user data-struct (Upon detection of a new login) IFF not already in data store
# adds user deets to data store
# AND adds user to credentials.txt IF it's new
def createNewUser(username, password, isActive, isNewUser):
    store = data_store.get()
    userExistsDataStore = False
    # check if user is in data store
    for user in store['users']:
        if user['username'] == username:
            userExistsDataStore = True
    if userExistsDataStore is False:
        userStruct = {"username": username, "password": password, "isActive": isActive}
        store['users'].append(userStruct)
        data_store.set(store)
    # Overwrite active status incase code above isnt run (case: Old user logging back in)
    changeUserActive(username, True)
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

# Same fnc as above, except catered for "EDT" client responses
# ["EDT", <title>, <username>, <msgID>, <newMsg>]
def EDTbreakResp(clientResp):
    brokenResp = clientResp.split(" ")
    lenBrokenResp = len(brokenResp)
    # join the 4th+ indexes
    newResp = ''
    for i in range(4, lenBrokenResp):
        newResp = newResp + brokenResp[i] + ' '
    # combine all needed
    retResp = [str(brokenResp[0]), str(brokenResp[1]), str(brokenResp[2]), str(brokenResp[3]), str(newResp.rstrip())]
    # remove whitespaces from retInput
    for i in retResp:
        if i == '':
            retResp.remove(i)
    return retResp

# Checks whether user owns the given thread, if so, returns True
def userIsThreadOwner(username, threadtitle):
    store = data_store.get()
    for threads in store['threads']:
        if threads['threadtitle'] == threadtitle:
            if threads['threadOwner'] == username:
                return True
            else:
                return False

# In cases of RMV(), -1 the threadID of all threads AFTER the removed thread.
# This is called BEFORE the thread is actually removed 
def decrementThreadIDs(rmvdThreadTitle):
    store = data_store.get()
    threadFound = False
    for threads in store['threads']:
        if threads['threadtitle'] == rmvdThreadTitle:
            threadFound = True # found the thread, now -1 for all successive threads
        if threadFound is True:
            threads['threadID'] += -1
    data_store.set(store)

# In cases of DLT(). -1 the msgID of all msgs in the given thread AFTER the to-be-removed msgID
# This is called BEFORE msg is actually deleted
# When called, its assumed hat all checks for DLT() have been passed (file found, msgID in range, user is owner)
def decrementMsgIDs(threadtitle, dltMsgID):
    store = data_store.get()
    msgFound = False
    for threads in store['threads']:
        if threads['threadtitle'] == threadtitle:
            for msgs in threads['threadMsgs']:
                if msgs['msgID'] == dltMsgID:
                    msgFound = True # found the msgID, now -1 for all successive msgIDs
                if msgFound is True:
                    msgs['msgID'] += -1
    data_store.set(store)


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
            # "threadFiles": []
        })
        data_store.set(store)
        # Now add file to Server's CWD
        f = open(f"{threadtitle}", "w") # "w" creates file if it doesnt exist
        f.write(f"{username}")
        f.close()
        return True


# Fnc first checks CWD for thread, then checks the give user is owner of thread, then decrements 1 from 
# the IDs of all threads created after the given thread (if any), then removes thread from dataStore, then
# removes file with threadtitle from CWD. 
def RMV(threadtitle, username):
    store = data_store.get()
    # FIRST check CWD for <threadtitle>
    try:
        f = open(f"{threadtitle}")
        f.close()
        # SECOND, check if username is owner of thread
        if userIsThreadOwner(username, threadtitle) is False:
            return "Not Owner"
        # If so, decrement all threadIDs of threads created after thread-to-be-removed
        decrementThreadIDs(threadtitle)
        # FINALLY delete the thread file from CWD and remove from data store
        for thread in store['threads']:
            if thread['threadtitle'] == threadtitle:
                store['threads'].remove(thread)
                data_store.set(store) # update data store accordingly
        os.remove(f"{threadtitle}") # rmv thread from server's cwd
        return "Thread Removed"
    except FileNotFoundError:
        return "File Not Found"


# Fnc reads contents of file and sends it to Client.
# Still checks if File exists or is Empty (only username in first line n thats it, if so, send "EMPTY")
def RDT(threadtitle):
    try:
        # First used readlines()
        f = open(f"{threadtitle}", "r")
        allLinesF = f.readlines()
        numLinesF = len(allLinesF)
        # then join the list via:
        fileLines = ""
        if numLinesF > 1: # if file has no messages/file uploads, return EMPTY
            for i in range(1, numLinesF): # do not include first line ("ownerUsername")
                fileLines = fileLines + allLinesF[i] # "\n" NOT needed IFF allLinesf[i] includes "\n" at the end
                # keep in mind client does "strip()" when it recieves this from Server !!!
        # returns a string of all the contents, EACH line in file is seperated via "\n" (print out to terminal to check this)
        # when client recieves this, client does .split("\n")
        else:
            fileLines = "EMPTY"
        return fileLines
    except FileNotFoundError:
        return "File Not Found"


# Simply returns all the Active threads. If none, returns "None"
def LST():
    store = data_store.get()
    threadNames = "Niche"
    # First check threads aren't empty
    numOfThreads = len(store['threads'])
    if numOfThreads > 0:
        threadNames = ""
        for thread in store['threads']:
            threadNames = threadNames + thread['threadtitle'] + "\n"
    return threadNames


# Fnc assumes file already exists (but still checks for file in Server side)
# Writes user's message to file, and stores it in data store correspondingly.  
def MSG(threadtitle, msg, username):
    store = data_store.get()
    try:
        f = open(f"{threadtitle}", "r") # First grab the no. of lines via readlines() by "r" mode
        allLinesF = f.readlines()
        f.close()
        msgID = len(allLinesF) # This ignores the standalone "\n" issue that arises from DLT() last msgs
        msgToAppend = f"\n{msgID} {username}: {msg}"
        f = open(f"{threadtitle}", "a") # open for appending
        f.write(msgToAppend)
        f.close()
        # ~~~~~~~~ DLT() leaves newline as a whole line IFF a last line is deleted, workaround is here:
        foundaNewLine = False
        fNew = open(f"{threadtitle}", "r")
        newLinesF = fNew.readlines()
        # Check for standalone new lines for e.g. newLinesF = ["hello\n", "\n", "<newMsg>"]
        for line in newLinesF:
            if line == '\n':
                foundaNewLine = True
                newLinesF.remove(line)
        fNew.close()
        # Now write newLinesF into file IFF a newline was detected, otherwise dont bother
        if foundaNewLine is True:
            fFinal = open(f"{threadtitle}", "w") # open for writing
            for lines in newLinesF:
                fFinal.write(lines)
            fFinal.close()
        # ~~~~~~~~
        # FINALLY, add to DATA STORE
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


# Edits the msg given via msgID, if its the user and if it exists in the Thread
# First checks if File exists
def EDT(threadtitle, username, msgID, newMsg):
    store = data_store.get()
    retMsg = "File Not Found"
    # First check if File exists
    for thread in store['threads']:
        if thread['threadtitle'] == threadtitle:
            numOfMsgs = len(thread['threadMsgs'])
            retMsg = 'MsgID Is Out Of Range'
            # Then check if the msgID isn't out of range (if this IF is wrong, retMsg will stay as is)
            if msgID <= numOfMsgs and msgID > 0:
                retMsg = 'User Is Not Owner Of Msg'
                # Then check if username is owner of message
                for msgs in thread['threadMsgs']:
                    if msgs['msgID'] == msgID:
                        if msgs['msgUser'] == username:
                            # Replace old msg w/ new msg
                            msgs['msg'] = newMsg
                            retMsg = "Success"
                            break
    data_store.set(store)
    if retMsg == "Success":
        # Now go edit the message in file (assuming username is owner of msg as per above)
        f = open(f"{threadtitle}", "r")
        allLinesF = f.readlines()
        f.close()
        ctr = 0
        for i in allLinesF:
            if i[0] == str(msgID):
                # partition the file line into 3 bits (2nd bit being ":")
                parted = i.partition(":")
                if ctr == len(allLinesF) - 1: # Dont add NEWLINE if its the very last line
                    msgToAdd = parted[0] + parted[1] + " " + newMsg# + "\n"
                else: # Otherwise, add newline
                    msgToAdd = parted[0] + parted[1] + " " + newMsg + "\n"
                allLinesF[ctr] = str(msgToAdd)
                break
            ctr += 1
        # Empty out file and rewrite the whole file in, except specific line will now be edited.
        f = open(f"{threadtitle}", "w")
        for line in allLinesF:
            f.write(line)
        f.close()
    return retMsg        


# Deletes the msg given via msgID, if its the user and if it exists in the Thread
# MSG() cmd was also edited due to this fnc leaving behind an empty line when deleting a line, so MSG() features
# an IF for removing single "\n" lines from readlines() fnc
def DLT(threadtitle, msgID, username):
    # Remove msgID from data store
    store = data_store.get()
    retMsg = "File Not Found"
    # First check if File exists
    for thread in store['threads']:
        if thread['threadtitle'] == threadtitle:
            numOfMsgs = len(thread['threadMsgs'])
            retMsg = 'MsgID Is Out Of Range'
            # Then check if the msgID isn't out of range (if this IF is wrong, retMsg will stay as is)
            if msgID <= numOfMsgs and msgID > 0:
                retMsg = 'User Is Not Owner Of Msg'
                # Then check if username is owner of message
                for msgs in thread['threadMsgs']:
                    if msgs['msgID'] == msgID:
                        if msgs['msgUser'] == username:
                            # FIRST decrement all the IDs of messages after this curr message
                            decrementMsgIDs(threadtitle, msgID)
                            # Message found and confirmed, now delete it
                            thread['threadMsgs'].remove(msgs)
                            retMsg = "Success"
                            break
    data_store.set(store)
    if retMsg == "Success":
        # Now go delete the message in file (assuming username is owner of msg as per above)
        f = open(f"{threadtitle}", "r")
        allLinesF = f.readlines()
        f.close()
        ctr = 0
        for i in allLinesF:
            if i[0] == str(msgID):
                # remove the line from allLinesF
                allLinesF.remove(i)
                break
            ctr += 1
        # Empty out file and rewrite the whole file in, except specific line will now be deleted.
        f = open(f"{threadtitle}", "w")
        for line in allLinesF:
            f.write(line)
        f.close()
    return retMsg

