home = 0
import socket, threading
import select
import sys
from threading import *

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server.bind(('192.168.43.226', 4444))
 
print("Server is Live!")
server.listen(100)
st = 1



def M2M():
    
    All = {'fan': 0, 'lights': 1, 'bedroom': 20, 'hall': 23}
    rooms = {'bedroom': 20, 'hall': 23}
    appliances = {'fan': 0, 'fans': 0, 'lights': 1, 'light': 1}
    Status = ['on', 'off']
    print(All)
        

    def CheckRoom(text, pin):
        print(True)
        for room in rooms:
            if(room in text or room + 's' in text or room + "'s" in text):
                return rooms[room], 1
        return 0, 0

    def CheckAppliance(text, pin):
        for var in appliances:
            if(var in text or var + 's' in text or var + "'s" in text):
                return appliances[var], 1
        return 0, 0
        
        

    def Check(text):
        global st
        text = text.split()
        print(text)
        #ON & OFF
        if('on' in text):
            status, st = 1, 1
        elif('off' in text):
            status, st = 0, 0

        print(st, 'Status')
        
        #DETERMINE ROOM
        pin, checkRoom = CheckRoom(text, 0)
        print("Room", pin, checkRoom, text)
        

        if(not checkRoom):
            print("No Room found. Please try again!")
            Body()

            
        #IDENTIFY APPLIANCE
        temp, checkAppliance = CheckAppliance(text, pin)
        print("APPLIANCE", pin, checkAppliance, text)
        pin += temp

        if(not checkAppliance):
            print("No Room found. Please try again!")
            Body()


        print(status, pin, checkRoom, checkAppliance)
        toSend =  str(status) + "," + str(pin)
        conn.send(toSend.encode())
        Body()


    #2 Tasks in one sentence
    def Check1(text):
        global st
        text = text.split()
        check = 0       #should become 2
        room = ""
        
        #FINDING ROOM and defining the pin
        for _ in rooms:
            if(_ in text or _ + "'s" in text or _ + "s" in text):
                pin = rooms[_]
                room = _
                break
        temp = pin
        
        #FINDING STATUS & APPLIANCE
        _ = 0         
        while(_ < len(text)):
            if(check == 2):
                if(status == "on"):
                    status, st = 1, 1
                else:
                    status, st = 0, 0
                print(st, 'Status')
                #Completion of the sentence
                print(status, pin)
                toSend =  str(status) + "," + str(pin)
                conn.send(toSend.encode())
                check = 0
                try:
                    text = text[_ + 1:]
                    _ = 0
                    pin = temp
    ##                Check(text)
    ##                break
                except:
                    text = ''
                    break
            if(text[_] in Status):
                check += 1
                status = text[_]
            if(text[_] in appliances):
                check += 1
                pin += appliances[text[_]]
            _ += 1
        
        
            
            


    def Text(text):
        print(text, True)
        roomCount = 0
        text.lower()
        if('guest' in text):
            text = text.split()
            if('activate' in text or 'on' in text):
                toSend =  str(1) + ", all" 
                conn.send(toSend.encode())
                Body()
            elif('deactivate' in text or 'off' in text):
                toSend =  str(0) + ", all" 
                conn.send(toSend.encode())
                Body()
                
        else:
            for _ in rooms:
                if(_ in text or _ + "'s" in text or _ + "s" in text):
                    roomCount += 1

            if('and' in text and roomCount == 2):
                    text = text.split('and')
                    Text(text[0])
                    Text(text[1])
            elif('&' in text and roomCount == 2):
                    text = text.split('&')
                    Text(text[0])
                    Text(text[1])
                    
            elif(('and' in text or '&' in text) and roomCount == 1):
                Check1(text)    

            
            elif(roomCount == 1):
                Check(text)
            elif(roomCount == 0):
                print("No rooms found. Please try again!")
                Body()



        
        

    queries = ["turn on bedrooms lights",
               "turn off bedrooms lights",
               "turn off bedrooms fan",
               "turn on bedrooms fan",
                "turn on hall's lights",
                "turn off hall's lights",
                "turn on hall's fan",
                "turn off hall's fan",
                "turn off halls fan",
                "activate guest mode",
               "turn off guest mode",
               ]

        

    def Body():
        i = 0
        for j in (queries):
            print(i, j, True)
            i += 1
            
        n = int(input())
        Text(queries[n])

    Body()


    


#Alert
import time
flag = False
def Alert():
    global st
    import json
    from firebase import firebase
    #firebase = firebase.FirebaseApplication('https://smart-home-automation-project.firebaseio.com/')
    firebase = firebase.FirebaseApplication('https://web-of-things-6ac4d.firebaseio.com/')
    global flag, check
    if(flag):
        if(time.time() - check > 2 and st):
            data = {'alert': 1}
            sent = json.dumps(data)
            result = firebase.post("/alert", sent)
            print('No one found', sent, time.time() )

            result = firebase.get('/', None)
            
            if('Condition' in result and st):
                status = 0
                check = int(result.split(' ')[1])
                
                if(check == 0 and st):
                    print('Got the Response as OFF')
                    conn.send('offall'.encode())
                    st = 0
                elif(check == 1 and st):
                    print('Got the Response as ON')
                    flag = False
            #3 secs delay
            start = time.time()
            while(time.time() - start <= 3):
                pass
                
    else:
        check = time.time()
        flag = True

def PublishSubcriber():
    import cv2
    import numpy as np


    
    body_classifier = cv2.CascadeClassifier('haarcascade_fullbody.xml')

    
    cap = cv2.VideoCapture('test1.mp4')


    while cap.isOpened():   
        ret, frame = cap.read()


        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        bodies = body_classifier.detectMultiScale(gray, 1.2, 3)

        if(len(bodies) == 0 ):
            Alert()
        for (x,y,w,h) in bodies:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 255), 2)
        cv2.imshow('Pedestrians', frame)

        if cv2.waitKey(25) & 0xFF == ord('q'): 
            break

    cap.release()
    cv2.destroyAllWindows()


      
clients = []



def ClientThread(conn, addr):
    if(home):
        M2M()
    else:
        PublishSubcriber()

while(1):
      conn, addr = server.accept()
      print('Connected with ' + addr[0])
      clients.append(conn)
      threading.Thread(target=ClientThread, args=(conn, addr)).start()
      
conn.close()
server.close()

