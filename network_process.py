import socket
import time
import threading
import sys


def connection(c, pid):
    global network
    global lock
    while True:
        length = c.recv(2)
        try: 
            int(length.decode())
        except ValueError:
            continue
        cmd = c.recv(int(length.decode()))
        msg = cmd.decode().split(', ')
        time.sleep(1)
        if msg[0] == 'request':
            for process in network:
                if pid != process:
                    network[process].sendall(length+cmd)
        elif msg[0] == 'reply':
            network[msg[2]].sendall(length+cmd)
        elif msg[0] == 'transfer':
            for process in network:
                if pid != process:
                    network[process].sendall(length+cmd)



s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('127.0.0.1', 3000))
s.listen()
network = {}
lock = threading.Lock()

while True:
        c, addr = s.accept()
        pid = c.recv(1024)
        pid = pid.decode('utf-8')
        network[pid] = c
        # print(connections)
        threading.Thread(target = connection, args=[c, pid]).start()



# proc = {
#     'p1': 3001,
#     'p2': 3002,
#     'p3': 3003
# }

# while True:
#     cmd, addr = s.recvfrom(1024)
#     cmd = cmd.decode('utf-8')
#     temp = cmd.split(',')
#     time.sleep(random.randint(1,6))
#     #s, name, receiver, clock, pid
#     s.sendto(cmd.encode('utf-8'), ('127.1', proc[temp[2]]))