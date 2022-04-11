# For testing certain file-stuff (and more!) in a smaller environment

from socket import *
import sys
from datetime import datetime
import time

def usernameExists(username):
    f = open("credentials.txt", "r") # open for reading and appending to end of file
    allLinesF = f.readlines()
    # print(f"ALL: {allLinesF}")
    # print(allLinesF[-1])
    numLinesF = len(allLinesF)
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


def appendToEOF(stringToAppend):
    f = open("credentials.txt", "a") # open in "access" mode
    f.write(stringToAppend)
    f.close()
    print(f"Appended [{stringToAppend}] to file")


if __name__ == "__main__":

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
    
    # userIn = str(input("Enter cmd: "))
    # cmdList = breakCmdInput(userIn)
    # print(cmdList)
    # print(len(cmdList))
    # print(cmdList[0])
    # print(type(cmdList[0]))

        