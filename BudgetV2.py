import csv
import datetime
import enum
import hashlib
import math
import pickle
import pprint
import re
import sys
import tkinter
from tkinter import filedialog

class FileDialog:
    root = None

    def __EnsureInitialized():
        if FileDialog.root is None:
            FileDialog.root = tkinter.Tk()
            FileDialog.root.withdraw()

    def Open():
        FileDialog.__EnsureInitialized()

        fname = tkinter.filedialog.askopenfilename()
        if fname == '':
            fname = None
        return fname

    def AskSaveAs(initial_name):
        FileDialog.__EnsureInitialized()

        fname = tkinter.filedialog.asksaveasfile(initialfile=initial_name)

        if fname == '':
            fname = None
        return fname

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
    def __init__(self, account, transaction_type, description, amount, datetime, balance_hint=0, tags=set()):
        amount_sign = 1
        if amount < 0:
            amount_sign = -1

        self.account = account
        self.transaction_type = transaction_type
        self.description = description
        self.fixed_amount = math.floor(math.abs(amount * 100)) * amount_sign
        self.datetime = datetime
        self.balance_hint = balance_hint
        self.tags = tags

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
    def __init__(self, transactions=dict()):
        self.__transactions = transactions

    def Load(file_name, default_on_missing=False):
        try:
            with open(file_name, 'rb') as file:
                transaction_db = pickle.load(file)
                print('Loaded transaction DB from {}'.format(file_name))
                return transaction_db
        except FileNotFoundError as e:
            if default_on_missing:
                print('Transaction DB file {} does not exist. Starting new empty DB.'.format(file_name))
                return TransactionDb()
            else:
                raise e
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

    def Count(self):
        return len(self.__transactions)

    def NewEntryCount(self, updates):
        count = 0
        for key in updates:
            if key not in self.__transactions:
                count += 1
        return count

    def Update(self, new_entries):
        self.__transactions.update(new_entries)


def PrintUsageError(errorString):
    print('Error: {}'.format(errorString))
    print('Usage: python BudgetV2.py BankStatement.csv TransactionDb.data')

class InteractiveModeState:
    def __init__(self):
        self.loaded_db = None

class InteractiveMode(enum.Enum):
    Quit = 0
    MainMenu = 1
    NewDb = 2
    LoadDb = 3
    SaveDb = 4
    ProcessCsv = 5

def present_prompt(prompt, option_dict):
    while True:
        if prompt is not None:
            print(prompt)
        for k,v in option_dict.items():
            print("[%s] - %s" % (k, v[0]))

        selection = input()
        if selection in option_dict:
            return option_dict[selection][1]
        if selection.lower() in option_dict:
            return option_dict[selection.lower()][1]
        if selection.upper() in option_dict:
            return option_dict[selection.upper()][1]
        else:
            print("Unrecognized input %s" % selection.lower())

def load_db_interactive():
    db_file_name = FileDialog.Open()
    if db_file_name is not None:
        try:
            return (db_file_name, TransactionDb.Load(db_file_name, default_on_missing=True))
        except BaseException as e:
            print("Failed to open db file: %s" % e)
            return None
    else:
        return None

def csv_processor_chase_bank(csv_rows, account_type):
    # TODO:
    raise NotImplementedError

def csv_processor_apple_card(csv_rows, account_type):
    # TODO:
    raise NotImplementedError

def process_csv_interactive():
    class CsvProcessingMode(enum.Enum):
        OpenCsv = 0
        SelectAccountType = 1
        SelectCsvFormat = 2
        ProcessingCsv = 3
        Quit = 4

    mode = CsvProcessingMode.OpenCsv
    csv_rows = None
    account_type = None
    csv_processor = None

    while mode != CsvProcessingMode.Quit:
        match mode:
            case CsvProcessingMode.OpenCsv:
                csv_filename = FileDialog.Open()
                if csv_filename is not None:
                    with open(csv_filename) as csv_file:
                        csvDictReader = csv.DictReader(csv_file)
                        csv_rows = [row for row in csvDictReader]
                    mode = CsvProcessingMode.SelectAccountType
                else:
                    mode = CsvProcessingMode.Quit
            case CsvProcessingMode.SelectAccountType:
                account_type = present_prompt("Select an account type:", {
                    'CHK': ("checking", Account.Checking),
                    'CC': ("credit card", Account.CreditCard),
                    'JCHK': ("joint checking", Account.JointChecking),
                    'B': ("back", None),
                    })
                if account_type is not None:
                    mode = CsvProcessingMode.SelectCsvFormat
                else:
                    mode = CsvProcessingMode.Quit
            case CsvProcessingMode.SelectCsvFormat:
                csv_processor = present_prompt("Select a CSV format:", {
                    'CHS': ("chase bank", csv_processor_chase_bank),
                    'APL': ("apple card", csv_processor_apple_card),
                    'B': ("back", None),
                    })
                if csv_processor is not None:
                    mode = CsvProcessingMode.ProcessingCsv
                else:
                    mode = CsvProcessingMode.SelectAccountType
                pass
            case CsvProcessingMode.ProcessingCsv:
                return csv_processor(csv_rows, account_type)
            case _:
                pass
    return None

