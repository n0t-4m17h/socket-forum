# Python Version: 3.8.10
# Program written by z5361183
# 10/04/22
# Run: $ python3 client.py serverPort
from socket import *
import sys
import os
from datetime import datetime
import time

#####################
#### Helper Fncs ####
#####################
### List of Commands possible ###
listOfCmds = ["CRT", "MSG", "DLT", "EDT", "LST", "RDT", "UPD", "DWN", "RMV", "XIT"]

# Globally change currCmd value (for socket.timeout issues) (workaround of using pointers)
def currCmdEquals(string):
    global currCmd
    currCmd = string

# Break down user input into a format suitable for Command's processing
def breakCmdInput(userInput):
    # break down per whitespace, and join index 2 to end, as one string
    brokenInput = userInput.split(" ")
    lenBrokenInput = len(brokenInput)
    if lenBrokenInput > 3:
        # join the 2nd+ indexes
        newIn = ''
        for i in range(2, lenBrokenInput):
            newIn = newIn + brokenInput[i] + ' '
        # combine all needed
        retInput = [str(brokenInput[0]), str(brokenInput[1]), str(newIn.rstrip())]
        return retInput
    # ELSE, its just 1 or 2 or 3 inputs (e.g "XIT" or "DLT 3331" or "MSG 3331 hi!")
    return brokenInput

# Same fnc as above, except catered for "EDT" cmd
# ["EDT", <title>, <msgID>, <newMsg>]
def EDTbreakCmdInput(userInput):
    brokenInput = userInput.split(" ")
    lenBrokenInput = len(brokenInput)
    # join the 3rd+ indexes
    newIn = ''
    for i in range(3, lenBrokenInput):
        newIn = newIn + brokenInput[i] + ' '
    # combine all needed
    retInput = [str(brokenInput[0]), str(brokenInput[1]), str(brokenInput[2]), str(newIn.rstrip())]
    return retInput


###################
#### CMDs Fncs ####
###################

# CMD 1: User wants to exit Forum
def XIT(clientSocket, serverPort, username):
    clientSocket.sendto(f"XIT {username}".encode("utf-8"), ('localhost', int(serverPort)))
    clientSocket.close()
    sys.exit(f'Adios, "{username}"')

# CMD 2: Server needs to create the thread with the given threadtitle and username
def CRT(clientSocket, serverPort, threadtitle, username, currCmd):
    # print(f"Before: {currCmd}")
    if ("CRT RESPONSE" in currCmd) is False: # this allows Client to skip sending and go waiting for Packet, incase of socket.timeout
        clientSocket.sendto(f"CRT {threadtitle} {username}".encode("utf-8"), ('localhost', int(serverPort)))
    currCmdEquals("CMD INPUTTED WAITING CRT RESPONSE")
    # print(f"After: {currCmd}")
    resp = str(clientSocket.recvfrom(2048)[0], "utf-8").strip()
    if "TITLE TAKEN" in resp:
        return False
    else:
        return True

# CMD 3:
def RMV(clientSocket, serverPort, threadtitle, username, currCmd):
    if ("RMV RESPONSE" in currCmd) is False: # this allows Client to skip sending and go waiting for Packet, incase of socket.timeout
        clientSocket.sendto(f"RMV {threadtitle} {username}".encode("utf-8"), ('localhost', int(serverPort)))
    currCmdEquals("CMD INPUTTED WAITING RMV RESPONSE")
    resp = str(clientSocket.recvfrom(2048)[0], "utf-8").strip()
    return resp

# CMD 4:
def MSG(clientSocket, serverPort, threadtitle, msg, currCmd):
    if ("MSG RESPONSE" in currCmd) is False: # this allows Client to skip sending and go waiting for Packet, incase of socket.timeout
        # skip the {username} for this one, so we dont need to change breakCmdInput()
        clientSocket.sendto(f"MSG {threadtitle} {msg}".encode("utf-8"), ('localhost', int(serverPort)))
    currCmdEquals("CMD INPUTTED WAITING MSG RESPONSE")
    resp = str(clientSocket.recvfrom(2048)[0], "utf-8").strip()
    if "TITLE INVALID" in resp:
        return False
    else:
        return True

