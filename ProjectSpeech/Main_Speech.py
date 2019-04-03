home = 1
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

if(home):
    All = {'fan': 0, 'lights': 1, 'bedroom': 20, 'hall': 14}
    rooms = {'bedroom': 20, 'hall': 23}
    appliances = {'fan': 0, 'fans': 0, 'lights': 1, 'light': 1}
    Status = ['on', 'off']
    print(All)

def M2M():
    def SpeechRecognition():
        import speech_recognition as sr 
        #enter the name of usb microphone that you found 
        #using lsusb 
        #the following name is only used as an example 
        mic_name = "Microsoft Sound Mapper - Input"
        #Sample rate is how often values are recorded 
        sample_rate = 48000
        #Chunk is like a buffer. It stores 2048 samples (bytes of data) 
        #here. 
        #it is advisable to use powers of 2 such as 1024 or 2048 
        chunk_size = 2048
        #Initialize the recognizer 
        r = sr.Recognizer() 

        #generate a list of all audio cards/microphones 
        mic_list = sr.Microphone.list_microphone_names() 

        #the following loop aims to set the device ID of the mic that 
        #we specifically want to use to avoid ambiguity.
        i = 0
        for  microphone_name in (mic_list):
            if (microphone_name == mic_name):        
                device_id = i
            i += 1

        #use the microphone as source for input. Here, we also specify 
        #which device ID to specifically look for incase the microphone 
        #is not working, an error will pop up saying "device_id undefined" 
        with sr.Microphone(device_index = device_id, sample_rate = sample_rate, 
                                                        chunk_size = chunk_size) as source: 
                #wait for a second to let the recognizer adjust the 
                #energy threshold based on the surrounding noise level 
                r.adjust_for_ambient_noise(source) 
                print("Say Something")
                #listens for the user's input 
                audio = r.listen(source) 
                        
                try: 
                        text = r.recognize_google(audio)
                        Body(text)
                        
                
                #error occurs when google could not understand what was said 
                
                except sr.UnknownValueError: 
                        print("Google Speech Recognition could not understand audio")
                        SpeechRecognition()
                
                except sr.RequestError as e: 
                        print("Could not request results from Google Speech Recognition service; {0}".format(e))
                        SpeechRecognition()


        

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
        text = text.split()
        print(text)
        #ON & OFF
        if('on' in text):
            status = 1
        elif('off' in text):
            status = 0

        
        #DETERMINE ROOM
        pin, checkRoom = CheckRoom(text, 0)
        print("Room", pin, checkRoom, text)
        

        if(not checkRoom):
            print("No Room found. Please try again!")
            SpeechRecognition()

            
        #IDENTIFY APPLIANCE
        temp, checkAppliance = CheckAppliance(text, pin)
        print("APPLIANCE", pin, checkAppliance, text)
        pin += temp

        if(not checkAppliance):
            print("No Room found. Please try again!")
            SpeechRecognition()


        print(status, pin, checkRoom, checkAppliance)
        toSend =  str(status) + "," + str(pin)
        conn.send(toSend.encode())
        SpeechRecognition()


    #2 Tasks in one sentence
    def Check1(text):
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
                    status = 1
                else:
                    status = 0

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
        print(text)
        roomCount = 0
        text.lower()
        if('guest' in text):
            text = text.split()
            if('activate' in text or 'on' in text):
                toSend =  str(1) + ", all" 
                conn.send(toSend.encode())
                SpeechRecognition()
            elif('deactivate' in text or 'off' in text):
                toSend =  str(0) + ", all" 
                conn.send(toSend.encode())
                SpeechRecognition()
                
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
                SpeechRecognition()



        
        

    queries = ["turn on bedrooms lights",
               "turn off bedrooms lights",
               "turn off bedrooms fan",
               "turn on bedrooms fan",
                "turn on hall's lights",
                "turn off hall's lights",
                "turn on hall's fan",
                "turn off hall's fan",
                "turn off halls fan",
                "turn off the light of bedroom and turn on the lights of hall",
                "turn off the lights and turn on the fan of hall",
               ]




    i = 0
    for j in (queries):
        print(i, j)
        i += 1
        
    ##
    ###while(1):
    ##def SpeechRecognition():
    ##    i = 0
    ##    for j in (queries):
    ##        print(i, j)
    ##        i += 1
    ##        
    ##    n = int(input())
    ##
    ##    Text(queries[n])



    ##VOICE INPUT

    def Body(text):
        Text(text)


    SpeechRecognition()

    


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

    
    cap = cv2.VideoCapture('test.mp4')


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

