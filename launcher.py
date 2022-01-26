import os
import sys
from subprocess import Popen

receiver_mail = sys.argv[1]
send_mail = sys.argv[2] #sender mail
send_password = sys.argv[3] #sender password

def main():
    print('Start program')
    f = open('wallets.txt', 'r');
    for line in f:
        Popen(["python", "main.py", line[:-1], receiver_mail, send_mail, send_password])
    f.close();

if __name__=="__main__":
    main()
