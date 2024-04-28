#!/usr/bin/env python
# -*- coding: utf-8 -*-



import hashlib
from pyfingerprint.pyfingerprint import PyFingerprint
from pyfingerprint.pyfingerprint import FINGERPRINT_CHARBUFFER1
import requests

backendURL = "http://localhost:4000"


## Search for a finger
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


get_todays = input("Do you want to display todays exams? (Y/N) ")
if get_todays.lower() != "n":
    response = requests.get(f"{backendURL}/exam/today", verify=False).json() 
    print("---------------------------------------------------")
    for i, exam in enumerate(response.get("exam_list", [])):
        print(f"\n{i+1}: Exam: {exam['name']} | Class: {exam['class']['name']}")
    print("\n---------------------------------------------------")


exam = input("Enter exam name: ")

## Tries to search the finger and calculate hash
try:
    print('Place your finger on the sensor.')

    ## Wait that finger is read
    while ( f.readImage() == False ):
        pass

    ## Converts read image to characteristics and stores it in charbuffer 1
    f.convertImage(FINGERPRINT_CHARBUFFER1)

    ## Searchs template
    result = f.searchTemplate()

    positionNumber = result[0]
    accuracyScore = result[1]

    if ( positionNumber == -1 ):
        print('No match found!')
        exit(0)
    else:
        print('Found template at position #' + str(positionNumber))
        print('The accuracy score is: ' + str(accuracyScore))
        print("\n")


    ## Loads the found template to charbuffer 1
    f.loadTemplate(positionNumber, FINGERPRINT_CHARBUFFER1)

    response = requests.post(f"{backendURL}/exam/fingerprint/{exam}/{positionNumber}").json()
    if response.get("error", False):
        print("ERROR: ")
        print(response["error"])
        exit(1)
    
    print(response["success"])
    print(f"Name: {response['student']['name']}")
    print(f"Roll Number: {response['student']['rollno']}")
    print(f"Time: {response['student']['time']}")


except Exception as e:
    print('Operation failed!')
    print('Exception message: ' + str(e))
    exit(1)
