import queue
import random
import socket
import sys
import threading
import time

PID = sys.argv[1]
IP = '127.0.0.1'

PORTS = {
    "p1": 3001, 
    "p2": 3002, 
    "p3": 3003, 
    "p4": 3004, 
    "p5": 3005
}

CONN_STATE = {
    (IP, 3001): True,
    (IP, 3002): True,
    (IP, 3003): True,
    (IP, 3004): True,
    (IP, 3005): True
}

balance = 100
blockchain = []
transfers = []

promised = []
accepted = 0

ballotNum = (0, PID)
acceptNum = (0, 0)
acceptVal = ''

events = queue.Queue()

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((IP, PORTS[PID]))

lock = threading.Lock()
threading.Thread(target = proccess).start()
threading.Thread(target = comm).start()
threading.Thread(target = paxos).start()

### TODO: READ SNAPSHOT IF NECESSARY ###
# Initial started up pass 'default' as the file
# Take 2nd param as reboot file
# Update all variables

while True:
    event = input()
    event = event.split(', ')

    if event[0] in ['transfer', 'balance', 'blockchain', 'fail link', 'fix']:
        events.put(event)
def message(msg,addr):
    time.sleep(2)
    if CONN_STATE[addr]:
        s.sendto(msg.encode(),addr)

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
        msg, addr = sock.recvfrom(1024)
        msg = msg.decode().split('|')

        type = msg[0]
        with lock:
            if CONN_STATE[addr] == False:
                continue
            # prepare|BallotNum|ID 
            if type == 'prepare':
                b = (int(msg[1]),msg[2])
                if b >= ballotNum:
                    ballotNum = b
                    response = 'promise|' + str(ballotNum[0]) + '|' + ballotNum[1] + '|' + 
                               str(acceptNum[0]) + '|' + acceptNum[1] + '|' + str(acceptVal)
                    threading.Thread(target = message, args = (response, addr)).start()
            # promise|BallotNum|ID|AcceptNum|ID|AcceptVal
            elif type == 'promise' and msg[1] == ballotNum[0] and msg[2] == ballotNum[1]:
                promised.append(msg)
            # accept|BallotNum|ID|Value
            elif type == 'accept':
                b = (int(msg[1]),msg[2])
                if b >= ballotNum:
                    acceptNum = b
                    acceptVal = msg[3]
                    response = 'accepted|' + str(acceptNum[0]) + '|' + acceptNum[1] + '|' + str(acceptVal)
                    threading.Thread(target = message, args = (response, addr)).start()
            # accepted|BallotNum|ID|Value
            elif type == 'accepted':
                accepted += 1
            # decide|... # TODO
            elif type == 'decide':
                ### TODO: BLOCKCHAIN ###
                
                
def process():
    global CONN_STATE
    global events
    global transfers

    while True:
        e = events.get()
        type = event[0]
        with lock:
            if type = 'balance':
                print(balance)
            elif type = 'blockchain':
                print(blockchain)
            # fail link, DEST
            elif type = 'fail link':
                CONN_STATE[(IP, PORTS[e[1]])] = False
            # fail link, DEST
            elif type = 'fix':
                CONN_STATE[(IP, PORTS[e[1]])] = True
            # transfer, receiver, amount
            elif type = 'transfer':
                temp = balance
                for t in transfers:
                    temp -= int(t[1])
                if temp <= e[2]:
                    print('Insufficient balance for: ' + str(e))
                    print('Transfer FAILED')
                    continue
                transfers.append((e[1],e[2]))
            elif type = 'fail process':
                ### TODO: SNAPSHOT ###

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

    # NEED TO PUT BACK ALL TRANSFERS IF PROCESS PROMOTES OTHER VALUE
    while True:
        if len(transfers) == 0:
            continue
        promote = True
        while True:
            time.sleep(random.randint(2,7))
            with lock:
                promised = []
                accepted = 0
                ballotNum[0] = ballotNum[0] + 1
                ballotNum[1] = PID
                # prepare|BallotNum|ID 
                prepare = 'prepare|' + ballotNum[0] + '|' + ballotNum[1]
                for conn in PORTS:
                    if conn != PID:
                        addr = (IP, PORTS[conn])
                        threading.Thread(target = message, args = (prepare, addr)).start()
            time.sleep(4.5)
            with lock:
                if len(promised) >= 2:
                    continue
            with lock:
                if all(p[-1] == '' for p in promised):
                    acceptVal = block ### TODO: TEMP PLACEHOLDER ###
                else:
                    promised.sort(reverse = True)
                    acceptVal = promised[0][-1]
                    promote = False
        with lock:
            # accept|BallotNum|ID|Value
            accept = 'accept|' + ballotNum[0] + '|' + ballotNum[1] + acceptVal
            for conn in PORTS:
                if conn != PID:
                    addr = (IP, PORTS[conn])
                    threading.Thread(target = message, args = (accept, addr)).start()
        time.sleep(4.5)
        with lock:
            if accepted < 2:
                continue
        with lock:
            decide = 'decide|...' ### TODO: TEMP PLACEHOLDER ###
            for conn in PORTS:
                if conn != PID:
                    addr = (IP, PORTS[conn])
                    threading.Thread(target = message, args = (decide, addr)).start()
            if promote:
                transfers = []
        