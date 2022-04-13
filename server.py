# Python Version: 3.8.10
# Program written by z5361183
# 10/04/22
# Run: $ python3 server.py serverPort 
from serverHelpers import *
from socket import *
import os
import sys
from datetime import datetime
import time

### Main Data Structure ###
dataStore = {
    'users': [],
    'threads': []
}

###################
### Helper Fncs ###
###################


#################
### CMDS fncs ###
#################

# deez
def RMV():
    pass

##################
#### MAIN Fnc ####
##################
if __name__ == "__main__":
    if (len(sys.argv) != 2):
        sys.exit("Execute program as such: $python3 server.py <server_port>")
    dataStoreClear()
    serverPort = int(sys.argv[1])
    WAIT_TIME_AUTH = 20 # wait time for authentication stage 
    WAIT_TIME_CMDS = 30 # for CMDs-input stage (NOTE: not good, cause User needs more time to read a thread for e.g)
    WAIT_TIME_IMG = 30 # wait time for image transfers

    serverSocket = socket(AF_INET, SOCK_DGRAM) 
    serverSocket.bind(('localhost', serverPort))
    # serverSocket.listen(1) # only for TCP ??

    while 1: # while loop 1 for Server's infinite loop
        try:
            print("Server waiting for clients...")
            usernameMsg, clientAddr = serverSocket.recvfrom(2048)
            print("Client authenticating")
            prevUsernameInput = ""
            checkForNewUserIter, i = 0, 0
            currCmd = ""
            userOnline = True
            while userOnline: # while loop 2 for authenticating
                serverSocket.settimeout(WAIT_TIME_AUTH) # Assuming user enters Auth-cmds within 20secs
                # messagePass, clientAddr = serverSocket.recvfrom(2048)
                try:
                    if i == 0: # this is Just for the first loop ONLY
                        username = (usernameMsg.decode("utf-8")).strip()
                        i += 1
                    # (i != 7) helped debug an issue with currCmd = "NEW USER", as when socket.timeout occured there, it wouldnt return to there, instead come straight here
                    elif ("WAITING USERNAME" in currCmd) or (i != 0 and i != 7): # this is for if the username prev entered is ticked as wrong, so on the 2nd input, wanna create a new user
                        currCmd = "WAITING USERNAME"
                        username = (str(serverSocket.recvfrom(2048)[0], "utf-8")).strip()
                    # FIRST check conditions are for cases of socket.timeout()
                    if "VALID USERNAME" in currCmd or usernameExists(username) is True:
                        if ("PASSWORD" in currCmd) is False: # prevents access to here, as "PASSWORD" is in next IF
                            checkForNewUserIter = 0 # reset the "check if new username is inputted" to 0
                            serverSocket.sendto("VALID USERNAME".encode("utf-8"), clientAddr) # Wait for password next
                            currCmd = "VALID USERNAME" # used incase of sockettimeout
                            password = (str(serverSocket.recvfrom(2048)[0], "utf-8")).strip()
                        # Check if username and password combo matches in credentials.txt
                        if "WRONG PASSWORD" in currCmd or checkUserPassCombo(username, password) is False:
                            serverSocket.sendto("WRONG PASSWORD".encode("utf-8"), clientAddr)
                            currCmd = "VALID USERNAME WRONG PASSWORD"
                            print(f'Wrong Password for "{username}"')
                            continue # loop back again, waiting for username
                        elif "VALID PASSWORD" in currCmd or checkUserPassCombo(username, password) is True:
                            # ADD USER to data store, and go to while loop 3
                            serverSocket.sendto("VALID PASSWORD".encode("utf-8"), clientAddr)
                            currCmd = "VALID USERNAME VALID PASSWORD"
                            print(f'"{username}" successful login')
                            createNewUser(username, password, True, False)

                    elif "WRONG USERNAME" in currCmd or "NEW USER" in currCmd or usernameExists(username) is False: # else its a NEW user
                        if "WRONG USERNAME 1" in currCmd or checkForNewUserIter == 0: # User has only inputted Invalid username ONCE; isn't creating a new user, yet
                            # respond to Client with "WRONG USERNAME"
                            serverSocket.sendto("WRONG USERNAME".encode("utf-8"), clientAddr)
                            currCmd = "WRONG USERNAME 1"
                            print(f'Wrong username: "{username}"')
                            checkForNewUserIter += 1
                            prevUsernameInput = username
                            continue # loop while 1 again
                        # User has now entered invalid Username TWICE, but 2nd input is different to first input, so not creating a new user, yet
                        elif "WRONG USERNAME 2" in currCmd or prevUsernameInput != username:
                            serverSocket.sendto("WRONG USERNAME".encode("utf-8"), clientAddr)
                            currCmd = "WRONG USERNAME 2"
                            print(f'Wrong username: "{username}"')
                            prevUsernameInput = username
                            continue
                        # if iterator != 0 && prevUserInput == user, 
                        # then User's being prompted by Client a 2nd time, so create a new User now
                        else:
                            # request Client for password and append both to credentials.txt file (createNewUser() will do that)
                            # dont resend request if coming back from socket.timeout
                            if ("NEW USER" in currCmd) is False:
                                serverSocket.sendto("NEW USERS PASSWORD".encode("utf-8"), clientAddr)
                            print(f'Detected new user "{username}", waiting for new password')
                            currCmd = "NEW USER" 
                            i = 7
                            password = (str(serverSocket.recvfrom(2048)[0], "utf-8")).strip()
                            createNewUser(username, password, True, True)
                            serverSocket.sendto("NEW USER LOGGED IN".encode("utf-8"), clientAddr)
                            print(f'"{username}" successful login!')
                            # code now jumps to 3rd while loop, in 3 lines

                    checkForNewUserIter = 0 # reset this for the next Client ??
                    while 1: # while loop 3 for normal COMMANDS (after logging in)
                        try:
                            serverSocket.settimeout(WAIT_TIME_CMDS) # Assuming user enters a CMD within 30secs
                            # request msg from Client, and break it down via its formatting ("<cmd> <arg1>...<argX>")
                            currCmd = "WAITING FOR CMD"
                            cmdMsg = (str(serverSocket.recvfrom(2048)[0], "utf-8")).strip()
                            cmdMsgBroken = breakCmdMsg(cmdMsg)
                            if cmdMsgBroken[0] == "XIT":
                                currCmd = "XIT"
                                changeUserActive(username, False)
                                print(f'"{username}" exited\n')
                                userOnline = False # this'll break the 2nd while loop, making Server now wait for clients
                                break
                            elif cmdMsgBroken[0] == "CRT":
                                print(f'"{username}" issued CRT command')
                                currCmd = "CRT"
                                if CRT(cmdMsgBroken[1], cmdMsgBroken[2]) is True:
                                    serverSocket.sendto("CRT SUCCESS".encode("utf-8"), clientAddr)
                                    print(f'"{username}" created thread "{cmdMsgBroken[1]}"!')
                                else:
                                    serverSocket.sendto("CRT TITLE TAKEN".encode("utf-8"), clientAddr)
                                    print(f'Failed to create "{username}"s thread "{cmdMsgBroken[1]}"')
                            elif cmdMsgBroken[0] == "MSG":
                                pass
                            elif cmdMsgBroken[0] == "DLT":
                                pass
                            elif cmdMsgBroken[0] == "EDT":
                                pass
                            elif cmdMsgBroken[0] == "LST":
                                # when sending Thread's contents to Client, have a "\n" for every newline
                                pass
                            elif cmdMsgBroken[0] == "RDT":
                                pass
                            elif cmdMsgBroken[0] == "RMV":
                                pass
                            elif cmdMsgBroken[0] == "UPD":
                                pass
                            elif cmdMsgBroken[0] == "DWN":
                                pass
                        # while 3's try-excepts
                        except Exception as e:
                            # Upon socket.timeout()
                            if (str(e).rstrip()) == "timed out":
                                print("Client's packet timed out, retrying...")
                                # print(f"Last currCmd value: {currCmd}") # FOR DEBUGGING
                                continue
                        # Upon "ctrl + c"
                        except KeyboardInterrupt:
                            killServer(serverSocket)
                # while 2's try-excepts
                except Exception as e:
                    # Upon socket.timeout()
                    if (str(e).rstrip()) == "timed out":
                        print("Client's packet timed out, retrying...")
                        print(f"Last currCmd value: {currCmd}") # FOR DEBUGGING
                        continue
                # Upon "ctrl + c"
                except KeyboardInterrupt:
                    killServer(serverSocket)
        # while 1's try-excepts
        except Exception as e:
            # Upon socket.timeout()
            if (str(e).rstrip()) == "timed out":
                print("Client's packet timed out, retrying...")
                continue
            else:
                print(f"ERROR: {e}")
                continue
        except KeyboardInterrupt:
            killServer(serverSocket)