def main_interactive():
    mode = InteractiveMode.MainMenu
    state = InteractiveModeState()

    while mode != InteractiveMode.Quit:
        match mode:
            case InteractiveMode.MainMenu:
                print()
                mode = present_prompt(None, {
                    'NDB': ("new db", InteractiveMode.NewDb),
                    'LDB': ("load db", InteractiveMode.LoadDb),
                    'SDB': ("save db", InteractiveMode.SaveDb),
                    'CSV': ("process csv", InteractiveMode.ProcessCsv),
                    'Q': ("quit", InteractiveMode.Quit),
                    })

            case InteractiveMode.NewDb:
                if state.loaded_db is None:
                    print("Loaded new DB.")
                    state.loaded_db = (None, TransactionDb())
                else:
                    # FIXME: support save on new db
                    print("ERROR: already loaded DB")
                mode = InteractiveMode.MainMenu

            case InteractiveMode.LoadDb:
                if state.loaded_db is None:
                    db = load_db_interactive()
                    if db is not None:
                        state.loaded_db = db
                        print("Loaded db. %s (%i entries)" % (
                            state.loaded_db[0],
                            state.loaded_db[1].Count()
                            ))
                else:
                    # FIXME: support save on re-load
                    print("ERROR: already loaded DB")
                mode = InteractiveMode.MainMenu

            case InteractiveMode.SaveDb:
                if state.loaded_db is not None:
                    save_file_name = None
                    if state.loaded_db[0] is not None:
                        save_file_name = state.loaded_db[0]
                    else:
                        save_file = FileDialog.AskSaveAs("budget.db")
                        save_file_name = save_file.name
                        save_file.close()

                    if save_file_name is not None:
                        print("Saving db. %s (%i entries)" % (
                            save_file_name,
                            state.loaded_db[1].Count()
                            ))
                        state.loaded_db[1].Save(save_file_name)
                        state.loaded_db = (save_file_name, state.loaded_db[1])
                else:
                    # FIXME: support save on re-load
                    print("ERROR: DB not loaded")
                mode = InteractiveMode.MainMenu

            case InteractiveMode.ProcessCsv:
                if state.loaded_db is not None:
                    transactions = process_csv_interactive()
                    if transactions is not None:
                        print("Adding %i new transactions" % state.loaded_db[1].NewEntryCount(transactions))
                        state.loaded_db[1].Update(transactions)
                else:
                    print("ERROR: DB not loaded")
                mode = InteractiveMode.MainMenu

            case _:
                pass

def main_cli():
    # verify args
    if len(sys.argv) < 3:
        PrintUsageError('Not enough args!')
        return

    bank_statement_file_name = sys.argv[1]
    if not bank_statement_file_name.lower().endswith('.csv'):
        PrintUsageError('File to parse must be csv')
        return

    db_file_name = sys.argv[2]
    transaction_db = TransactionDb.Load(db_file_name, default_on_missing=True)
    print('Loaded transaction db with %u entries' % transaction_db.Count())

    with open(bank_statement_file_name) as bank_statement_csv:
        csvDictReader = csv.DictReader(bank_statement_csv)
        for row in csvDictReader:
            if row['Type'] == 'ACCT_XFER':
                pprint.pp(row)

    if len(sys.argv) >= 4:
        print('Saving transaction db with %u entries' % transaction_db.Count())
        transaction_db.Save(db_file_name)

def main():
    if "-i" in sys.argv:
        main_interactive()
    else:
        main_cli()

if __name__ == '__main__':
    main()
