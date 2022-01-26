import http.client
import sys
from datetime import datetime
import json
import time
import smtplib

wallet_id = sys.argv[1]
to_addr = sys.argv[2]
login = sys.argv[3]
passwd = sys.argv[4]
host = "smtp.mail.ru"
txcount_start = 0
conn = http.client.HTTPSConnection("btcbook.nownodes.io")
api_key='dFQ6xLeysYv9zUa4ntSfmNobqcXVJMKW'

class Transaction(object):
    def __init__(self, acc, txid, time, v, vin, fees, conf, balance, ubalance):
        self.acc = acc
        self.txid = txid
        self.time = time
        self.v = v
        self.vin = vin
        self.fees = fees
        self.conf = conf
        self.balance = balance
        self.ubalance = ubalance

    def to_string(self):
        return f'Account: {self.acc}\nTransaction ID: {self.txid}\nTime : {self.time}\nValue: {self.v}\nValueIn: {self.vin}\nFees: {self.fees}\nConfirmations: {self.conf}\nCurrent balance: {self.balance}\nUnconfirmed balance: {self.ubalance}'

def to_btc(satoshi):
    return satoshi/100000000

def fill_txcount_start():
    payload = ''
    headers = {
    'api-key': api_key
    }
    conn.request("GET", "/api/v2/address/"+wallet_id, payload, headers)
    res = conn.getresponse()
    data = res.read()

    #print(data)

    jsonresult = json.loads(data);
    txids = jsonresult['txids']
    global txcount_start
    txcount_start = len(txids)

def load_list():
    payload = ''
    headers = {
    'api-key': api_key
    }
    conn.request("GET", "/api/v2/address/"+wallet_id, payload, headers)
    res = conn.getresponse()
    data = res.read()
    jsonresult = json.loads(data);
    txids = jsonresult['txids']

    txids = txids[:-(txcount_start-5)]

    txids.reverse()

    ans = []
    for tx in txids:
        conn.request("GET", "/api/v2/tx/"+tx, payload, headers)
        res = conn.getresponse()
        data = res.read()
        txjson = json.loads(data);

        txid = tx
        time = datetime.utcfromtimestamp(int(txjson['blockTime']))
        v = to_btc(int(txjson['value']))
        vin = to_btc(int(txjson['valueIn']))
        fees = to_btc(int(txjson['fees']))
        conf = int(txjson['confirmations'])
        balance = to_btc(int(jsonresult['balance']))
        ubalance = to_btc(int(jsonresult['unconfirmedBalance']))
        ans.append(Transaction(wallet_id, txid, time, v, vin, fees, conf, balance, ubalance))
    return ans

def is_equal(t1, t2):
    if (t1.conf==t2.conf):
        return True
    else:
        return False

def announce(obj):
    print(obj.to_string()+'\n')
    BODY = "\r\n".join((
        "From: %s" % login,
        "To: %s" % to_addr,
        "Subject: %s" % "Balance change" ,
        "",
        "Balance has been changed!\n%s" % obj.to_string()
    ))
    server = smtplib.SMTP_SSL(host, 465)
    #server.connect(host)
    server.login(login, passwd)
    server.sendmail(login, to_addr, BODY)

def announce_tx_new_info(obj):
    print('Change in Transaction. Check confirmations\n'+obj.to_string()+"\n");
    BODY = "\r\n".join((
        "From: %s" % login,
        "To: %s" % to_addr,
        "Subject: %s" % "Transaction info" ,
        "",
        "Transaction information has been updated. Looks like it has a new confirmation!\n%s" % obj.to_string()
        ))
    server = smtplib.SMTP_SSL(host, 465)
    #server.connect(host)
    server.login(login, passwd)
    server.sendmail(login, to_addr, BODY)
    server.quit()


def cmp_txs(oldlist, newlist):
    for i in range (0, len(oldlist)):
        if (not is_equal(oldlist[i], newlist[i])):
                announce_tx_new_info(newlist[i])

def main():
    print(f'Start monitoring of {wallet_id}\n')
    fill_txcount_start()
    all_transactions = load_list()
    #all_transactions.pop() #раскомментируйте и программа покажет последнюю транзакцию
    while True:
        new_transactions = load_list()
        for i in range(len(all_transactions), len(new_transactions)):
            announce(new_transactions[i])
            cmp_txs(all_transactions, new_transactions)
            all_transactions=new_transactions
        time.sleep(5)

if __name__=="__main__":
    main()
