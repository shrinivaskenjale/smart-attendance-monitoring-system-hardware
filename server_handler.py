from datetime import datetime

import requests

from config import BACKEND_BASE_URL

# ==========================================
# FUNCTION TO MARK ATTENDANCE LOCALLY IN CSV
# ==========================================


def markAttendanceInCSV(name, attendancePath):
    with open(attendancePath, 'r+') as f:
        myDataList = f.readlines()
        nameList = []
        for line in myDataList:
            entry = line.split(',')
            nameList.append(entry[0])
        if name not in nameList:
            time_now = datetime.now()
            tStr = time_now.strftime('%H:%M:%S')
            dStr = time_now.strftime('%d/%m/%Y')
            f.write(f'\n{name},{tStr},{dStr}')


# ==========================================
# FUNCTION TO CREATE NEW ATTENDANCE RECORD
# ==========================================

def createNewAttendance(facultyId):
    r = requests.post(BACKEND_BASE_URL+'/system/new-attendance', json={
        'facultyId': facultyId
    })

    if(r.ok):
        data = r.json()
        print(data['facultyName'])
        return data['attendanceId']


# ==========================================
# FUNCTION TO MARK ATTENDANCE IN DATABASE
# ==========================================

def markAttendance(attendanceId, studentId, recognizedPeople):
    r = requests.post(BACKEND_BASE_URL + f'/system/mark-attendance/{attendanceId}', json={
        'studentId': studentId
    })

    if(r.ok):
        data = r.json()
        print(data['userName'])
        recognizedPeople.add(studentId)
        return studentId
