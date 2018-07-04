import pickle
import re
import sys

CACHE_FILE_NAME = 'CategoryCache.data'

def PrintUsageError(errorString):
    print('Error: {}'.format(errorString))
    print('Usage: python Budget.py BankStatement.csv')

def LoadCache(cacheFileName):
    try:
        with open(cacheFileName, 'rb') as cacheFile:
            cache = pickle.load(cacheFile)
            print('Loaded cache from {}: {}'.format(cacheFileName, cache))
            return cache
    except FileNotFoundError:
        print('No cache file found @ {}'.format(cacheFileName))
        return dict()

def SaveCache(cacheFileName, categoryCache):
    with open(cacheFileName, 'wb+') as cacheFile:
        # print results
        print('Saving cache to {}: {}'.format(cacheFileName, categoryCache))
        pickle.dump(categoryCache, cacheFile)

def Main():
    # Verify Args
    if len(sys.argv) < 2:
        PrintUsageError('Not enough args!')
        return

    bankStatementFileName = sys.argv[1]
    if not bankStatementFileName.lower().endswith('.csv'):
        PrintUsageError('File to parse must be csv')
        return

    # load the file containing the old categories and dict that maps recurring descriptions to categories
    categoryCache = LoadCache(CACHE_FILE_NAME)

    # load the csv file from chase
    with open(bankStatementFileName, 'r') as bankStatementFile:
        debitLines = [line for line in bankStatementFile.readlines() if line.lower().startswith('debit')]
        transactionLine = re.compile(r'\w+,\d{2}/\d{2}/\d{4},"(.*)",(-?\d+.\d+)')
        for line in debitLines:
            match = transactionLine.match(line)
            if match is None:
                continue
            assert len(match.groups()) == 2
            description = match.group(1)
            amount = float(match.group(2))
            print('amount: {}'.format(amount))
            print('description: {}'.format(description))
            print()

        # read each line for amount and description
            # if description auto matches, tally it up
            # if it doesn't prompt user to categorize it
    # save the file containing the old categories and dict that maps recurring descriptions to categories
    SaveCache(CACHE_FILE_NAME, categoryCache)

if __name__ == '__main__':
    Main()
