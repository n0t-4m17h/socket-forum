# Python Version: 3.8.10
# Program written by z5361183
# 10/04/22
# Run; $ python3 client.py serverPort
from socket import *
import sys
from datetime import datetime
import time

### List of Commands possible ###
listOfCmds = ["CRT", "MSG", "DLT", "EDT", "LST", "RDT", "UPD", "DWN", "RMV", "XIT"]

def XIT(clientSocket, serverPort, username):
    clientSocket.sendto(f"XIT {username}".encode("utf-8"), ('localhost', int(serverPort)))
    clientSocket.close()
    sys.exit(f"Godspeed, {username}")

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
    # ELSE, its one or two inputs (e.g "XIT" or "DLT 3331")
    return brokenInput

# CMD 1: Server needs to create the thread with the given threadtitle
def CRT(user, threadtitle):
    pass


# let the OS pick a random Client Port -> "sock.bind(('localhost', 0))", selected port is in "sock.getsockname()"
##################
#### MAIN Fnc ####
##################
if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit('Execute program as such: $python3 client.py <server_port>')

    serverPort = int(sys.argv[1])
    WAIT_TIME_NRML = 5 # wait time for non-image commands
    WAIT_TIME_IMG = 15 # wait time for image transfers

    clientSocket = socket(AF_INET, SOCK_DGRAM) # sock_dgram == UDP socket
    # Set the timeout time if packet is taking too long/lost
    # clientSocket.settimeout(WAIT_TIME)

    while 1: # while loop 1 for logging onto server
        goToWhile2 = False
        username = str(input("Enter username: "))
        # if username == "XIT": # only needed for debugging
        #     XIT(clientSocket, serverPort)
        # Send Username to Server
        clientSocket.sendto(username.encode("utf-8"), ('localhost', serverPort))
        # Wait for Server to respond with either "INVALID/VALID USERNAME"
        response, serverAddress = clientSocket.recvfrom(2048)
        respStr = (response.decode("utf-8")).strip()
        # IF username doesn't exist, then prompt it again (i.e restart loop)
        if respStr == "INVALID USERNAME":
            print("Invalid username")
            continue
        # IF Server decides its gonna create this new user, then send Server a password from user
        elif respStr == "NEW USERS PASSWORD":
            password = str(input("Enter new password: "))
            clientSocket.sendto(password.encode("utf-8"), ('localhost', serverPort))
            # response = str(clientSocket.recvfrom(2048)[0], "utf-8")
            goToWhile2 = True
        # IF given Username matches Server's files, then send Server the matching password
        elif respStr == "VALID USERNAME":
            password = str(input("Enter password: "))
            clientSocket.sendto(password.encode("utf-8"), ('localhost', serverPort))
            response = str(clientSocket.recvfrom(2048)[0], "utf-8")
            if response == "INVALID PASSWORD":
                print("Invalid password")
                continue
            else: # if resp = "VALID PASSWORD"
                goToWhile2 = True

        # upon successful authentication, we can now enter forums
        if goToWhile2 is True:
            print("====================\nWelcome to the forum\n====================")
            while 1:
                cmdInput = str(input("Enter one of the following commands: CRT, MSG, DLT, EDT, LST, RDT, UPD, DWN, RMV, XIT: "))
                # break down cmdInput into a list of args 
                cmdList = breakCmdInput(cmdInput) # cmdList[0] is the cmd, [1] is 2nd, and [3] is final arg
                if (cmdList[0] in listOfCmds) is False:
                    print("Invalid command")
                    continue
                elif cmdList[0] == "CRT":
                    # Include CRT-specific error checking !!
                    # CRT(cmdList[1])
                    pass
                elif cmdList[0] == "MSG":
                    pass
                elif cmdList[0] == "DLT":
                    pass
                elif cmdList[0] == "EDT":
                    pass
                elif cmdList[0] == "LST":
                    pass
                elif cmdList[0] == "RDT":
                    pass
                elif cmdList[0] == "UPD":
                    pass
                elif cmdList[0] == "DWN":
                    pass
                elif cmdList[0] == "RMV":
                    pass
                elif cmdList[0] == "XIT":
                    if len(cmdList) != 1:
                        print("Invalid syntax for XIT")
                    else:
                        XIT(clientSocket, serverPort, username)

    clientSocket.close()
