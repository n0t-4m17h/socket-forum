# Python Version: 3.8.10
# Program written by z5361183
# 10/04/22
# Run; $ python3 client.py serverPort
from socket import *
import sys
from datetime import datetime
import time

def XIT(clientSocket, serverPort):
    clientSocket.sendto("Curr socket has exited".encode("utf-8"), ('localhost', int(serverPort)))
    clientSocket.close()
    sys.exit("Goodbye")
    

# let the OS pick a random Client Port -> "sock.bind(('localhost', 0))", selected port is in "sock.getsockname()"

if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit('Execute program as such: $python3 client.py <server_port>')

    serverPort = int(sys.argv[1])
    WAIT_TIME_NRML = 5 # wait time for non-image commands
    WAIT_TIME_IMG = 15 # wait time for image transfers

    clientSocket = socket(AF_INET, SOCK_DGRAM) # sock_dgram == UDP socket
    # Set the timeout time if packet is taking too long/lost
    # clientSocket.settimeout(WAIT_TIME)

    while 1:
        # try:
            # simplify datetime to just HH:MM:SS, 24hr time
            timestamp = str(datetime.today())[11:19]

            command = str(input("Enter username: "))
            if command == "XIT":
                XIT(clientSocket, serverPort)

            # ".encode("utf-8")" turns the message into a "bytes-like object", from a str. ".decode("utf-8") does the opposite
            clientSocket.sendto(command.encode("utf-8"), ('localhost', int(serverPort)))
            t1 = time.time()

            # Waiting for Server Response --> This is where program pauses (w/out exception) if packet is lost
            # pingEchoCommand, serverAddress = clientSocket.recvfrom(2048)
            t2 = time.time()

        # LEGACY: except socket.timeout: # not working, baseclass issue
        # except:
        #     # Assume the packet was lost (cause UDP), hence "timed out"
        #     print("Packet timeout: resending timed-out packet")
        #     continue
    
    # print(f"Min RTT: {min_rtt}\nMax RTT: {max_rtt}\nAvg RTT: {avg_rtt}")

    clientSocket.close()