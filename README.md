<div align="center">

# Paxos Bank Simulator!
by: Johnson Ku and Michael Zhang
</div>

## Contents
<ul>
  <li>Installation Prerequisites
  <li>Overview
  <li>Usage
</ul>

## Installation Prerequisites

**Version:** Python 3.7.7 

**Libraries/Frameworks:** sys, socket, time, subprocess, threading, hashlib, os

## Overview

Transferring money between any two accounts is one of the most prominent applications in today’s world. Instead of a mutual exclusion approach, we have built a peer-to-peer money exchange application on top of a private blockchain to create a trusted but fault-tolerant decentralized system such that transactions between 2 clients can be executed without any middle-man.

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
