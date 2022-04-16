# For testing certain file-stuff (and more) cmds in a smaller environment

from socket import *
import os
import sys
from datetime import datetime
import time

def usernameExists(username):
    f = open("credentials.txt", "r") # open for reading and appending to end of file
    allLinesF = f.readlines()
    print(f"ALL: {allLinesF}")
    print(allLinesF[-1])
    numLinesF = len(allLinesF)
    print(numLinesF)
    for i in range(0, numLinesF):
        # break up string into user and pass
        brokenLogin = allLinesF[i].split(" ") # this is a list
        user = brokenLogin[0].rstrip()
        password = brokenLogin[1].rstrip() # removes trailing newline
        if (username == user):
            f.close()
            return True
    f.close()
    return False

def breakCmdInput(userInput):
    # break down per whitespace, and join index 2 to end, as one string
    brokenInput = userInput.split(" ")
    print(f"broken input BEFORE: {brokenInput}")
    lenBrokenInput = len(brokenInput)
    print(lenBrokenInput)
    if lenBrokenInput > 3:
        # join the 2nd+ indexes
        newIn = ''
        for i in range(2, lenBrokenInput):
            newIn = newIn + brokenInput[i] + ' '
        print(f"3rd Arg: {newIn.rstrip()}")
        # Combine all needed
        retInput = [str(brokenInput[0]), str(brokenInput[1]), str(newIn.rstrip())]
        return retInput
    
    # ELSE, its a single command args
    return brokenInput

def EDTbreakCmdInput(userInput):
    brokenInput = userInput.split(" ")
    lenBrokenInput = len(brokenInput)
    # join the 4th+ indexes
    newIn = ''
    for i in range(4, lenBrokenInput):
        newIn = newIn + brokenInput[i] + ' '
    # combine all needed
    retInput = [str(brokenInput[0]), str(brokenInput[1]), str(brokenInput[2]), str(brokenInput[3]), str(newIn.rstrip())]
    # remove whitespaces from retInput
    for i in retInput:
        if i == '':
            retInput.remove(i)
    return retInput


def appendToEOF(stringToAppend):
    f = open("credentials.txt", "a") # open in "access" mode
    f.write(stringToAppend)
    f.close()
    print(f"Appended [{stringToAppend}] to file")

def CRT(username, title):
    try:
        open(f"{title}")
        print("File found cuh")
    except FileNotFoundError:
        print("File NOT found cuh, gonna create it")
        f = open(f"{title}", "w")
        f.write(f"{username}")
        f.close()
    # for files in os.listdir('.'):
    #     print(files)
    # pass
def MSG(title, msg, username):
    # check file exists
    try:
        f = open(f"{title}", "r") ### TRY IF "r" WORKS HERE, can also user readlines()
        allLinesF = f.readlines()
        f.close()
        msgID = len(allLinesF)
        msgToAppend = f"\n{msgID} {username}: {msg}"
        f = open(f"{title}", "a") # open for appending
        f.write(msgToAppend)
        f.close()
        print("MSG added to file")
        # print()

        ### DLT() leaves newline as a whole line IFF a last line is deleted, workaround is here:
        foundaNewLine = False
        fNew = open(f"{title}", "r")
        newLinesF = fNew.readlines()
        print(f"in MSG newlinesF len({len(newLinesF)}) before: {newLinesF}")
        for line in newLinesF:
            if line == '\n':
                foundaNewLine = True
                newLinesF.remove(line)
        fNew.close()
        # Now write newLinesF into file
        if foundaNewLine is True:
            print("MSG added AND removed newlines (in new file)")
            fFinal = open(f"{title}", "w") # open for writing
            for lines in newLinesF:
                fFinal.write(lines)
            fFinal.close()
        else:
            print("MSG: No newlines found")
        # print(f"in MSG newlinesF after: {newLinesF}")
    except FileNotFoundError:
        print("MSG cmd's file not found")
        # snedto("MSG FAILURE")

def RDT(threadtitle):
    # First used readlines()
    f = open(f"{threadtitle}", "r")
    allLinesF = f.readlines()
    numLinesF = len(allLinesF)
    # then join the list via:
    fileLines = ""
    if numLinesF > 1: # if file has no messages/file uploads, return EMPTY
        for i in range(1, numLinesF):
            fileLines = fileLines + allLinesF[i] # "\n" NOT needed IFF allLinesf[i] includes "\n" at the end
            # keep in mind client does "strip()" when it recieves this from Server !!!
    else:
        fileLines = "EMPTY"
    # returns a string of all the contents, EACH line in file is seperated via "\n" (print out to terminal to check this)
    # when client recieves this, client does .split("\n")
    return fileLines

