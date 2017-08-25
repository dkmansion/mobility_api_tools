#!/usr/bin/python #macOS
##/bin/env/ python # for use with linux

'''
    @author         dkmansion
    @revision       1.0 2017-08-24
    @description    Script to obtain current iTunes details for a list of apps,
                    provided through their bundleID in the bundleList disctionary
                    variable
    @license        MIT
    @warranty       None
    @support        None
    @API reference  https://affiliate.itunes.apple.com/resources/documentation/itunes-store-web-service-search-api/
'''

def versiontuple(s):
    '''
        @description Helper function to transform string version numbers into a comparable value
        @source kindall at stackoverflow  http://stackoverflow.com/a/11887825/3447669
    '''
    return tuple(map(int, (s.split("."))))

def searchappstore():

    import requests
    import sys

    # ** bundleList is the ONLY ITEM THAT MUST BE CUSTOMIZED for this script to be useful to you.
    # Modify this dictionary list with the bundle IDs for the apps you wish to get info for with this script.
    bundleList = ["com.invalid.bundleid", "com.epic.rover", "com.epic.roverprerelease",
                  "com.epic.canto", "com.epic.cantoprerelease",
                  "com.another.bad.bundleid","com.epic.haiku", "com.epic.haikuprerelease",
                  "com.air-watch.agent", "com.citrix.ReceiveriPad"]

    RED = "\033[1;31m"
    # BLUE = "\033[1;34m"
    # CYAN = "\033[1;36m"
    # GREEN = "\033[0;32m"
    RESET = "\033[0;0m"
    # BOLD = "\033[;1m"
    # REVERSE = "\033[;7m"
    SEPARATOR = "\n- - - - - - - - - - - - - -\n"

    errorsFound = 0
    errorList = []
    url = "https://itunes.apple.com/lookup"

    # Loop through list and get the details
    for bundleid in bundleList:
        querystring = {"bundleId": "" + bundleid + ""}

        # print str(querystring)

        response = requests.request("GET", url, params=querystring).json()

        appResults = response["results"]

        #Check if results are empty
        if len(appResults):
            # print (str(appResults))

            # Extra for loop so you don't have to know the indices of the values below.
            #   For ease of modification adding or removing values.
            for app in appResults:
                print (
                       "App Name: " + app["trackName"] + "\n"
                       + "\t\t" + "BundleId:\t" + app["bundleId"] + "\n"
                       + "\t\t" + "Version:\t" + app["version"] + "\n"
                       + "\t\t" + "Released:\t" + app["currentVersionReleaseDate"] + "\n"
                       )
        else:
            errorsFound += 1
            # BundleID is bad
            #change test to red
            sys.stdout.write(RED)
            errorList.append(bundleid)

            print (str("\nInvalid Bundle ID: " + bundleid + "\n"))
            #reset color to standard output
            sys.stdout.write(RESET)

    if errorsFound <> 0:
        sys.stdout.write(RED)

        print (str(SEPARATOR + "Errors found with BundleIDs"
                   + "\n\t\t" + str(errorList) + SEPARATOR))
        # reset color to standard output
        sys.stdout.write(RESET)


if __name__ == '__main__':
    searchappstore()
