import queue
import random
import socket
import sys
import threading
import time
from hashlib import sha256



# PID of the process
PID = sys.argv[1]

# IP address of the process
IP = '127.0.0.1'

# Dictionary containing all ports of all processes
# Used for UDP connection
PORTS = {
    "p1": 3001, 
    "p2": 3002, 
    "p3": 3003, 
    "p4": 3004, 
    "p5": 3005
}

# Dictionary containing the state of each connection
# Address: Connection state (bool)
CONN_STATE = {
    (IP, 3001): True,
    (IP, 3002): True,
    (IP, 3003): True,
    (IP, 3004): True,
    (IP, 3005): True
}

# For testing purposes
addr_to_PID = {
    (IP, 3001): 'p1',
    (IP, 3002): 'p2',
    (IP, 3003): 'p3',
    (IP, 3004): 'p4',
    (IP, 3005): 'p5'
}

# Amount of money in the bank
balance = 100

# List of blocks
# block - list [txns, nonce, hash]
# txns - list of tuples (sender, receiver, amount) converted to a string
blockchain = []

# List of transactions to be added to pending
# transactions - tuple (sender, receiver, amount)
# Used to ensure that transfers added during paxos are not lost
transfers = []

# List of transactions to be added to the blockchain 
# transactions - tuple (sender, receiver, amount)
pending = []

# List of promises from other processes
# promise - list [promise, BallotNum, ID, AcceptNum, ID, AcceptVal]
promised = []

# Number of accepted messages from other processes
accepted = 0

# Ballot that the process gives its promise to
# format - (BallotNum, PID)
ballotNum = (0, PID)

# Ballot number associated with acceptVal
# format - (BallotNum, PID)
acceptNum = (0, '')

# Proposed block converted into string
# format - txns||nonce||hash
acceptVal = ''

# Queue that holds all events of the process
# Possible events: ['transfer', 'balance', 'blockchain', 'fail link', 'fix']
events = queue.Queue()

# Create socket
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((IP, PORTS[PID]))

# Lock to ensure mutual exclusion
lock = threading.Lock()

### TODO: READ SNAPSHOT IF NECESSARY ###
# Initial started up pass 'default' as the file
# Take 2nd param as reboot file
# Update all variables

# Send a message using UDP
# msg (str) - message to be sent
# addr (str, int) - tuple (IP, port) for UDP destination
def message(msg,addr):
    # Fixed delay for each message
    time.sleep(2)
    # Check if connection is valid
    if CONN_STATE[addr]:
        s.sendto(msg.encode(),addr)

# Thread for receiving all messages
def comm():
    global accepted
    global acceptNum
    global acceptVal
    global balance
    global ballotNum
    global blockchain
    global events
    global promised

    while True:
        msg, addr = s.recvfrom(1024)
        msg = msg.decode().split('|')

        # Message type, one of the following:
        # prepare, promise, accept, accepted, decide
        type = msg[0]

        with lock:
            # Pretend message was never received if connection is broken
            if CONN_STATE[addr] == False:
                continue
            # prepare|BallotNum|ID 
            if type == 'prepare':
                b = (int(msg[1]),msg[2])
                # TESTING: Print receive 
                print('Received PREPARE for ballot ' + str(b))
                # Check if the received ballot is larger than the promised ballot
                # If so, update ballotNum, send 'promise' back to sender
                if b >= ballotNum:
                    ballotNum = b
                    response = ('promise|' + str(ballotNum[0]) + '|' + ballotNum[1] + '|' +
                               str(acceptNum[0]) + '|' + acceptNum[1] + '|' + str(acceptVal) )
                    threading.Thread(target = message, args = (response, addr)).start()
                    # TESTING: Print sending response
                    print('Sending PROMISE for ballot ' + str(b))
            # promise|BallotNum|ID|AcceptNum|ID|AcceptVal
            elif type == 'promise' and msg[1] == ballotNum[0] and msg[2] == ballotNum[1]:
                # Add promise into list of promises
                promised.append(msg)
                # TESTING: Print received promise
                print('Received PROMISE for ballot ' + str(ballotNum))
            # accept|BallotNum|ID|Value
            elif type == 'accept':
                b = (int(msg[1]),msg[2])
                # TESTING: Print receive 
                print('Received ACCEPT for ballot ' + str(b))
                # Check if the received ballot is larger than the promised ballot
                # If so, update acceptNum and acceptVal, send 'accepted' back to sender
                if b >= ballotNum:
                    acceptNum = b
                    acceptVal = msg[3]
                    response = 'accepted|' + str(acceptNum[0]) + '|' + acceptNum[1] + '|' + str(acceptVal)
                    threading.Thread(target = message, args = (response, addr)).start()
                    # TESTING: Print sending response
                    print('Sending ACCEPTED for ballot ' + str(b))
            # accepted|BallotNum|ID|Value
            elif type == 'accepted':
                # Increment number of 'accepted' messages by 1
                accepted += 1
                # TESTING: Print received accepted
                print('Received ACCEPTED for ballot ' + str(ballotNum))
            # decide|acceptVal
            elif type == 'decide':
                # TESTING: Print received decision
                print('Received DECIDE from ' + addr_to_PID[addr] + ' , adding block to blockchain')
                # Update local blockchain
                acceptVal = msg[1]
                blockchain.append(acceptVal.split('||'))
                # Update balance
                update = acceptVal.split('||')[0].strip('][').split(', ')
                for u in update:
                    transaction = u.strip(')(').split(', ')
                    if transaction[0] == PID:
                        balance -= int(transaction[2])
                    if transaction[1] == PID:
                        balance += int(transaction[2])
                # Reset all paxos variables for the new round of paxos
                promised = []
                accepted = 0
                ballotNum = (0, PID)
                acceptNum = (0, '')
                acceptVal = ''

