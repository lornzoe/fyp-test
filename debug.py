# this is purely just to make sure my webcam was working, lmao

import cv2
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
print("Testing camera...")
while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break
    cv2.imshow('Test', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cap.release()
cv2.destroyAllWindows() 