#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
from pyfingerprint.pyfingerprint import PyFingerprint
from pyfingerprint.pyfingerprint import FINGERPRINT_CHARBUFFER1
from pyfingerprint.pyfingerprint import FINGERPRINT_CHARBUFFER2
import requests

backendURL = "http://localhost:4000"

def saveFingerprintToDatabase(fingerprintID, studentID):
    print("\nSaving fingerprint to database....")
    response = requests.post(f"{backendURL}/student/{studentID}", data={"fingerprint_id": fingerprintID}, verify=False).json()
    if response.get("error", False):
        print("ERROR: ")
        print(response["error"])
        return
    print(response.get("success"))


## Enrolls new finger
##

## Tries to initialize the sensor
try:
    f = PyFingerprint('COM3', 57600, 0xFFFFFFFF, 0x00000000)

    if ( f.verifyPassword() == False ):
        raise ValueError('The given fingerprint sensor password is wrong!')

except Exception as e:
    print('The fingerprint sensor could not be initialized!')
    print('Exception message: ' + str(e))
    exit(1)

## Gets some sensor information
print('Currently used templates: ' + str(f.getTemplateCount()) +'/'+ str(f.getStorageCapacity()))



rollNumber = input("\nEnter your roll number: ")

response = requests.get(f"{backendURL}/student/rollno/{rollNumber}", verify=False).json() 

if (response.get("error", False)):
    print("ERROR: ")
    print(response["error"])
    exit(1)

studentID = response["id"]

print("\n\n------- STUDENT INFORMATION -------\n")
print("Name: " + response["name"])
print("Class: " + response["class"])
print("Semester: " + response["semester"])
print("\n")


input("Click enter to continue.")

## Tries to enroll new finger
try:
    print('Place your finger on the sensor.')

    ## Wait that finger is read
    while ( f.readImage() == False ):
        pass

    ## Converts read image to characteristics and stores it in charbuffer 1
    f.convertImage(FINGERPRINT_CHARBUFFER1)

    ## Checks if finger is already enrolled
    result = f.searchTemplate()
    positionNumber = result[0]

    if ( positionNumber >= 0 ):
        print('Template already exists at position #' + str(positionNumber))
        saveFingerprintToDatabase(positionNumber, studentID)
        exit(0)

    print('Remove finger...')
    time.sleep(2)

    print('Waiting for same finger again...')

    ## Wait that finger is read again
    while ( f.readImage() == False ):
        pass

    ## Converts read image to characteristics and stores it in charbuffer 2
    f.convertImage(FINGERPRINT_CHARBUFFER2)

    ## Compares the charbuffers
    if ( f.compareCharacteristics() == 0 ):
        raise Exception('Fingers do not match')

    ## Creates a template
    f.createTemplate()

    ## Saves template at new position number
    positionNumber = f.storeTemplate()
    print('Finger enrolled successfully!')
    print('New template position #' + str(positionNumber))
    saveFingerprintToDatabase(positionNumber, studentID)

except Exception as e:
    print('Operation failed!')
    print('Exception message: ' + str(e))
    exit(1)