def EDT(threadtitle, username, msgID, newMsg):
    # Now go edit the message in file
    f = open(f"{threadtitle}", "r")
    allLinesF = f.readlines()
    # print(allLinesF)
    # print(allLinesF[3][0])
    # print()
    ctr = 0
    # print(f"LEN: {len(allLinesF)}")
    for i in allLinesF:
        # print(f"Line: {i}")
        if i[0] == str(msgID):
            # break down the string into 2 bits (upto ":" and beyond)
            parted = i.partition(":")
            # print(f"parted msg -> {parted}")
            if ctr == len(allLinesF) - 1: # Dont add NEWLINE if its the very last line
                msgToAdd = parted[0] + parted[1] + " " + newMsg# + "\n"
            else: # If not last line, then add newline
                msgToAdd = parted[0] + parted[1] + " " + newMsg + "\n"
            # print(f"msg to add -> {str(msgToAdd)}")
            allLinesF[ctr] = str(msgToAdd)
            break
        ctr += 1
    # print(allLinesF)
    f = open(f"{threadtitle}", "w")
    for line in allLinesF:
        f.write(line)
    f.close()
    print(f"EDT: Msg id '{msgID}' has been edited!")
    # return retMsg       

# DOESNT decrement msgIDs (implem. seperately in serverHelpers.py)
def DLT(threadtitle, msgID, username):
    # Now go edit the message in file
    f = open(f"{threadtitle}", "r")
    allLinesF = f.readlines()
    # oldLenAllLinesF = len(allLinesF)
    # print(f"in DLT: {allLinesF}")
    # print(allLinesF[3][0])
    # print()
    ctr = 0
    # print(f"LEN: {len(allLinesF)}")
    for i in allLinesF:
        # print(f"Line: {i}")
        if i[0] == str(msgID):
            # remove the line from allLinesF
            allLinesF.remove(i)
            break
        ctr += 1
    # print(allLinesF)
    # print(f"{ctr} and {oldLenAllLinesF} and {len(allLinesF)}")
    
    # print(allLinesF[ctr - 1]) # print new last line (when printed, won't include the "\n" which is present for "print(allLinesF)")
    f = open(f"{threadtitle}", "w")
    for line in allLinesF:
        f.write(line)
    f.close()
    print(f"DLT: Msg id '{msgID}' has been delete!")

    # if ctr == len(allLinesF):
    #     print(allLinesF[ctr - 1])
    #     allLinesF[ctr - 1].rstrip() # new messages are added with prefix "\n", so all g
if __name__ == "__main__":
    # pass
    # print(EDTbreakCmdInput("EDT shrek1 hans 2 hello darkness my old friend"))

    CRT("shrek", "shrek1")
    MSG("shrek1", "ogres are like onions", "shrek") # msgID 1
    MSG("shrek1", "they smell?", "donkeh") # msgID 2
    DLT("shrek1", "1", "shrek")
    # EDT("shrek1", "donkeh", "2", "im shrek")
    # DLT("shrek1", "2", "donkeh")
    # MSG("shrek1", "i just deleted m y msg", "donkeh") # msgID 2
    # DLT("shrek1", "2", "shrek")

    # f = open("shrek1", "r")
    # lines = f.readlines()
    # print(f"{len(lines)} and {lines}") # len() surprisngly doesnt include standalone msgs

    # lines = str(RDT("shrek1")).strip()
    # print(lines)

    # print("Going to open cred.txt file: ")
    # truth = usernameExists("hans")
    # if truth is True:
    #     print("user exists")
    # elif truth is False:
    #     print("user does not exist")
    # else:
    #     print(f"Error is: {truth}")

    # user = "notAmith"
    # password = "aLegend69"
    # strToAppend = "\n" + f"{user}" + f" {password}"
    # appendToEOF(strToAppend)

    # print(EDTbreakCmdInput("EDT 3331 3 hello thendi pattis"))
    
    # userIn = str(input("Enter cmd: "))
    # cmdList = breakCmdInput(userIn)
    # print(cmdList)
    # print(len(cmdList))
    # print(cmdList[0])
    # print(type(cmdList[0]))

