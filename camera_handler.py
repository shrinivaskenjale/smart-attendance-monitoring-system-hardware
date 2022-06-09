import cv2

# ==========================================
# FUNCTION TO DISPLAY LABEL ON IDENTIFIED FACE
# ==========================================


def showLabel(frame, faceLocation, label):
    # get co-ordinates of face inside resized frame
    y1, x2, y2, x1 = faceLocation

    # get co-ordinates of face inside original frame
    y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4

    # draw rectangle around face
    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
    # draw rectangle below face for text
    cv2.rectangle(frame, (x1, y2 - 35), (x2, y2),
                  (0, 255, 0), cv2.FILLED)
    # put text below face
    cv2.putText(frame, label, (x1 + 6, y2 - 6),
                cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
