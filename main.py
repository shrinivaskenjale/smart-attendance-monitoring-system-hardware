# ==========================================
# IMPORTS
# ==========================================

import cv2
import numpy as np
import face_recognition
import os
import shutil


from server_handler import createNewAttendance, markAttendance
from images_handler import fetchImages, faceEncodings, downloadImages
from camera_handler import showLabel


# ==========================================
# DRIVER CODE
# ==========================================
if(__name__ == "__main__"):

    currentFacultyId = None
    currentAttendanceId = None
    recognizedPeople = set()

    imagesPath = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), 'images')
    # attendancePath = os.path.join(os.path.dirname(
    #     os.path.abspath(__file__)), 'attendance.csv')

    if(os.path.isdir(imagesPath)):
        shutil.rmtree(imagesPath)

    os.mkdir(imagesPath)

    downloadImages(imagesPath)

    images, personIds, userTypes = fetchImages(imagesPath)

    # Encoding all stored images
    encodeListKnown = faceEncodings(images)
    print('Starting face recognition...')

    # starting camera to capture video stream
    # 0 = internal camera
    # 1 = external camera
    cam = cv2.VideoCapture(0)

    while True:
        # read a video frame by frame
        # read() returns tuple in which 1st item is boolean value
        # either True or False and 2nd item is frame of the video.
        # read() returns False when video is ended so
        # no frame is readed and error will be generated.
        ret, frame = cam.read()

        waitingDelay = 1

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
                showLabel(frame, faceLoc, id)

                # markAttendanceInCSV(id, attendancePath)

                # stop the attendance
                if(currentFacultyId == id and len(recognizedPeople) > 0):

                    currentAttendanceId = None
                    currentFacultyId = None
                    recognizedPeople = set()
                    print('Attendance Stopped')
                    waitingDelay = 30000

                # create new attendance
                elif(userType == 'faculty' and currentAttendanceId is None):

                    currentAttendanceId = createNewAttendance(id)
                    if(currentAttendanceId):
                        currentFacultyId = id
                        waitingDelay = 30000

                # verify and mark attendance of student
                elif(userType == 'student' and currentAttendanceId and (id not in recognizedPeople)):

                    currentPersonId = markAttendance(
                        currentAttendanceId, id, recognizedPeople)
                    if(currentPersonId):
                        waitingDelay = 5000

        # display current frame
        cv2.imshow('Smart Attendance Monitoring System', frame)
        if (cv2.waitKey(waitingDelay) == 13):
            break

        # show updated present count
        print(len(recognizedPeople))

    # release all resources
    cam.release()
    cv2.destroyAllWindows()