# CMD 5:
def RDT(clientSocket, serverPort, threadtitle, username, currCmd):
    if ("RDT RESPONSE" in currCmd) is False: # this allows Client to skip sending and go waiting for Packet, incase of socket.timeout
        # skip the {username} for this one, so we dont need to change breakCmdInput()
        clientSocket.sendto(f"RDT {threadtitle} {username}".encode("utf-8"), ('localhost', int(serverPort)))
    currCmdEquals("CMD INPUTTED WAITING RDT RESPONSE")
    resp = str(clientSocket.recvfrom(2048)[0], "utf-8").strip()
    return resp

# CMD 6:
def LST(clientSocket, serverPort, username, currCmd):
    if ("LST RESPONSE" in currCmd) is False: # this allows Client to skip sending and go waiting for Packet, incase of socket.timeout
        clientSocket.sendto(f"LST {username}".encode("utf-8"), ('localhost', int(serverPort)))
    currCmdEquals("CMD INPUTTED WAITING LST RESPONSE")
    resp = str(clientSocket.recvfrom(2048)[0], "utf-8").strip()
    return resp

# CMD 7:
def EDT(clientSocket, serverPort, threadtitle, username, msgID, newMsg, currCmd):
    if ("EDT RESPONSE" in currCmd) is False: # this allows Client to skip sending and go waiting for Packet, incase of socket.timeout
        clientSocket.sendto(f"EDT {threadtitle} {username} {msgID} {newMsg}".encode("utf-8"), ('localhost', int(serverPort)))
    currCmdEquals("CMD INPUTTED WAITING EDT RESPONSE")
    resp = str(clientSocket.recvfrom(2048)[0], "utf-8").strip()
    return resp
    
# CMD 8:
def DLT(clientSocket, serverPort, threadtitle, msgID, currCmd):
    if ("DLT RESPONSE" in currCmd) is False: # this allows Client to skip sending and go waiting for Packet, incase of socket.timeout
        clientSocket.sendto(f"DLT {threadtitle} {msgID}".encode("utf-8"), ('localhost', int(serverPort)))
    currCmdEquals("CMD INPUTTED WAITING DLT RESPONSE")
    resp = str(clientSocket.recvfrom(2048)[0], "utf-8").strip()
    return resp

# CMD 9:
def UPD(clientSocket, serverPort, threadtitle, filename, currCmd):
    if ("UPD RESPONSE" in currCmd) is False: # this allows Client to skip sending and go waiting for Packet, incase of socket.timeout
        clientSocket.sendto(f"UPD {threadtitle} {filename}".encode("utf-8"), ('localhost', int(serverPort)))
    currCmdEquals("CMD INPUTTED WAITING UPD RESPONSE")
    resp = str(clientSocket.recvfrom(2048)[0], "utf-8").strip()
    return resp

# CMD 10:
def DWN(clientSocket, serverPort, threadtitle, msgID, currCmd):
    pass

