import smtplib
import os
import json
import imghdr
from email.message import EmailMessage
from random import randint
from datetime import datetime
from datetime import time
class tools:


    def doctor_registration_register(self ,number,name,surname):
        try:
            payload ={
                "name": f"{name}",
                "surname": f"{surname}",
                "number": number
            }
            with open("/reports/doctor_register,json","a") as infile :
                json.dump(payload,infile)
        except Exception as e  : 
            print("[doctor_registration_register] doctor_registration_register() joining error:",e)

    def create_time_slots(self,data):
        working_hours = data[0]["practise"]["working_hours"]
        open = working_hours["open"]
        closed = working_hours["closed"]
        time_in = int(open.split(":")[0])
        time_out = int(closed.split(":")[0])
        time_slot_array =[]
        time = time_in
        for i in range(0,((time_out+1)-time_in)):
            time_slot_array.append(f"{time}:00")
            time += 1

        return time_slot_array

    def id_analysis(self,data):
        try:
            dob = data[0:6]
            gender  = data[6:7]
            if int(gender)>0 and int(gender) < 4:
                gender = "female"
            elif int(gender)>5 and int(gender) < 9:
                gender ="male"
            return dob,gender
        except Exception as e :
            print("[id_analysis] id_analysis() joining error:",e)


    def generate_id(self,data):
        id = ""
        try :
            print(data)
            ids  = []
            for i in data :
                ids.append(i["patient_number"])
            
            for i in range(0,11):
                id =id + f"{randint(0,9)}" 
            if id in ids :
                for i in range(0,11):
                    id =id + f"{randint(0,9)}" 
            else:
                return id

        except Exception as e:
            print("ERROR-in->generate_id>>>:", e)
        return id
    def generate_task_id(self,data =""):
        id = ""
        try :            
           for i in range(0,5):
                id =id + f"{randint(0,9)}" 
        except Exception as e:
            print("ERROR-in->generate_id>>>:", e)
        return id
      



        
      