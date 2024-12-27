from flask import Flask, jsonify, render_template, Response
import cv2
import cvzone
from cvzone.FaceMeshModule import FaceMeshDetector
from threading import Thread
import time

app = Flask(__name__)


video = cv2.VideoCapture(0)
detector = FaceMeshDetector(maxFaces=1)

blinkCounter = 0
counter = 0
color = (0, 0, 255)
ratioList = []
last_check_time = time.time()  
notification_sent = False  


idList = [22, 23, 24, 26, 110, 157, 158, 159, 160, 161, 130, 243]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_blink_count')
def get_blink_count():
    global last_check_time, blinkCounter, notification_sent

    
    current_time = time.time()
    elapsed_time = current_time - last_check_time
    reminder = False  

    if elapsed_time >= 60:
        
        if blinkCounter < 10 and not notification_sent: 
            reminder = True  
            notification_sent = True  
        
       
        blinkCounter = 0
        last_check_time = current_time  
        notification_sent = False  # Allow notification for the next minute

    return jsonify({'blink_count': blinkCounter, 'reminder': reminder})

def detect_blink():
    global blinkCounter, counter, color, ratioList
    success, img = video.read()

    if not success:
        return

    img, faces = detector.findFaceMesh(img, draw=False)
    if faces:
        face = faces[0]
        for id in idList:
            cv2.circle(img, face[id], 3, color, cv2.FILLED)

        leftUp = face[159]
        leftDown = face[23]
        leftLeft = face[130]
        leftRight = face[243]

        lengthVer, _ = detector.findDistance(leftUp, leftDown)
        lengthHor, _ = detector.findDistance(leftLeft, leftRight)
        ratio = int((lengthVer / lengthHor) * 100)
        ratioList.append(ratio)

        if len(ratioList) > 5:
            ratioList.pop(0)
        ratioAvg = sum(ratioList) / len(ratioList)

        if ratioAvg < 25 and counter == 0:
            blinkCounter += 1
            color = (0, 200, 0)
            counter = 1

        if counter != 0:
            counter += 1
            if counter > 10:
                counter = 0
                color = (0, 0, 255)

# Stream webcam feed to the client
def generate_frame():
    while True:
        success, frame = video.read()
        if not success:
            break
        
        # Apply face mesh detection for blink count
        detect_blink()

        # Convert frame to JPEG format to send over HTTP
        ret, jpeg = cv2.imencode('.jpg', frame)
        if ret:
            # Yield image as byte data to send as a stream
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frame(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    def video_thread():
        while True:
            detect_blink()

    Thread(target=video_thread, daemon=True).start()

    app.run(debug=True, use_reloader=False)
