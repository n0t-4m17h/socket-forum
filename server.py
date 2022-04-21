# Python Version: 3.8.10
# Program written by z5361183
# 10/04/22
# Run: $ python3 server.py serverPort 
from serverHelpers import *
from dataStore import data_store
from socket import *
import os
import sys
from datetime import datetime
import time

#################
### CMDS fncs ###
#################



##################
#### MAIN Fnc ####
##################
if __name__ == "__main__":
    if (len(sys.argv) != 2):
        sys.exit("Execute program as such: $python3 server.py <server_port>")
    serverPort = int(sys.argv[1])
    WAIT_TIME_INF = 86400 # 24hrs
    WAIT_TIME_AUTH = 20 # wait time for authentication stage 
    WAIT_TIME_CMDS = 30 # for CMDs-input stage (NOTE: not good, cause User needs more time to read a thread for e.g)
    WAIT_TIME_IMG = 30 # wait time for image transfers

    serverSocket = socket(AF_INET, SOCK_DGRAM) 
    serverSocket.bind(('localhost', serverPort))
    # serverSocket.listen(1) # only for TCP ??

    while 1: # while loop 1 for Server's infinite loop
        try:
            print("Server waiting for clients...")
            serverSocket.settimeout(WAIT_TIME_INF)
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
                    # currCmd = "WAITING FOR CMD" # to pass next IF
                    checkForNewUserIter = 0 # reset this for the next Client ??
                    while 1: # while loop 3 for normal COMMANDS (after logging in)
                        try:
                            serverSocket.settimeout(WAIT_TIME_CMDS) # Assuming user enters a CMD within 30secs
                            # request msg from Client, and break it down via "<cmd> <arg1>...<argX>"
                            # # This IF prevents waiting for CMD, incases of socket timeout
                            # # if "WAITING FOR CMD" in currCmd:
                            currCmd = "WAITING FOR CMD"
                            cmdMsg = (str(serverSocket.recvfrom(2048)[0], "utf-8")).strip()
                            cmdMsgBroken = breakCmdMsg(cmdMsg)
                            # XIT
                            if cmdMsgBroken[0] == "XIT":
                                currCmd = "XIT"
                                changeUserActive(username, False)
                                print(f'"{username}" EXITED\n')
                                userOnline = False # this'll break the 2nd while loop, making Server now wait for clients
                                break
                            # CRT
                            elif cmdMsgBroken[0] == "CRT":
                                print(f'"{username}" issued CRT command')
                                currCmd = "CRT"
                                # Pass in threadtitle then username
                                if CRT(cmdMsgBroken[1], cmdMsgBroken[2]) is True:
                                    serverSocket.sendto("CRT SUCCESS".encode("utf-8"), clientAddr)
                                    print(f'"{username}" created THREAD "{cmdMsgBroken[1]}"!')
                                else:
                                    serverSocket.sendto("CRT TITLE TAKEN".encode("utf-8"), clientAddr)
                                    print(f'Failed to create "{username}"s THREAD "{cmdMsgBroken[1]}"')
                            # RMV
                            elif cmdMsgBroken[0] == "RMV":
                                print(f'"{username}" issued RMV command')
                                currCmd = "RMV"
                                rmvRet = RMV(cmdMsgBroken[1], username)
                                if "File Not Found" in rmvRet:
                                    serverSocket.sendto("FILE NOT FOUND".encode("utf-8"), clientAddr)
                                    print(f'"{username}" failed to remove non-existent thread "{cmdMsgBroken[1]}"')
                                elif "Not Owner" in rmvRet:
                                    serverSocket.sendto("NOT OWNER".encode("utf-8"), clientAddr)
                                    print(f'"{username}" not owner of "{cmdMsgBroken[1]}", failed to remove')
                                else: # "Thread Removed" in rmvRet:
                                    # Successfully removed file
                                    serverSocket.sendto("FILE REMOVED SUCCESS".encode("utf-8"), clientAddr)
                                    print(f'"{username}" deleted thread "{cmdMsgBroken[1]}"!')
                            # LST
                            elif cmdMsgBroken[0] == "LST":
                                # when sending Thread's contents to Client, have a "\n" for every newline
                                print(f'"{username}" issued LST command')
                                currCmd = "LST"
                                # pass in threadtitle for reading
                                lstRet = LST()
                                serverSocket.sendto(lstRet.encode("utf-8"), clientAddr)
                                print(f'"{username}" is viewing all listed threadtitles!')
                            # MSG
                            elif cmdMsgBroken[0] == "MSG":
                                print(f'"{username}" issued MSG command')
                                currCmd = "MSG"
                                # Pass in threadtitle then 'msg'
                                if MSG(cmdMsgBroken[1], cmdMsgBroken[2], username) is True:
                                    serverSocket.sendto("MSG SUCCESS".encode("utf-8"), clientAddr)
                                    print(f'"{username}" sent a message in thread "{cmdMsgBroken[1]}"!')
                                else:
                                    serverSocket.sendto("MSG TITLE INVALID".encode("utf-8"), clientAddr)
                                    print(f'"{username}" failed to send message to invalid thread "{cmdMsgBroken[1]}"')
                            # RDT
                            elif cmdMsgBroken[0] == "RDT":
                                print(f'"{username}" issued RDT command')
                                currCmd = "RDT"
                                # pass in threadtitle for reading
                                rdtRet = RDT(cmdMsgBroken[1])
                                if "File Not Found" == rdtRet:
                                    serverSocket.sendto("FILE NOT FOUND".encode("utf-8"), clientAddr)
                                    print(f'"{username}" failed to read non-existent thread "{cmdMsgBroken[1]}"')
                                else: # OR "EMPTY" == rdtRet:
                                    # Send read contents of file
                                    serverSocket.sendto(rdtRet.encode("utf-8"), clientAddr)
                                    print(f'"{username}" is reading thread "{cmdMsgBroken[1]}"!')
                            # EDT
                            elif cmdMsgBroken[0] == "EDT":
                                print(f'"{username}" issued EDT command')
                                currCmd = "EDT"
                                # BREAK DOWN CMD AS PER CLIENT.PY'S HELPER, SPECIAL CASE OF EDT
                                EDTrespBroken = EDTbreakResp(cmdMsg)
                                # pass in threadtitle, username, msgID & newMsg, for processing
                                #               <thread>                     <msgID>         <newMsg>
                                edtRet = EDT(EDTrespBroken[1], username, int(EDTrespBroken[3]), EDTrespBroken[4])
                                if "File Not Found" == edtRet:
                                    serverSocket.sendto("FILE NOT FOUND".encode("utf-8"), clientAddr)
                                    print(f'"{username}" failed to edit msg in non-existent thread "{EDTrespBroken[1]}"')
                                elif "MsgID Is Out Of Range" == edtRet:
                                    serverSocket.sendto("MSGID IS OUT OF RANGE".encode("utf-8"), clientAddr)
                                    print(f'"{username}"s msgID "{EDTrespBroken[3]}" is out of range in thread "{EDTrespBroken[1]}"')
                                elif "User Is Not Owner Of Msg" == edtRet:
                                    serverSocket.sendto("USER IS NOT OWNER".encode("utf-8"), clientAddr)
                                    print(f'"{username}" is not owner of msgID "{EDTrespBroken[3]}" in thread "{EDTrespBroken[1]}"')
                                else: # "Success" == edtRet
                                    serverSocket.sendto("SUCCESS".encode("utf-8"), clientAddr)
                                    print(f'"{username}" edited msgID "{EDTrespBroken[3]}" in thread "{EDTrespBroken[1]}"!')
                            # DLT
                            elif cmdMsgBroken[0] == "DLT":
                                print(f'"{username}" issued DLT command')
                                currCmd = "DLT"
                                #               <thread>             <msgID>
                                dltRet = DLT(cmdMsgBroken[1], int(cmdMsgBroken[2]), username)
                                if "File Not Found" == dltRet:
                                    serverSocket.sendto("FILE NOT FOUND".encode("utf-8"), clientAddr)
                                    print(f'"{username}" failed to delete msg in non-existent thread "{cmdMsgBroken[1]}"')
                                elif "MsgID Is Out Of Range" == dltRet:
                                    serverSocket.sendto("MSGID IS OUT OF RANGE".encode("utf-8"), clientAddr)
                                    print(f'"{username}"s msgID "{cmdMsgBroken[2]}" is out of range in thread "{cmdMsgBroken[1]}"')
                                elif "User Is Not Owner Of Msg" == dltRet:
                                    serverSocket.sendto("USER IS NOT OWNER".encode("utf-8"), clientAddr)
                                    print(f'"{username}" is not owner of msgID "{cmdMsgBroken[2]}" in thread "{cmdMsgBroken[1]}"')
                                else: # "Success" == dltRet
                                    serverSocket.sendto("SUCCESS".encode("utf-8"), clientAddr)
                                    print(f'"{username}" deleted msgID "{cmdMsgBroken[2]}" in thread "{cmdMsgBroken[1]}"!')
                            # UPD
                            elif cmdMsgBroken[0] == "UPD":
                                print(f'"{username}" issued UPD command')
                                currCmd = "UPD"
                                #               <thread>         <filename>
                                updRet = UPD(cmdMsgBroken[1], cmdMsgBroken[2], username)
                                if "File Not Found" == updRet: # THis means "threadtitle" is invalid !!!
                                    serverSocket.sendto("FILE NOT FOUND".encode("utf-8"), clientAddr)
                                    print(f'"{username}" failed to upload file to non-existent thread "{cmdMsgBroken[1]}"')
                                elif "File Exists In Thread" == updRet:
                                    serverSocket.sendto("FILE EXISTS IN THREAD".encode("utf-8"), clientAddr)
                                    print(f'"{username}" failed to upload already-existent file "{cmdMsgBroken[2]}" in thread "{cmdMsgBroken[1]}"')
                                else: # "Success" == updRet
                                    serverSocket.sendto("SUCCESS".encode("utf-8"), clientAddr)
                                    respMsg = (str(serverSocket.recvfrom(2048)[0], "utf-8")).strip()
                                    if respMsg == "UDP REQUESTING CONNECTION":
                                        # Now Open TCP socket && read in file's contents
                                        serverSocketTCP = socket(AF_INET, SOCK_STREAM)  # sock_stream == TCP socket
                                        serverSocketTCP.bind(('localhost', int(serverPort)))
                                        serverSocketTCP.listen(1)
                                        # Send via UDP, that TCP socket is open
                                        serverSocket.sendto("TCP OPEN".encode("utf-8"), clientAddr)
                                        # Client now creates its connection socket and connects to Server's TCP socket
                                        connectionSocket, clientTCPaddr = serverSocketTCP.accept()
                                        # print(f'New TCP connection from: "{clientTCPaddr}" of user "{username}"')

                                        # Recieve file as BYTES and write them into cwd as BYTEs ('wb')
                                        # First ask for the size of the file (UDP), then ask for the file's contents
                                        fileSizeStr = str(serverSocket.recvfrom(2048)[0], "utf-8").strip()
                                        # Now wait for the file itself (TCP)
                                        fileContentsResp = connectionSocket.recv(int(fileSizeStr))
                                        newFileName = str(cmdMsgBroken[1]) + "-" + str(cmdMsgBroken[2])
                                        f = open(newFileName.strip(), "wb")
                                        f.write(fileContentsResp)
                                        f.close()
                                        # print("Closing TCP connection AND socket")
                                        connectionSocket.close()
                                        serverSocketTCP.close()
                                        # Send via UDP, that the file has been uploaded
                                        serverSocket.sendto("FILE UPLOADED".encode("utf-8"), clientAddr)
                                        print(f'"{username}" uploaded file "{cmdMsgBroken[2]}" to thread "{cmdMsgBroken[1]}"!')
                            # DWN
                            elif cmdMsgBroken[0] == "DWN":
                                print(f'"{username}" issued DWN command')
                                currCmd = "DWN"
                                #               <thread>         <filename>
                                dwnRet = DWN(cmdMsgBroken[1], cmdMsgBroken[2], username)
                                if "File Not Found" == dwnRet: # THis means "threadtitle" is invalid !!!
                                    serverSocket.sendto("FILE NOT FOUND".encode("utf-8"), clientAddr)
                                    print(f'"{username}" failed to download a file from non-existent thread "{cmdMsgBroken[1]}"')
                                elif "File Not In Thread" == dwnRet:
                                    serverSocket.sendto("FILE NOT IN THREAD".encode("utf-8"), clientAddr)
                                    print(f'"{username}" failed to download a non-existent file "{cmdMsgBroken[2]}" in thread "{cmdMsgBroken[1]}"')
                                else: # "Success" == dwnRet
                                    serverSocket.sendto("SUCCESS".encode("utf-8"), clientAddr)
                                    # Client waits for connection "recv"
                                    respMsg = (str(serverSocket.recvfrom(2048)[0], "utf-8")).strip()
                                    if respMsg == "UDP REQUESTING CONNECTION":
                                        # Now Open TCP socket && read in file's contents
                                        serverSocketTCPdwn = socket(AF_INET, SOCK_STREAM)  # sock_stream == TCP socket
                                        print("binding")
                                        serverSocketTCPdwn.bind(('localhost', int(serverPort)))
                                        serverSocketTCPdwn.listen(1)
                                        # Send via UDP, that TCP socket is open
                                        print("sending 'TCP OPEN'")
                                        serverSocket.sendto("TCP OPEN".encode("utf-8"), clientAddr)
                                        # Client now creates its connection socket and connects to Server's TCP socket
                                        print("accepting connection")
                                        connectionSocket, clientTCPaddr = serverSocketTCPdwn.accept()
                                        # Read in file as BYTES and send it as BYTES
                                        expectedFiletitle = str(cmdMsgBroken[1] + "-" + cmdMsgBroken[2]) # This is name of file in server's CWD
                                        f = open(expectedFiletitle, "rb").read()
                                        contLen = len(f) # in bytes
                                        # First send the expected file size (UDP)
                                        print("sending file size")
                                        serverSocket.sendto(f"{contLen}".encode("utf-8"), clientAddr)
                                        # Now send the whole file (TCP)
                                        print("sending file")
                                        connectionSocket.sendall(f)
                                        # once done, close TCP connection
                                        print("closing socket")
                                        connectionSocket.close()
                                        serverSocketTCPdwn.close()
                                        # Get recieved confirmation from Client
                                        respMsg = (str(serverSocket.recvfrom(2048)[0], "utf-8")).strip()
                                        if respMsg == "FILE DOWNLOADED":
                                            print(f'"{username}" downloaded file "{cmdMsgBroken[2]}" from thread "{cmdMsgBroken[1]}"!')
                                        else: 
                                            print(f'"{username}" failed to downloaded file "{cmdMsgBroken[2]}" from thread "{cmdMsgBroken[1]}"')
                                        continue

                        
                        # while 3's try-excepts
                        except Exception as e:
                            # Upon socket.timeout()
                            if (str(e).rstrip()) == "timed out":
                                print("Client's packet timed out, retrying...")
                                # print(f"Last currCmd value: {currCmd}") # FOR DEBUGGING
                                continue
                            else:
                                print(f"ERROR: {e}")
                                continue
                        # Upon "ctrl + c"
                        except KeyboardInterrupt:
                            killServer(serverSocket)
                
                # while 2's try-excepts
                except Exception as e:
                    # Upon socket.timeout()
                    if (str(e).rstrip()) == "timed out":
                        print("Client's packet timed out, retrying...")
                        # print(f"Last currCmd value: {currCmd}") # FOR DEBUGGING
                        continue
                    else:
                        print(f"ERROR: {e}")
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
