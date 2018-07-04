import pickle
import re
import sys

CACHE_FILE_NAME = 'CategoryCache.data'

class CategoryCacheEntry:
    def __init__(self, descriptionMatch, category):
        self.descriptionMatch = descriptionMatch
        self.category = category

def PrintUsageError(errorString):
    print('Error: {}'.format(errorString))
    print('Usage: python Budget.py BankStatement.csv')

def LoadCache(cacheFileName):
    try:
        with open(cacheFileName, 'rb') as cacheFile:
            cache = pickle.load(cacheFile)
            print('Loaded cache from {}'.format(cacheFileName))
            return cache
    except FileNotFoundError:
        print('No cache file found @ {}'.format(cacheFileName))
        return list()

def SaveCache(cacheFileName, categoryCache):
    with open(cacheFileName, 'wb+') as cacheFile:
        # print results
        print('Saving cache to {}'.format(cacheFileName))
        pickle.dump(categoryCache, cacheFile)

def FindCategoryFromCache(categoryCache, description):
    for cacheEntry in categoryCache:
        if cacheEntry.descriptionMatch.lower() in description.lower():
            return cacheEntry.category
    return None

def AssignCategory(categoryCache, description):
    category = input('Enter category for "{}":'.format(description))
    categoryCache.append(CategoryCacheEntry(description, category))
    return category

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

    debitReport = dict()

    # load the csv file from chase
    with open(bankStatementFileName, 'r') as bankStatementFile:
        debitLines = [line for line in bankStatementFile.readlines() if line.lower().startswith('debit')]
        transactionLine = re.compile(r'\w+,\d{2}/\d{2}/\d{4},"(.*)\s+\d{2}/\d{2}",(-?\d+.\d+)')
        # read each line for amount and description
        for line in debitLines:
            match = transactionLine.match(line)
            if match is None:
                continue
            assert len(match.groups()) == 2
            description = re.sub(r'\s+', ' ', match.group(1))
            amount = float(match.group(2))
            print('amount: {}'.format(amount))
            print('description: {}'.format(description))
            print()

            # if description auto matches, tally it up
            category = FindCategoryFromCache(categoryCache, description)
            if category is None:
                # if it doesn't prompt user to categorize it
                category = AssignCategory(categoryCache, description)

            if category not in debitReport:
                debitReport[category] = 0
            debitReport[category] += amount

    # flatten the debit report map into a sorted list
    debitReportList = sorted(
        [(category, categoryDebitSum) for category, categoryDebitSum in debitReport.items()],
        key=lambda debitReportListEntry: debitReportListEntry[1])

    for debitReportListEntry in debitReportList:
        print('You spent ${:.2f} on {}'.format(-1 * debitReportListEntry[1], debitReportListEntry[0]))

    # save the file containing the old categories and dict that maps recurring descriptions to categories
    SaveCache(CACHE_FILE_NAME, categoryCache)

if __name__ == '__main__':
    Main()