# let the OS pick a random Client Port -> "sock.bind(('localhost', 0))", selected port is in "sock.getsockname()"
# REFER TO LAB02 !!!!****
##################
#### MAIN Fnc ####
##################
if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit('Execute program as such: $python3 client.py <server_port>')
    global currCmd
    currCmd = ""
    serverPort = int(sys.argv[1])
    WAIT_TIME_NRML = 0.7 # wait time for non-image commands
    WAIT_TIME_IMG = 2 # wait time for image transfers

    clientSocket = socket(AF_INET, SOCK_DGRAM) # sock_dgram == UDP socket
    # Set the timeout time if packet is taking too long/lost
    clientSocket.settimeout(WAIT_TIME_NRML)
    currCmd = ""
    enterUser = True
    respStr = ""
    currUsername = "" # save curr User's username for CMDs section
    while 1: # while loop 1 for logging onto server
        # try-except block used for sockettimeout timer 
        try:
            if "ENTER USERNAME" in currCmd or enterUser is True:
                goToWhile2 = False
                username = str(input("Enter username: "))
                clientSocket.sendto(username.encode("utf-8"), ('localhost', serverPort))
                # Wait for Server to respond with either "WRONG/VALID USERNAME"
                currCmd = "ENTER USERNAME"
                response, serverAddress = clientSocket.recvfrom(2048)
                respStr = (response.decode("utf-8")).strip()
            # IF username doesn't exist, then prompt it again (i.e restart loop)
            if respStr == "WRONG USERNAME":
                print("Invalid username")
                enterUser = True
                continue
            # IF Server decides its gonna create this new user, then send Server a password from user
            elif respStr == "NEW USERS PASSWORD":
                if ("NEW USERS PASSWORD" in currCmd) is False: # prevent password re-prompt & go straight to waiting for response 
                    password = str(input("Enter new password: "))
                    clientSocket.sendto(password.encode("utf-8"), ('localhost', serverPort))
                    currCmd = "NEW USERS PASSWORD"
                currCmd = "NEW USERS PASSWORD"
                response = str(clientSocket.recvfrom(2048)[0], "utf-8").strip()
                if response == "NEW USER LOGGED IN":
                    enterUser = False
                    currUsername = username
                    goToWhile2 = True
                    break
            # IF given Username matches Server's files, then send Server the matching password
            elif respStr == "VALID USERNAME":
                if ("ENTER PASSWORD" in currCmd) is False: # prevent password re-prompt
                    password = str(input("Enter password: "))
                    clientSocket.sendto(password.encode("utf-8"), ('localhost', serverPort))
                    currCmd = "ENTER PASSWORD"
                enterUser = False
                currCmd = "ENTER PASSWORD"
                response = str(clientSocket.recvfrom(2048)[0], "utf-8")
                if response == "WRONG PASSWORD":
                    print("Wrong password")
                    enterUser = True
                    continue
                else: # if resp = "VALID PASSWORD"
                    enterUser = False
                    currUsername = username
                    goToWhile2 = True
                    break
        
        except Exception as e:
            # Upon socket.timeout()
            if (str(e).rstrip()) == "timed out":
                print("Server's packet timedout, retrying...")
                # print(f"Last currCmd value: {currCmd}")
                continue
            else:
                print(f"e: {e}")
        # Upon "ctrl + c"
        except KeyboardInterrupt:
            print("\nKilling client...")
            goToWhile2 = False # just in case
            break

    # upon successful authentication, we can now enter forums
    if goToWhile2 is True:
        print("====================\nWelcome to the forum\n====================")
        while 1: 
            try:
                # This IF is for cases when timeout occurs and CMD input already occurred
                if ("CMD INPUTTED" in currCmd) is False:
                    cmdInput = str(input("\nEnter one of the following commands: CRT, MSG, DLT, EDT, LST, RDT, UPD, DWN, RMV, XIT: "))
                    currCmdEquals("CMD INPUTTED")
                    # break down cmdInput into a list of args 
                    cmdList = breakCmdInput(cmdInput) # cmdList[0] is the cmd, [1] is 2nd, and [3] is final arg
                if (cmdList[0] in listOfCmds) is False:
                    print("Invalid command")
                    currCmdEquals("ENTER CMD")
                    continue
                # CRT
                elif cmdList[0] == "CRT":
                    # Include CRT-specific error checking !!
                    if len(cmdList) != 2: # should only be "CRT <title>"
                        print("Incorrect syntax for CRT")
                        currCmdEquals("ENTER CMD")
                        continue
                    else:
                        ret = CRT(clientSocket, serverPort, cmdList[1], currUsername, currCmd)
                        if ret == False:
                            print("Threadtitle taken, please try again...")
                            currCmdEquals("ENTER CMD")
                            continue
                        else:
                            print(f'Thread "{cmdList[1]}" created!')
                            currCmdEquals("ENTER CMD")
                            continue
                # RMV
                elif cmdList[0] == "RMV":
                    if len(cmdList) != 2:
                        print("Incorrect syntax for RMV")
                        currCmdEquals("ENTER CMD")
                        continue
                    else:
                        ret = str(RMV(clientSocket, serverPort, cmdList[1], currUsername, currCmd)).strip()
                        if "FILE NOT FOUND" in ret:
                            print(f'Thread "{cmdList[1]}" not found')
                            currCmdEquals("ENTER CMD")
                            continue
                        elif "NOT OWNER" in ret:
                            print(f'You are not the owner of thread "{cmdList[1]}"')
                            currCmdEquals("ENTER CMD")
                            continue
                        elif "FILE REMOVED" in ret:
                            print(f'Removed thread "{cmdList[1]}"!')
                            currCmdEquals("ENTER CMD")
                            continue
                # LST
                elif cmdList[0] == "LST":
                    if len(cmdList) != 1:
                        print("Incorrect syntax for LST")
                        currCmdEquals("ENTER CMD")
                        continue
                    else:
                        ret = LST(clientSocket, serverPort, username, currCmd)
                        if ret == "Niche":
                            print("There are no active threads right now")
                            currCmdEquals("ENTER CMD")
                            continue
                        else:
                            print(f'==== Listing all threads')
                            print(ret)
                            print(f'==== Done listing!')
                            currCmdEquals("ENTER CMD")
                            continue
                # MSG
                elif cmdList[0] == "MSG":
                    # Remove any whitespace included, mistakingly leads to extra args (for e.g. "MSG 3331 " (3args) instead of "MSG 3331" (2args))
                    for i in cmdList:
                        if i == '':
                            cmdList.remove(i)
                    if len(cmdList) != 3: # should only be "MSG <title> '<arg1>...<argX>'", everything after <title> is grouped as one string
                        print("Incorrect syntax for MSG")
                        currCmdEquals("ENTER CMD")
                        continue
                    else:
                        ret = MSG(clientSocket, serverPort, cmdList[1], cmdList[2], currCmd)
                        if ret == False:
                            print(f'Thread "{cmdList[1]}" not found')
                            currCmdEquals("ENTER CMD")
                            continue
                        else:
                            print(f'Message sent in thread "{cmdList[1]}"!')
                            currCmdEquals("ENTER CMD")
                            continue
                # RDT
                elif cmdList[0] == "RDT":
                    if len(cmdList) != 2: # should only be "RDT <title>""
                        print("Incorrect syntax for RDT")
                        currCmdEquals("ENTER CMD")
                        continue
                    else:
                        ret = RDT(clientSocket, serverPort, cmdList[1], username, currCmd)
                        if ret == "FILE NOT FOUND":
                            print(f'Thread "{cmdList[1]}" not found')
                            currCmdEquals("ENTER CMD")
                            continue
                        elif ret == "EMPTY":
                            print(f'Thread "{cmdList[1]}" is empty')
                            currCmdEquals("ENTER CMD")
                            continue
                        else:
                            print(f'==== Reading "{cmdList[1]}"')
                            print(ret)
                            print(f'==== Done reading!')
                            currCmdEquals("ENTER CMD")
                            continue
                # EDT
                elif cmdList[0] == "EDT":
                    if len(cmdList) < 3: # should only be "EDT <title> <msgID> <msg...>" atleast
                        print("Incorrect syntax for EDT")
                        print("here")
                        currCmdEquals("ENTER CMD")
                        continue
                    # Since EDT has 3 extra args, its a special case (breakCmdInput() will is not wired for EDT cmds)
                    listToSend = EDTbreakCmdInput(cmdInput)
                    if len(listToSend) != 4:
                        print("Incorrect syntax for EDT")
                        print("there")
                        currCmdEquals("ENTER CMD")
                        continue
                    # Check if msgID is a number (isinstance() may raise error if msgID == "hello" for e.g.)
                    try:
                        if isinstance(int(listToSend[2]), int) is False:
                            print("Please enter an integer for message ID")
                            currCmdEquals("ENTER CMD")
                            continue
                    except: # ValueError 
                        print("Please enter an integer for message ID")
                        currCmdEquals("ENTER CMD")
                        continue
                    #                                    <thread>     <username>   <msgID>        <newMsg>
                    ret = EDT(clientSocket, serverPort, listToSend[1], username, listToSend[2], listToSend[3], currCmd)
                    if ret == "FILE NOT FOUND":
                            print(f'Thread "{cmdList[1]}" not found')
                            currCmdEquals("ENTER CMD")
                            continue
                    elif ret == "MSGID IS OUT OF RANGE":
                        print(f'Invalid message ID "{listToSend[2]}"')
                        currCmdEquals("ENTER CMD")
                        continue
                    elif ret == "USER IS NOT OWNER":
                        print(f'Incorrect owner of the message with ID "{listToSend[2]}"')
                        currCmdEquals("ENTER CMD")
                        continue
                    else: # ret == "SUCCESS" 
                        print(f'Message ID "{listToSend[2]}" in "{listToSend[1]}" has been edited!')
                        currCmdEquals("ENTER CMD")
                        continue
                # DLT
                elif cmdList[0] == "DLT":
                    if len(cmdList) != 3: # should only be "DLT <title> <msgID>"
                        print("Incorrect syntax for DLT")
                        currCmdEquals("ENTER CMD")
                        continue
                    try:
                        if isinstance(int(cmdList[2]), int) is False:
                            print("Please enter an integer for message ID")
                            currCmdEquals("ENTER CMD")
                            continue
                    except: # ValueError 
                        print("Please enter an integer for message ID")
                        currCmdEquals("ENTER CMD")
                        continue
                    ret = DLT(clientSocket, serverPort, cmdList[1], cmdList[2], currCmd)
                    if ret == "FILE NOT FOUND":
                            print(f'Thread "{cmdList[1]}" not found')
                            currCmdEquals("ENTER CMD")
                            continue
                    elif ret == "MSGID IS OUT OF RANGE":
                        print(f'Invalid message ID "{cmdList[2]}"')
                        currCmdEquals("ENTER CMD")
                        continue
                    elif ret == "USER IS NOT OWNER":
                        print(f'Incorrect owner of the message with ID "{cmdList[2]}"')
                        currCmdEquals("ENTER CMD")
                        continue
                    else: # ret == "SUCCESS" 
                        print(f'Message ID "{cmdList[2]}" in "{cmdList[1]}" has been deleted!')
                        currCmdEquals("ENTER CMD")
                        continue
                # UPD
                elif cmdList[0] == "UPD":
                    if len(cmdList) != 3: # should only be "UPD <title> <filename>"
                        print("Incorrect syntax for UPD")
                        currCmdEquals("ENTER CMD")
                        continue
                    # Give Server the command && Wait for server response
                    ret = UPD(clientSocket, serverPort, cmdList[1], cmdList[2], currCmd)
                    if ret == "FILE NOT FOUND":
                        print(f'Thread "{cmdList[1]}" not found')
                        currCmdEquals("ENTER CMD")
                        continue
                    elif ret == "FILE EXISTS IN THREAD":
                        print(f'File "{cmdList[2]}" already exists in thread "{cmdList[1]}"')
                        currCmdEquals("ENTER CMD")
                        continue
                    else: # ret == "SUCCESS" 
                        # Greenlit by Server, now do this:
                        
                        # Tell Server to open TCP connection, then do file transfer

                        # once done, close TCP connection
                        print(f'File "{cmdList[2]}" successfully uploaded to "{cmdList[1]}"!')
                        currCmdEquals("ENTER CMD")
                        continue
                # DWN
                elif cmdList[0] == "DWN":
                    if len(cmdList) != 3: # should only be "DWN <title> <filename>"
                        print("Incorrect syntax for DWN")
                        currCmdEquals("ENTER CMD")
                        continue
                    # Tell Server to open TCP connection, then do file transfer
                    # once done, close TCP connection
                    pass
                # XIT
                elif cmdList[0] == "XIT":
                    if len(cmdList) != 1:
                        print("WRONG syntax for XIT")
                    else:
                        XIT(clientSocket, serverPort, username)
        
            except Exception as e:
                # Upon socket.timeout()
                if (str(e).rstrip()) == "timed out":
                    print("Server's packet timedout, retrying...")
                    # print(f"Last currCmd value: {currCmd}") # ONLY FOR DEBUGGING
                    continue
                else:
                    print(f"ERROR: {e}")
                    continue
            # Upon "ctrl + c"
            # except KeyboardInterrupt:
                # XIT(clientSocket, serverPort, username)

    clientSocket.close()
