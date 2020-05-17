import threading
import queue
import socket
import sys
import time 

# transfer, sender, receiver, dollar_amount
def receive():
    global replies
    global blockchain
    global balance
    global requests
    global clock
    global pid
    global lock
    global s

    while True:
        length = s.recv(2)
        length = int(length.decode())
        msg = s.recv(length)
        msg = msg.decode().split(', ')
        with lock:
            clock = max(clock, int(msg[-1])) + 1
            # request, clock, pid
            if msg[0] == 'request':
                requests.put((int(msg[1]),msg[2]))
                temp_list = []
                # reply, sender_pid, receiver_pid
                clock += 1
                reply = 'reply, ' + pid + ', ' + msg[2] + ', ' + str(clock)
                reply = str(len(reply)) + reply
                # send reply back to requesting process
                s.sendall(reply.encode())
            # reply, sender_pid, receiver_pid
            elif msg[0] == 'reply':
                # Add reply to the set of replies
                replies.add(msg[1])
            # transfer, sender_pid, receiver_pid, amount
            elif msg[0] == 'transfer':
                if msg[2] == pid:
                    balance += int(msg[3])
                blockchain.append((msg[1], msg[2], msg[3]))
                temp = requests.get()



def process():
    global events
    global blockchain
    global requests
    global balance
    global clock
    global pid
    global replies
    global lock
    global s

    while True:
        while events.not_empty:
            # get top of queue
            e = events.get()
            event = e[0]
            # transfer
            if event == 'transfer':
                amount = e[1]
                receiver = e[2]
                with lock:
                    clock += 1
                    # Check if transfer amount is valid
                    if balance < int(amount) or receiver == pid:
                        print('FAILURE')
                        continue
                    clock += 1
                    requests.put((clock, pid))
                    # Send requests to other processes
                    request = 'request, ' +  str(clock) + ', ' + pid + ', ' + str(clock)
                    request = str(len(request)) + request
                    s.sendall(request.encode())
                # Wait until request is at the top of the queue
                # and replies have been received from the other processes
                time.sleep(3)
                while True:
                        if len(replies) == 2:
                        # Check if request is at the top
                            with lock:
                                top = requests.get() 
                                if top[1] == pid:
                                    replies.clear()
                                    # Change own balance
                                    balance -= int(amount)
                                    # Update own blockchain
                                    # Transfer, release, and broadcast message combined together
                                    clock += 2
                                    release = 'transfer, ' + pid + ', ' + receiver + ', ' + amount + ', ' + str(clock)
                                    release = str(len(release)) + release
                                    s.sendall(release.encode())
                                    time.sleep(1)
                                    blockchain.append((pid, receiver, amount))
                                    break
                                requests.put(top)
                            time.sleep(1)
            # print blockchain
            elif event == 'blockchain':
                with lock:
                    print('blockchain: ' + str(blockchain))
            # print balance
            elif event == 'balance':
                with lock:
                    print('balance: ' + str(balance))
                    print('Clock: ' + str(clock))

# python server.py pid
pid = sys.argv[1]

# Establish TCP connection with NW
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.connect(('127.0.0.1', 3000))
s.sendall(pid.encode('utf-8'))

events = queue.Queue()
replies = set()
requests = queue.PriorityQueue()
blockchain = []
balance = 10
clock = 0


lock = threading.Lock()

threading.Thread(target = receive).start()
threading.Thread(target = process).start()

while(True):
    time.sleep(0.01)
    # Possible inputs
    # transfer, amount, receive_pid
    # balance
    # blockchain 
    e = input('Enter command: ')
    e = e.split(', ')
    if e[0] != 'transfer' and e[0] != 'balance' and e[0] != 'blockchain':
        print('Invalid commmand')
        continue
    events.put(e)

