import pickle
import re
import sys
import enum
import math
import datetime
import hashlib

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
    def __init__(self, account, transaction_type, description, amount, datetime):
        self.account = account
        self.transaction_type = transaction_type
        self.description = description
        self.fixed_amount = math.floor(amount * 100)
        self.datetime = datetime

        idbytes = "_".join([
            str(self.account),
            str(self.transaction_type),
            self.description,
            str(self.fixed_amount),
            str(self.datetime)
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
    # FIXME:
    # for t in transaction_db.transactions:
    #     print('    {} - {}'.format(t, hash(t)))

    # FIXME: stub transaction log
    if len(sys.argv) >= 4:
        print('Writing stub entries')
        for i in range(0, 36500):
            typ = None
            desc = None
            amt = None
            dat = datetime.datetime(2022,10,30)+datetime.timedelta(days=i)
            if i % 4 == 0:
                typ = TransactionType.Debit
                desc = "test debit {}".format(i)
                amt = 10.15
            elif i % 4 == 1:
                typ = TransactionType.Credit
                desc = "test credit {}".format(i)
                amt = 11.15
            elif i % 4 == 2:
                typ = TransactionType.Transfer
                desc = "test xfer {}".format(i)
                amt = 21.15
            else:
                typ = TransactionType.Income
                desc = "test inc {}".format(i)
                amt = 31.15

            transaction_db.transactions.add(Transaction(Account.Checking, typ, desc, amt, dat))

        print('Saving transaction db with {} entries'.format(len(transaction_db.transactions)))
        transaction_db.Save(db_file_name)

if __name__ == '__main__':
    main()
