# For testing certain file-stuff in a smaller environment

from socket import *
import sys
from datetime import datetime
import time

def usernameExists(username):
    f = open("credentials.txt", "a") # open for reading and appending to end of file
    allLinesF = f.readlines()
    numLinesF = len(allLinesF)
    for i in range(0, numLinesF):
        # break up string into user and pass
        brokenLogin = allLinesF[i].split(" ") # this is a list
        user = brokenLogin[0]
        password = brokenLogin[1].rstrip() # removes trailing newline
        if (username == user):
            f.close()
            return True
    f.close()
    return False


if __name__ == "__main__":
    print("Going to open cred.txt file: ")
    truth = usernameExists("Han")
    if truth is True:
        print("pass exists")
    elif truth is False:
        print("pass does not exist")
    else:
        print(f"Error is: {truth}")
        