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

def sort_report(report):
    return sorted(
        [(category, categorySum) for category, categorySum in report.items()],
        key=lambda reportListEntry: reportListEntry[1])

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
        transactionLine = re.compile(r'\w+,(\d{2})/\d{2}/(\d{4}),"(.*)\s+.*",(-?\d+.\d+)')
        # read each line for amount and description
        for line in debitLines:
            match = transactionLine.match(line)
            if match is None:
                print('no match! {}'.format(line))
                continue
            assert len(match.groups()) == 4
            description = re.sub(r'\s+', ' ', match.group(3))
            amount = float(match.group(4))
            monthYear = match.group(2) + ' ' + match.group(1)

            # if description auto matches, tally it up
            category = FindCategoryFromCache(categoryCache, description)
            if category is None:
                # if it doesn't prompt user to categorize it
                category = AssignCategory(categoryCache, description)

            if monthYear not in debitReport:
                debitReport[monthYear] = dict()
            if category not in debitReport[monthYear]:
                debitReport[monthYear][category] = 0
            debitReport[monthYear][category] += amount

    # flatten the debit report into a sorted list of reports for each month
    debitReportMonthList = [ (monthYear, sort_report(report)) for monthYear, report in debitReport.items() ]
    debitReportMonthList = sorted(debitReportMonthList, key=lambda entry: entry[0])

    for monthYearReport in debitReportMonthList:
        monthSum = 0
        for debitReportListEntry in monthYearReport[1]:
            monthSum += debitReportListEntry[1]
        print('{}: {}'.format(monthYearReport[0], -monthSum))
        for debitReportListEntry in monthYearReport[1]:
            print('    spent ${:.2f} on {}'.format(-debitReportListEntry[1], debitReportListEntry[0]))

    # save the file containing the old categories and dict that maps recurring descriptions to categories
    SaveCache(CACHE_FILE_NAME, categoryCache)

if __name__ == '__main__':
    Main()