# Thread for processesing events given by the command line             
def process():
    global CONN_STATE
    global events
    global transfers

    while True:
        e = events.get()
        type = event[0]
        with lock:
            if type == 'balance':
                print(balance)
            elif type == 'blockchain':
                print(blockchain)
            # fail link, DEST
            elif type == 'fail link':
                CONN_STATE[(IP, PORTS[e[1]])] = False
            # fail link, DEST
            elif type == 'fix':
                CONN_STATE[(IP, PORTS[e[1]])] = True
            # transfer, receiver, amount
            elif type == 'transfer':
                temp = balance
                for t in transfers:
                    temp -= int(t[1])
                # Make sure there is sufficient money for the transfer
                if temp <= e[2]:
                    print('Insufficient balance for: ' + str(e))
                    print('Transfer FAILED')
                    continue
                # Append transfer to list of transfers
                transfers.append((PID,e[1],e[2]))
            elif type == 'fail process':
                ### TODO: SNAPSHOT ###
                continue

# Thread to run paxos
def paxos():
    global accepted
    global acceptNum
    global acceptVal
    global balance
    global ballotNum
    global blockchain
    global events
    global promised
    global transfers
    global PID
    global pending
    while True:
        if len(transfers) == 0 and len(pending) == 0:
            continue
        time.sleep(10)
        # Add all transactions in transfer to pending
        # Ensures that transfers added by user while paxos is running are not lost
        with lock:
            for t in transfers:
                pending.append(t)
            transfers = []
        # Flag to determine if own value is being promoted
        promote = True
        # PHASE I: LEADER ELECTION
        while True:
            time.sleep(random.randint(0,5))
            with lock:
                promised = []
                accepted = 0
                ballotNum[0] = ballotNum[0] + 1
                ballotNum[1] = PID
                # prepare|BallotNum|ID 
                prepare = 'prepare|' + ballotNum[0] + '|' + ballotNum[1]
                # send prepare messages to all processes
                for conn in PORTS:
                    if conn != PID:
                        addr = (IP, PORTS[conn])
                        threading.Thread(target = message, args = (prepare, addr)).start()
            # Wait for 'promise' reponses
            # Acts as a psuedo timeout
            time.sleep(4.5)
            with lock:
                # If not enough promises, start from PHASE I again
                if len(promised) < 2:
                    continue
            with lock:
                # If all acceptVal from promises are empty, set own acceptVal
                if all(p[-1] == '' for p in promised):
                    # Find appropriate nonce
                    # h = sha256(txns||nonce) must end with a number from 0-4
                    while True:
                        nonce = str(random.randint(100))
                        h = sha256((str(pending) + "||" + nonce).encode('utf-8')).hexdigest()
                        if '0' <= h[-1] <= '4':
                            # TESTING: Print nonce and hash value
                            print('Nonce: ' + nonce)
                            print('Hash value: ' + h)
                            break
                    # Edge case for first block
                    if len(blockchain) == 0:
                        acceptVal = str(pending) + '||' + nonce + '|| '
                    # General case for all other blocks
                    else:
                        # Hash of the previous block
                        prevHash = sha256(str(blockchain[-1]).encode('utf-8')).hexdigest()
                        acceptVal = str(pending) + '||' + nonce + '||' + prevHash
                # If acceptVal are not all empty, promote the acceptVal with the highest ballotNum
                # Set promote flag to false
                else:
                    promised.sort(reverse = True)
                    acceptVal = promised[0][-1]
                    promote = False
        # PHASE II: CONSENSUS
        with lock:
            # accept|BallotNum|ID|Value
            accept = 'accept|' + ballotNum[0] + '|' + ballotNum[1] + '|' + acceptVal
            # Send 'accept' messages to all processes
            for conn in PORTS:
                if conn != PID:
                    addr = (IP, PORTS[conn])
                    threading.Thread(target = message, args = (accept, addr)).start()
        # Wait for 'promise' reponses
        # Acts as a psuedo timeout
        time.sleep(4.5)
        with lock:
            # If the process does not receive the majority of 'accepted', restart from PHASE I
            if accepted < 2:
                continue
        # PHASE III: Decide
        with lock:
            # Send 'decide' message to all processes
            decide = 'decide|' + acceptVal
            for conn in PORTS:
                if conn != PID:
                    addr = (IP, PORTS[conn])
                    threading.Thread(target = message, args = (decide, addr)).start()
            # Remove all successful transactions from pending
            if promote:
                pending = []
            # Add block to blockchain
            blockchain.append(acceptVal.split('||'))
            # Update balance
            update = acceptVal.split('||')[0].strip('][').split(', ')
            for u in update:
                transaction = u.strip(')(').split(', ')
                if transaction[0] == PID:
                    balance -= int(transaction[2])
                if transaction[1] == PID:
                    balance += int(transaction[2])
            # Reset all paxos variables for the new round of paxos
            promised = []
            accepted = 0
            ballotNum = (0, PID)
            acceptNum = (0, '')
            acceptVal = ''            

# Start threads
threading.Thread(target = process).start()
threading.Thread(target = comm).start()
threading.Thread(target = paxos).start()

# Continuously take input from command line
while True:
    event = input('Enter Command: ')
    event = event.split(', ')
    # Place event in queue if valid
    if event[0] in ['transfer', 'balance', 'blockchain', 'fail link', 'fix']:
        events.put(event)
    else:
        print('Invalid Command')