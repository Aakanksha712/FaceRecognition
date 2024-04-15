

######Face recognition###########



from firebase import firebase
import face_recognition
import pandas as pd
import json
import numpy as np
import os
from datetime import datetime
import filestack
from filestack import Client
firebase = firebase.FirebaseApplication("https://coal-automation-system-default-rtdb.firebaseio.com/",None)

import cv2
import json



face_encodings = []
names = []

print("\n**************************FACE RECOGNITION SYSTEM****************************\n")

def record_face():
    name = input("Please enter the name of the person whose identity is to be recorded:\n")
    print("Inside face recording")
    video_capture = cv2.VideoCapture(0)
    names.append(name)
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    count = 0
    while(True):
        ret, frame = cap.read()
        frame = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(frame)
        face_encoding = face_recognition.face_encodings(frame, face_locations)[0]
        face_encodings.append(face_encoding)
        count = count + 1    
        # Display the resulting frame
        cv2.imshow('face recording', frame)
        cv2.waitKey(1000)
    
        if count == 1:
            break
  
    # After the loop release the cap object
    cap.release()
    # Destroy all the windows
    face_encoded = pd.Series(face_encodings).to_json(orient='values')
    
    cv2.destroyAllWindows()
    data = {
        "encoding" : face_encoded,
        "name":name
    }
    firebase.post("https://coal-automation-system-default-rtdb.firebaseio.com/Output/",data)
    return face_encodings



def recognize_face():
    
    print("Inside face recognition")
     # set path in which you want to save images
    path = r'E:\BEIT_SEM_1\BE_Project\number_plate_detection\filestack_folder'

    # changing directory to given path
    os.chdir(path)
    data_face = firebase.get("https://coal-automation-system-default-rtdb.firebaseio.com/Output",'')
       
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    count = 0
    while(True):
        ret, frame = cap.read()
        frame = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)

        face_locations = face_recognition.face_locations(frame)
        face_encoding = face_recognition.face_encodings(frame, face_locations)[0]
        unknown_encoding = face_encoding
        #print(face_encodings)
        count = count + 1    
        # Display the resulting frame
        cv2.imshow('face recognition', frame)
        cv2.waitKey(1000)

        if count == 1:
            break
  
    # After the loop release the cap object
    cap.release()
    # Destroy all the windows
    cv2.destroyAllWindows()

    flag = True
    for key in data_face:
        face = data_face[key]['encoding']
        face = face.replace('[','')
        face = face.replace(']','')
        face= face.split(',')
        facearr = []
        for i in face:
           i = float(i)
           facearr.append(i)
        facearr = np.array(facearr)
    
        match = face_recognition.compare_faces([facearr],unknown_encoding,tolerance=0.4)
        if(match[0] == True):
             # Put current DateTime on each frame
            font = cv2.FONT_HERSHEY_PLAIN
            cv2.putText(frame, str(datetime.now()), (20, 40),
            font, 2, (255, 255, 255), 2, cv2.LINE_AA)

            #Store frame in a folder
            date_str = str(datetime.now())
            filename = 'Frame_'+'1'+'.jpg'
		
		    # Save the images in given path
            cv2.imwrite(filename, frame)

            #Saving frame to filestack 
            client = Client('APt8284UIQ0eYA426LCr1z')
            img_path = 'E:\\BEIT_SEM_1\\BE_Project\\number_plate_detection\\filestack_folder\\' + filename
            filelink = client.upload(filepath=img_path)
            URL = filelink.url
            #print(URL)
            firebase.post("https://coal-automation-system-default-rtdb.firebaseio.com/URL/",URL)
            os.remove(img_path)
            flag = False
            print()
            face_num = data_face[key]['name']
            print("Hello " + data_face[key]['name'])
            data_match = firebase.get("https://coal-automation-system-default-rtdb.firebaseio.com/Name_num_map",'')
            for item in data_match:
                name = data_match[item]['name']
                if(name == face_num):
                    print()
                    print("The matched number plate is: ")
                    print(data_match[item]['number_plate'])
            print()
    if(flag == True):
        print()
        print('Unknown face')
        URL = "https://cdn.filestackcontent.com/h4dcYnLRMmci0oKidtPw"
        firebase.post("https://coal-automation-system-default-rtdb.firebaseio.com/URL/",URL)
        print()

  


while(True):
    print("Press 1 for recording a new face\nPress 2 for verifying a face")
    choice = int(input())
    face1 = ""

    if(choice == 1):
       face1 =  record_face()
    elif(choice == 2):
        recognize_face()
    else:
        break