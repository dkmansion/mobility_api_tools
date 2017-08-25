#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
 Created on Wed Oct 12 17:18:31 2016
 @author: mansiond
 @license:  MIT
"""

def versiontuple(s):
    '''
        @description Helper function to transform string version numbers into a comparable value
        @source kindall at stackoverflow  http://stackoverflow.com/a/11887825/3447669
    '''
    return tuple(map(int, (s.split("."))))


import requests
import time
import logging
import os
import sys

# Variables
scriptName = os.path.basename(sys.argv[0])
# Update logfolder to your preferred location, MUST be existing.  If not please create it.
logfolder = "~/cronjobs/apilogs/"
runTime = time.strftime("%Y-%m-%d-%H-%M-%S")
logFileFullPath = logfolder + scriptName + "_" + runTime + '.log'

#Your app ID numbers WILL be different use
#   126 = Airwatch Agent Ver 5.4.2
#   122 = VoalteOnePlatform 3.3.4


appID = 121  # sys.argv[1]
appVersion = "5.1.3"  # sys.argv[2]
# Your API hostname
apiHost = "your-aw-api.hostname.com"

# aw-tenant-code is obtained from Airwatch  All Settings > System > Advanced > API > REST API
    #   Create a new key or use an existing one.

# authorization is a base64 encode of the username:password for an admin account allowed to use the API.
    #>>> import base64
    #>>> base64.b64encode('username:password')
    #    'dXNlcm5hbWU6cGFzc3dvcmQ='
    #
    # concatenate "Basic " + base64 encoded auth credentials.
    # You can handle this interactively if your security rules do'e allow it to be used this way.
        # Be careful of using the encoding as sys.argv options at the command line since that is unsafe also, and probably more risky.

    # API account
        # Make a dedicated Administrator account with very complex password.
        # Add Role which includes REST API FULL access. "Roles tab"
        # Verify authentication type on the "API tab"

headers = {
    'aw-tenant-code': "your_tenant_code_here",
    'content-type': "application/json",
    'authorization': "Basic your_base64_auth_string_here"
}


# Only These Serial Numbers if supplied in the dictionary below.
serialList = [""]

# Configure Logging
logging.basicConfig(filename=logFileFullPath, level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s',
                    filemode='w')

deviceIDList = []

enrolledResponseURL = "https://" + apiHost + "/api/system/users/enrolleddevices/search"

# OS Platform to specify apps to query
querystring = {"Platform": "Apple"}


# Response containing the enrolled devices in the Airwatch Console.
enrolledResponse = requests.request("GET", enrolledResponseURL, headers=headers, params=querystring)
# print("1\t" + enrolledResponse.text)

# print("2\t" + "ResponseList")
responseList = enrolledResponse.json()
# print("3\t" + str(responseList))
#Log the response list
logging.info(str(responseList))


responseList = responseList['EnrolledDeviceInfoList']

failure = 0
failureList = []
success = 0
successList = []
skipped = 0
skippedList = []
ignored = 0
ignoredList = []
processed = 0
processedList = []
trouble = 0
troubleList = []

deviceGlobal = ""
deviceNumGlobal = ""

try:
    # Loop through list and add device attributes to new list
    for device in responseList:
        try:
            enrolledDeviceList = [device['DeviceID'], device['FriendlyName'], device['SerialNumber']]
            deviceIDList.append(enrolledDeviceList)
            deviceIDList.sort()
        except KeyError:
            failure += 1
            pass

    # print(deviceIDList)

    # Get length of deviceList
    deviceNum = len(deviceIDList)

    deviceNumGlobal = len(deviceIDList)

    for device in deviceIDList:
        deviceGlobal = device

        # Throttle the process to allow api breathing room. 1/4 second per device.
        time.sleep(0.25)

        try:
            processed += 1
            processedList.append(str(device[2]))

            logging.info('{0:05d}'.format(processed) + " - " + str(device))

            # URL to get apps assigned to device
            appResponseURL = "https://" + apiHost +"/api/mdm/devices/" + str(device[0]) + "/apps"

            appResponse = requests.request("GET", appResponseURL, headers=headers)

            appResponseList = appResponse.json()

            # add app list for device to list
            appResponseList = appResponseList['DeviceApps']

            # logging.info('{0:05d}'.format(processed) + " - " + str(appResponseList))

            ##appIDList = []

            # Search app list for target app (appID)
            for app in appResponseList:
                theAppID = str(app["Id"]["Value"])
                try:
                    # Check for match of the airwatch app id number to the target appID.
                    if str(theAppID) == str(appID):
                        # print(str(device))
                        appList = [theAppID]
                        logging.info('{0:05d}'.format(processed) + " - " + str(theAppID) + " " +
                                     app["ApplicationName"] + " " + app["Version"])

                        # If version is null log as a trouble device.
                        if str(app["Version"]) == "":
                            trouble += 1
                            troubleList.append(str(device[2]))
                            # Log as a problem
                            logging.warning('{0:05d}'.format(processed) + " - " + str(theAppID) +
                                            " " + app["ApplicationName"] + " " + app["Version"] +
                                            " This device has an app problem.")
                        else:
                            # enter processing here

                            # Check version number against target version (appVersion) less than target send device the install command.
                            if versiontuple(str(app["Version"])) < versiontuple(str(appVersion)):
                                # update d
                                payload = '{\"SerialNumber\":\"' + str(device[2]) + '\"}'

                                installAppURL = "https://"+ apiHost +"/api/mam/apps/purchased/" + str(theAppID) + "/install"
                                installResponse = requests.request("POST", installAppURL, data=payload, headers=headers)

                                # print("update app " + str(appID) + "/" + str(theAppID))
                                # Log the processing of the device install
                                logging.info('{0:05d}'.format(processed) + " / " + '{0:05d}'.format(
                                    deviceNum) + "\t" + "update app " + str(appID) + "/" + str(theAppID))
                                logging.info('{0:05d}'.format(processed) + " / " + '{0:05d}'.format(deviceNum) + "\tPayload = " + payload)

                                # if Response from install comamnd contains information log as a failure.
                                # Future error handling based on http response codes should be used.
                                if len(installResponse.text):
                                    failure += 1
                                    logging.error('{0:05d}'.format(processed) + " / " + '{0:05d}'.format(deviceNum) + "\t" + installResponse.text)
                                    failureList.append(str(device[2]))
                                else:
                                    success += 1
                                    successList.append(str(device[2]))
                                    logging.info('{0:05d}'.format(processed) + " / " + '{0:05d}'.format(deviceNum) + "\t" + "Install action accepted.")

                            # If version equal or greater then target version, skip and log as skipped, due to "Current Version".
                            else:
                                skipped += 1
                                skippedList.append(str(device[2]))
                                logging.info(
                                    '{0:05d}'.format(processed) + " / " + '{0:05d}'.format(deviceNum) + "\t" + str(
                                        app[0]) + " ----- " + str(app["Version"]) + "\tCorrect Version")
                            # Done with iteration so Break
                        break
                    else:
                        ignored += 1
                        ignoredList.append(str(device[2]))
                        logging.info('{0:05d}'.format(processed) + " / " + '{0:05d}'.format(deviceNum) + "\t" + str(
                            app[0]) + " ----- " + str(app["Version"]) + "\tCorrect Version")

                    # Break to next device
                    break

                except KeyError:
                    # Ignore KeyErrors for now.
                    pass
                    ##logging.info(appIDList)
        except KeyError:
            # Log KeyError as a Failure
            failure += 1
            failureList.append(str(device[2]))
            # Ignore KeyErrors for now.
            pass

except KeyError:
    # Log KeyError as a Failure
    failure += 1
    failureList.append(str(deviceGlobal[2]))
    # Ignore KeyErrors for now.
    pass

finally:
    # Compile the result counts and list of serial numbers for the log
    results = "\n\t" + "{\n\t\t\"Failures\": " + str(failure) + "\n\t\t" + \
              "\"Failure List\": " + str(failureList) + "\n\t\t\t" + \
              ", \"Ignored\": " + str(ignored) + "\n\t\t" + \
              "\"Ignore List\": " + str(ignoredList) + "\n\t\t\t" + \
              ", \"Skipped\": " + str(skipped) + "\n\t\t" + \
              "\"Skipped List\": " + str(skippedList) + "\n\t\t\t" + \
              ", \"Processed\": " + str(processed) + "\n\t\t" + \
              "\"Processed List\": " + str(processedList) + "\n\t\t\t" + \
              ", \"Successful\": " + str(success) + "\n\t\t" + \
              "\"Successful List\": " + str(successList) + "\n\t\t\t" + \
              ", \"Trouble\": " + str(trouble) + "\n\t\t" + \
              "\"Trouble List\": " + str(troubleList) + "\n\t\t\t" + \
              ", \"Devices\": " + str(deviceNumGlobal) + "\n\t" + "}"

logging.info("Results:\t" + results)

##### Finish logging items.
