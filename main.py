# ==========================================
# IMPORTS
# ==========================================

import cv2
import numpy as np
import face_recognition
import os
import shutil
import Adafruit_CharLCD as LCD
import RPi.GPIO as GPIO


from server_handler import createNewAttendance, markAttendance
from images_handler import fetchImages, faceEncodings, downloadImages
from camera_handler import showLabel


# ==========================================
# DRIVER CODE
# ==========================================
if(__name__ == "__main__"):

    GPIO.setmode(GPIO.BCM)

    lcd1 = 12
    lcd2 = 7
    lcd3 = 8
    lcd4 = 25
    lcd5 = 24
    lcd6 = 23

    lcd = LCD.Adafruit_CharLCD(lcd1, lcd2, lcd3, lcd4, lcd5, lcd6, 0, 16, 2)

    currentFacultyId = None
    currentFacultyName = None
    currentAttendanceId = None
    recognizedPeople = set()

    imagesPath = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), 'images')
    # attendancePath = os.path.join(os.path.dirname(
    #     os.path.abspath(__file__)), 'attendance.csv')

    if(os.path.isdir(imagesPath)):
        shutil.rmtree(imagesPath)

    os.mkdir(imagesPath)

    # Downloading images
    lcd.clear()
    lcd.message('DOWNLOADING\nIMAGES...')
    downloadImages(imagesPath)

    images, personIds, userTypes = fetchImages(imagesPath)

    # Encoding all stored images
    lcd.clear()
    lcd.message('GENERATING FACE\nENCODINGS...')
    encodeListKnown = faceEncodings(images)

    # print('Starting face recognition...')
    lcd.clear()
    lcd.message('     READY!\n----------------')

    
    

    while True:
        
        # starting camera to capture video stream
        # 0 = internal camera
        # 1 = external camera
        cam = cv2.VideoCapture(0)
        
        # read a video frame by frame
        # read() returns tuple in which 1st item is boolean value
        # either True or False and 2nd item is frame of the video.
        # read() returns False when video is ended so
        # no frame is readed and error will be generated.
        ret, frame = cam.read()
        
        # release camera
        cam.release()

        waitingDelay = 1
        lcdUpdate=False

        # resizing captured frame
        resizedFrame = cv2.resize(frame, (0, 0), None, 0.25, 0.25)

        # converting frame from BGR to RGB
        resizedFrame = cv2.cvtColor(resizedFrame, cv2.COLOR_BGR2RGB)

        # find locations of all faces in current frame
        frameFaceLocations = face_recognition.face_locations(resizedFrame)

        # finding encodings of all faces in the frame
        frameFaceEncodings = face_recognition.face_encodings(
            resizedFrame, frameFaceLocations)

        # iterating over all encodings of all faces in the frame
        for faceEncod, faceLoc in zip(frameFaceEncodings, frameFaceLocations):

            # comparing current face with known faces
            matches = face_recognition.compare_faces(
                encodeListKnown, faceEncod)

            # finding euclidean distance between current face and known faces
            faceDist = face_recognition.face_distance(
                encodeListKnown, faceEncod)

            # get index of minimum distance value
            matchIndex = np.argmin(faceDist)

            # if minimum distance face matches with current face in the frame
            if(matches[matchIndex] == True):

                # get id and status of the person
                id = personIds[matchIndex]
                userType = userTypes[matchIndex]

                # give label on the face
                # showLabel(frame, faceLoc, id)

                # markAttendanceInCSV(id, attendancePath)

                # stop the attendance
                if(currentFacultyId == id and len(recognizedPeople) > 0):
                    # print('Attendance Stopped')
                    lcd.clear()
                    lcd.message(f'THANK YOU\nCOUNT : {len(recognizedPeople)}')
                    waitingDelay = 10000
                    lcdUpdate=True
                    currentAttendanceId = None
                    currentFacultyId = None
                    currentFacultyName=None
                    recognizedPeople = set()

                # create new attendance
                elif(userType == 'faculty' and currentAttendanceId is None):

                    currentAttendanceId, facultyName = createNewAttendance(id)
                    if(currentAttendanceId):
                        firstName, lastName = facultyName.split()
                        lcd.clear()
                        lcd.message(f'{firstName}\n{lastName}'.upper())
                        currentFacultyId = id
                        currentFacultyName = f'{firstName[0]} {lastName}'.upper()
                        waitingDelay = 10000
                        lcdUpdate=True

                # verify and mark attendance of student
                elif(userType == 'student' and currentAttendanceId and (id not in recognizedPeople)):

                    currentPersonId, studentName = markAttendance(
                        currentAttendanceId, id, recognizedPeople)
                    if(currentPersonId):
                        firstName, lastName = studentName.split()
                        lcd.clear()
                        lcd.message(f'{firstName}\n{lastName}'.upper())
                        waitingDelay = 3000
                        lcdUpdate=True

        # display current frame
        #cv2.imshow('Smart Attendance Monitoring System', frame)
        if (cv2.waitKey(waitingDelay) == 13):
            break

        # show updated present count
        if(lcdUpdate):
            if(currentFacultyId is not None):
                # print(len(recognizedPeople))
                lcd.clear()
                lcd.message(
                    f'{currentFacultyName}\nCOUNT : {len(recognizedPeople)}')
            else:
                lcd.clear()
                lcd.message('     READY!\n----------------')

    # release all resources
    cv2.destroyAllWindows()
