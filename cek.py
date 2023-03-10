import cv2
import numpy as np
from flask import Flask, render_template, Response, request
import os, sys
import datetime, time
from threading import Thread
import winsound

global capture,rec_frame, grey, switch, neg, face, rec, out 
capture=0
grey=0
neg=0
face=0
switch=1
rec=0
rec_frame = None

app = Flask(__name__)

try:
    os.mkdir('./shots')
except OSError as error:
    pass

hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

#camera = cv2.VideoCapture('vid1.mp4')
camera = cv2.VideoCapture(0)

def record(out):
    global rec_frame
    while(rec):
        time.sleep(0.05)
        out.write(rec_frame)

def detect_people(frame):
    while True:
        ret, frame = camera.read()
        if not ret:
            break
        
        frame = cv2.resize(frame, (640, 480))
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

def gen_frames():
    global out, capture, rec_frame
    while True:
        success, frame = camera.read()
        if success:
            if(grey):
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            if(neg):
                frame = cv2.bitwise_not(frame)
            if(capture):
                capture = 0
                now = datetime.datetime.now()
                p = os.path.sep.join(['shots', "shot_{}.png".format(str(now).replace(":",''))])
                cv2.imwrite(p, frame)
            if(rec):
                rec_frame=frame
                frame= cv2.putText(cv2.flip(frame, 1), "recording",(0,25), cv2.FONT_HERSHEY_COMPLEX, 1, (0,0,255),4)
                frame= cv2.flip(frame,1)
            else:
                detect_people = frame
                boxes, weights = hog.detectMultiScale(frame, winStride=(8, 8))
                boxes = np.array([[x, y, x + w, y + h] for (x, y, w, h) in boxes])

                for (xA, yA, xB, yB) in boxes:
                    cv2.rectangle(frame, (xA, yA), (xB, yB), (0, 255, 0), 2)
                    cv2.putText(frame, 'WTF', (xA, yA-2), cv2.FONT_HERSHEY_COMPLEX, 0.9, (0, 255, 0), 2)

                now = datetime.datetime.now()
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cv2.putText(frame, timestamp, (10, 30), cv2.FONT_HERSHEY_COMPLEX, 0.6, (0, 255, 0), 2)
                
            try:                
                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                        b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            
            except Exception as e:
                pass

        else:
            pass
        time.sleep(0.01)

@app.route('/')
def cek():
    return render_template('cek.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/requests',methods=['POST','GET'])
def tasks():
    global switch,camera
    if request.method == 'POST':
        if request.form.get('click') == 'Capture':
            global capture
            capture=1
        elif  request.form.get('grey') == 'Grey':
            global grey
            grey=not grey
        elif  request.form.get('neg') == 'Negative':
            global neg
            neg=not neg   
        elif  request.form.get('stop') == 'Stop/Start':
            
            if(switch==1):
                switch=0
                camera.release()
                cv2.destroyAllWindows()
                
            else:
                camera = cv2.VideoCapture(0)
                switch=1
        elif  request.form.get('rec') == 'Start/Stop Recording':
            global rec, out
            rec= not rec
            if(rec):
                now=datetime.datetime.now() 
                fourcc = cv2.VideoWriter_fourcc(*'XVID')
                out = cv2.VideoWriter('vid_{}.avi'.format(str(now).replace(":",'')), fourcc, 20.0, (640, 480))#wtf play back speed  fourcc, 10.0 
                thread = Thread(target = record, args=[out,])
                thread.start()
            elif(rec==False):
                out.release()
                 
    elif request.method=='GET':
        return render_template('cek.html')
    return render_template('cek.html')

if __name__ == '__main__':
    app.run(debug=True)