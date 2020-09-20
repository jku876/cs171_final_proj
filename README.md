# Paxos-Bank-Simulator
by Johnson Ku and Michael Zhang
## Project Description
A program simulating a decentralized bank that handles transactions between clients. The bank utilizes a blockchain to log the transactions 
among the clients and the Paxos consensus protocol to replicate the logs throughout the distributed system.
## Usage
1. After cloning the reposity, start the program by typing `python3 process.py PORT` into terminal where PORT is any of the preset ports 3001-3005.
2. Open up to 5 processes on different terminal windows with the same command but with different port numbers.
3. Type `balance` into terminal to check the client's current balance.
4. Type `blockchain` to view the current log of transactions.
5. Simulate transferring money to another client by typing `Transfer, RECEIVER, AMOUNT` into  terminal where RECEIVER is any of the other clients (p1-p5)
and AMOUNT is less or equal to your current balance.
4. Type `fail link, DEST` to simulate a network failure between two clients where DEST is any of the other clients (p1-p5). Type `fix link, DEST` to fix the 
link between the two clients.
5. Type `fail process` to simulate a process crashing in the distributed system.
6. Type `pending transfers` to view the transfers that have not been processed yet.
