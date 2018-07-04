import pickle

CACHE_FILE_NAME = 'CategoryCache.data'

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
        print('Saving cache to {}: {}'.format(cacheFileName, categoryCache))
        pickle.dump(categoryCache, cacheFile)

def Main():
    # load the file containing the old categories and dict that maps recurring descriptions to categories
    categoryCache = LoadCache(CACHE_FILE_NAME)
    # load the csv file from chase
    # read each line for amount and description
        # if description auto matches, tally it up
        # if it doesn't prompt user to categorize it
    # print results
    # save the file containing the old categories and dict that maps recurring descriptions to categories
    SaveCache(CACHE_FILE_NAME, categoryCache)

if __name__ == '__main__':
    Main()
