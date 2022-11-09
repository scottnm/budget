import csv
import datetime
import enum
import hashlib
import math
import pickle
import pprint
import re
import sys

class Account(enum.Enum):
    Checking = 0
    CreditCard = 1
    JointChecking = 2

class TransactionType(enum.Enum):
    Debit = 0
    Credit = 1
    Transfer = 2
    Income = 3

class Transaction:
    def __init__(self, account, transaction_type, description, amount, datetime, balance_hint=0):
        amount_sign = 1
        if amount < 0:
            amount_sign = -1

        self.account = account
        self.transaction_type = transaction_type
        self.description = description
        self.fixed_amount = math.floor(math.abs(amount * 100)) * amount_sign
        self.datetime = datetime
        self.balance_hint = balance_hint

        idbytes = "_".join([
            str(self.account),
            str(self.transaction_type),
            self.description,
            str(self.fixed_amount),
            str(self.datetime),
            str(balance_hint)
            ]).encode("utf8")
        self.hash = int(hashlib.sha256(idbytes).hexdigest(), 16)

    def __hash__(self):
        return self.hash

    def __eq__(self, other):
        return self.hash == other.hash

    def __repr__(self):
        return "{}: {} - {}.{} - {}".format(
            self.transaction_type,
            self.description,
            math.floor(self.fixed_amount / 100),
            self.fixed_amount % 100,
            self.datetime)

class TransactionDb:
    def __init__(self, transactions):
        self.transactions = transactions

    def Load(file_name):
        try:
            with open(file_name, 'rb') as file:
                transaction_db = pickle.load(file)
                print('Loaded transaction DB from {}'.format(file_name))
                return transaction_db
        except FileNotFoundError as e:
            print('Transaction DB file {} does not exist. Starting new empty DB.'.format(file_name))
            return TransactionDb(set())
        except BaseException as e:
            print('Could not load transaction DB from {}! {}'.format(file_name, e))
            raise e

    def Save(self, file_name):
        try:
            with open(file_name, 'wb+') as file:
                print('Saving transaction DB to {}'.format(file_name))
                pickle.dump(self, file)
        except BaseException as e:
            print('Could not save transaction DB to {}! {}'.format(file_name, e))

def PrintUsageError(errorString):
    print('Error: {}'.format(errorString))
    print('Usage: python BudgetV2.py BankStatement.csv TransactionDb.data')

def main():
    # verify args
    if len(sys.argv) < 3:
        PrintUsageError('Not enough args!')
        return

    bank_statement_file_name = sys.argv[1]
    if not bank_statement_file_name.lower().endswith('.csv'):
        PrintUsageError('File to parse must be csv')
        return

    db_file_name = sys.argv[2]
    transaction_db = TransactionDb.Load(db_file_name)
    print('Loaded transaction db with {} entries'.format(len(transaction_db.transactions)))

    with open(bank_statement_file_name) as bank_statement_csv:
        csvDictReader = csv.DictReader(bank_statement_csv)
        for row in csvDictReader:
            if row['Type'] == 'ACCT_XFER':
                pprint.pp(row)

    if len(sys.argv) >= 4:
        print('Saving transaction db with {} entries'.format(len(transaction_db.transactions)))
        transaction_db.Save(db_file_name)

if __name__ == '__main__':
    main()
