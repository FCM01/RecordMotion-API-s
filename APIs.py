
from flask import Flask, request, json, jsonify,send_file
from flask_pymongo import PyMongo
from bson import json_util
from flask_cors import CORS
import json
import datetime
import jwt

from microfunction import tools
from report import report


def parse_json(data):
    return json.loads(json_util.dumps(data))


app=Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/Clinic1"
app.config["SECRET_KEY"] ="flow@master#alphaV1$%^#&@672"

mongo  = PyMongo(app)
CORS(app)

#patient route area
@app.route("/patiant/account/signup",methods=["POST"])
def patient_signup():
    status =200
    resp= {}
    try:
        data = request.get_json("data")
        print("data -->",data)
        name  = data["data"]["name"]
        surname  = data["data"]["surname"]
        email  = data["data"]["email"]
        password  = data["data"]["password"]
        print("name -->",name)
        if name!= "" and surname != "" and email!= "" and password!="" :

                patient_account_payload  = {
                    "name" :f"{name}",
                    "surname" :f"{surname}",
                    "email":f"{email}",
                    "password":f"{password}"
                }

                patient = mongo.db.user_accounts.insert_one(patient_account_payload)
                if patient != None:
                    status =200
                    email_response  = tools()
                    response = email_response.emailing_services(f"{email}",f"{email}","signup")
                    if response != None:
                        resp = {"message":"new user has been added","email":"sent","status":f"{status}"}
                    else:
                        status =400
                        resp = {"message":"new user has been added","email":"not sent","status":f"{status}"}

        else:
            status = 400
            resp={"message":"missing credentials","status":f"{status}"}
    except Exception as e  :
        status = 400
        resp={"message":f"{e}","status":"fail"}
        print("ERORR (patiant/account/signup)--->",e)
    return jsonify(resp),status
@app.route("/kanban/initiate",methods=["GET"])
def kanban_initiate():
    status =200
    resp = {}
    try:
        today = datetime.date.today()
        database_check  = parse_json(mongo.db.kanban.find_one({"id":1}))
        print(database_check)
        if database_check != None:
            database_date = database_check["date"]
            print(database_date)
            print(today)
            if database_date != f"{today}":
                data = parse_json(mongo.db.appointment.find_one({"date":f"{today}"}))
                print("appointment data -->",data)
                if data != None:
                    appointments  = data["bookings"]
                    payload = {"$set": {
                            "id": 1,
                            "date":f"{today}",
                            "appointmentlist":appointments,
                            "arrivedlist": [],
                            "reschedulelist":[]

                        }
                        }
                    response = parse_json(mongo.db.kanban.find())
                    resp  = {"messge":"success","data":response[0]}
                else:
                    payload = {"$set": {
                            "id": 1,
                            "date":f"{today}",
                            "appointmentlist": [],
                            "arrivedlist": [],
                            "reschedulelist":[]

                        }
                        }
                    mongo.db.kanban.update_one({"id": 1}, payload)
                    response = parse_json(mongo.db.kanban.find())
                    resp  = {"messge":"No Appointments Today","data":response[0]}

                if database_check[0]["appointmentlist"] == [] and database_check[0]["arrivedlist"] == [] and database_check[0]["consultationlist"] == [] and database_check[0]["reschedulelist"] == []:
                    data = mongo.db.appointment.find_one({"date":f"{today}"})
                    appointments  = data["bookings"]
                    payload = {"$set": {
                        "id": 1,
                        "date":f"{today}",
                        "appointmentlist": appointments,
                        "arrivedlist": [],
                        "reschedulelist":[]

                    }
                    }


                    mongo.db.kanban.update_one({"id": 1}, payload)
                    response = parse_json(mongo.db.kanban.find())
                    resp  = {"messge":"success","data":response[0]}
                else:
                    data = {
                        "id": 1,
                        "date":f"{today}",
                        "appointmentlist": database_check[0]["appointmentlist"],
                        "arrivedlist": database_check[0]["arrivedlist"],
                        "reschedulelist":database_check[0]["reschedulelist"]


                    }
                    resp  = {"message":"success","data":data}
            else :
                data= parse_json(mongo.db.kanban.find())
                resp = {"message": "kaban up to date","data":data[0]}
        else:
            data = parse_json(mongo.db.appointment.find_one({"date": f"{today}"}))
            appointments = data["bookings"]
            data = {
                        "id": 1,
                        "date":f"{today}",
                        "appointmentlist":appointments,
                        "arrivedlist":[],
                        "reschedulelist":[]


                    }
            mongo.db.kanban.insert_one(data)
            resp = {"message": "kaban inserted"}
    except Exception as e:
        status = 400
        resp = {"message": f"{e}", "status": "fail"}
        print("ERORR (/kanban/initiate)--->", e)
    return jsonify(resp), status

@app.route("/reschedule/appointment",methods = ["POST"])
def reschedule():
    status  = 200
    resp = {}
    try:
        data = request.get_json("data")
        patient_number = data["data"]["patient_number"]
        date = data["data"]["date"]
        today = datetime.date.today()
        if  patient_number != "":
            appointment_response = parse_json(mongo.db.appointment.find_one({"date": f"{today}"}))
            if appointment_response != None:
                array = appointment_response["bookings"]
                appointment = {}
                for i in array:
                    if i["patient_number"] == patient_number:
                        appointment = i
                        array.pop(array.index(i))
                        date_database_check  = parse_json(mongo.db.appointment.find_one({"date":f"{date}"}))
                        patient_check  = parse_json(mongo.db.patients.find_one({"patient_number":f"{patient_number}"}))
                        if patient_check == None:
                            data = parse_json(mongo.db.patients.find())
                            id= tools()
                            patient_number = id.generate_id(data)
                            payload = {
                                "name": i["name"] ,
                                "surname": i["surname"] ,
                                "email": i["email"] ,
                                "date": i["date"] ,
                                "phone_number": i["phone_number"] ,
                                "patient_number":i["patient_number"] ,
                                "service":i["service"] 
                            }
                            mongo.db.profile_tocreate.insert_one(payload)
                        if  date_database_check != None:
                            print(date_database_check)
                            bookings  = date_database_check["bookings"]
                            appointment_payload ={
                                 "name": i["name"] ,
                                "surname": i["surname"] ,
                                "email": i["email"] ,
                                "date": i["date"] ,
                                "time_slot":i["time_slot"],
                                "phone_number": i["phone_number"] ,
                                "patient_number":i["patient_number"] ,
                                "service":i["service"] 
                           
                            }
                            check = {}
                            for i in bookings :
                                if appointment_payload["name"] ==i["name"]:
                                    check = i
                            if check  != {}:
                                if appointment_payload["date"] == check["date"]:
                                    if appointment_payload["time_slot"] == check["time_slot"]:
                                        status = 404
                                        resp ={"message":f"You can not make two appointments for patient in the same day at the same time"}
                                        return jsonify(resp),status
                                    else:
                                        bookings.append(appointment_payload)
                                        payload = {"$set":{
                                                "bookings":bookings,
                                            }
                                            }
                                        mongo.db.appointment.update_one({"date":f"{date}"},payload)
                                        resp ={"message":f"Appointment for patient successfully made","status":status}
                                        return jsonify(resp),status
                            else:
                                bookings.append(appointment_payload)
                                payload = {"$set":{
                                            "bookings":bookings,
                                        }
                                        }
                                mongo.db.appointment.update_one({"date":f"{date}"},payload)
                                resp ={"message":f"Appointment for patient  successfully recheduled","status":status}
                                

                        else:

                            appointment_payload ={
                                 "name": i["name"] ,
                                "surname": i["surname"] ,
                                "email": i["email"] ,
                                "date": i["date"] ,
                                "time_slot":i["time_slot"],
                                "phone_number": i["phone_number"] ,
                                "patient_number":i["patient_number"] ,
                                "service":i["service"] 

                            }
                            bookings = []
                            bookings.append(appointment_payload )
                            payload = {
                            "date":f"{date}",
                            "bookings":bookings,

                            }
                            mongo.db.appointment.insert_one(payload)
#//SECTION:this is the update of the rescheduled appointments orign record                          
                payload = {"$set": {
                    "bookings": array,
                }
                }
                mongo.db.appointment.update_one({"date": f"{today}"}, payload)
                mongo.db.reschedule.insert_one(appointment)
                resp = {"message":"Appointment for patient  successfully recheduled"}
    except Exception as e :
        status = 400
        resp = {"message": f"{e}", "status": "fail"}
        print("ERORR (/reschedule/appointment)--->", e)
    return jsonify(resp), status
@app.route("/kanban/manage",methods=["POST"])
def kanban_mange():
    status =200
    resp = {}
    try:
        data = request.get_json("data")
        appointmentlist = data["data"]["appointmentlist"]
        arrivedlist = data["data"]["arrivedlist"]
        reschedulelist = data["data"]["reschedulelist"]
        today = datetime.date.today()
        if appointmentlist != "" and arrivedlist != ""  and reschedulelist !="":
            database_check =parse_json(mongo.db.kanban.find())
            if database_check == []:
                payload = {
                    "id":1,
                    "date":f"{today}",
                    "appointmentlist": appointmentlist,
                    "arrivedlist": arrivedlist,
                    "reschedulelist":reschedulelist

                }


                mongo.db.kanban.insert_one(payload)
                resp = {"message": "Kaban inserted"}
            else:
                payload = {"$set": {
                    "id": 1,
                    "date":f"{today}",
                    "appointmentlist":appointmentlist,
                    "arrivedlist":arrivedlist,
                    "reschedulelist":reschedulelist

                }
                }
                print(payload)
                mongo.db.kanban.update_one({"id": 1}, payload)
                resp = {"message": "Kaban updated"}

    except Exception as e :
        status = 400
        resp = {"message": f"{e}", "status": "fail"}
        print("ERORR (patiant/account/signup)--->", e)
    return  jsonify(resp),status
#Task  routes

@app.route("/Today/task/retrieve",methods = ["GET"])
def retieve_today_task():
    status  = 200
    resp  = {}
    try:
        today = datetime.date.today()
        tasks  = mongo.db.tasks
        response  = tasks.find({"date":f"{today}"})
        if response != None:
            status = 200
            task_array =[]
            for i in parse_json(response):
                payload = {
                                "task_id": i["task_id"],
                                "task": i["task"],
                                "user_id": i["user_id"],
                                "date": i["date"],
                                "assigned_user": i["assigned_user"],
                                "priority": i["priority"]
                            }

                task_array.append(payload)
            return_response = parse_json(task_array)
            resp = {"response":return_response,"message":"Tasks retrieved"}
        else:
            resp = {"message":"No task today"}

    except Exception as e:
        status = 400
        resp={"message":f"{e}","status":status}
        print("ERORR (/Today/task/retrieve route)--->",e)
    return jsonify(resp),status
@app.route ("/Add/task",methods=["POST"])
def add_task():
    status = 200
    resp  = {}
    try :
        data = request.get_json("data")

        task = data["data"]["task"]
        user_id  = data["data"]["user_id"]
        priority= data["data"]["priority"]
        assigned_user = data["data"]["assigned_user"]
        today = datetime.date.today()
        if task != ""   and user_id != "":
            tool = tools()
            id = tool.generate_task_id()
            payload  =  {
                        "task_id":f"{id}",
                        "task":f"{task}",
                        "user_id":f"{user_id }",
                        "date":f"{today}",
                        "assigned_user":assigned_user,
                        "priority":f"{priority}"

                    }
            mongo.db.tasks.insert_one(payload)
            status = 200
            resp ={"message":"Task successfully added","status":status}
        else:
            status= 400
            resp={"message":"Missing values","status":"fail"}

    except Exception as e:
        status= 400
        resp={"message":f"{e}","status":"fail"}
        print("ERORR (/Add/task route)--->",e)
    return jsonify(resp), status
@app.route("/task/delete",methods=["POST"])
def task_delete():
    status = 200
    resp = {}
    try:
        data  = request.get_json()
        task_id = data["data"]["task_id"]
        if task_id != "":
            database_check  = parse_json(mongo.db.tasks.find({"task_id":task_id}))
            if database_check != []:
                mongo.db.tasks.delete_one({"task_id":task_id})
                resp = {"message":"Task deleted"}
            else:
                status = 401
                resp = {"message":"Task not found"}
        else:
            status  = 400
            resp = {"message":"No task_id"}


    except Exception as e:
        status = 400
        resp = {"message": f"{e}", "status": status}
        print("ERORR (/task/delete)--->", e)
    return  jsonify(resp),status

@app.route("/task/complete",methods=["POST"])
def task_complete():
    status = 200
    resp = {}
    try:
        data  = request.get_json()
        task_id = data["data"]["task_id"]
        print(task_id)
        if task_id != "":
            database_check = parse_json(mongo.db.tasks.find_one({"task_id":f"{task_id}"}))
            print(database_check)
            if database_check != None:
                payload ={
                        "task_id":database_check["task_id"],
                        "task":database_check["task"],
                        "user_id": database_check["user_id"],
                        "date": database_check["date"],
                        "assigned_user":database_check["assigned_user"],
                        "priority": database_check["priority"]

                }
                mongo.db.completed_tasks.insert_one(payload)
                mongo.db.tasks.delete_one({"task_id":f"{task_id}"})
                resp = {"message":"Task Completed"}
            else:
                status = 401
                resp = {"message":"Task not found"}
        else:
            status  = 400
            resp = {"message":"No task_id"}


    except Exception as e:
        status = 400
        resp = {"message": f"{e}", "status": status}
        print("ERORR (/task/complete)--->", e)
    return  jsonify(resp),status

@app.route("/retrieve/task/complete", methods=["GET"])
def retrieve_task_completed():
    resp = {}
    status =200
    try:
        database_check = parse_json(mongo.db.completed_tasks.find({}))
        print(database_check)
        if database_check !=  []:
            array_of_tasks = []
            for i in database_check:
                payload = {
                            "task_id": i["task_id"],
                            "task": i["task"],
                            "user_id": i["user_id"],
                            "date": i["date"],
                            "assigned_user": i["assigned_user"],
                            "priority": i["priority"]
                        }
                array_of_tasks.append(payload)
            resp = {"message":"success","data":array_of_tasks}
        else:
            status = 404
            resp  = {"message":"No completed tasks"}
    except Exception as e:
        status = 400
        resp = {"message": f"{e}", "status": status}
        print("ERORR (/task/complete)--->", e)
    return jsonify(resp), status
@app.route("/retrieve/all/task", methods=["GET"])
def retrieve_all_task():
    resp ={}
    status =200
    try:
        database_check = parse_json(mongo.db.tasks.find({}))
        print(database_check)
        if database_check !=  []:
            array_of_tasks = []
            for i in database_check:
                payload = {
                            "task_id": i["task_id"],
                            "task": i["task"],
                            "user_id": i["user_id"],
                            "date": i["date"],
                            "assigned_user": i["assigned_user"],
                            "priority": i["priority"]
                        }
                array_of_tasks.append(payload)
            resp = {"message":"success","data":array_of_tasks}
        else:
            status = 404
            resp  = {"message":"No tasks"}
    except Exception as e:
        status = 400
        resp = {"message": f"{e}", "status": status}
        print("ERORR (/retrieve/all/task)--->", e)
    return jsonify(resp), status

@app.route("/retrieve/assigned/task", methods=["POST"])
def retrieve_assigned_task():
    resp = {}
    status = 200
    try:
        data =request.get_json("data")
        token = data["data"]["token"]
        data = jwt.decode(token, app.config["SECRET_KEY"],algorithms=['HS256'])
        user_id= data["user_number"]
        database_check = parse_json(mongo.db.tasks.find({}))
       
        if database_check !=  []:
            array_of_tasks = []
            for i in database_check:
                array= i["assigned_user"]
                index= database_check.index(i)
                payload={
                    "array":array,
                    "index":index
                }
                array_of_tasks.append(payload)
            print("[array_of_tasks]-->",array_of_tasks)
            asssigned_tasks=[]
            for i in array_of_tasks:
                for j in i["array"]:
                    if j["user"]=="employee":
                        if user_id == j["data"]["user_number"]:
                            index = i["index"]
                            asssigned_tasks.append(database_check[index])


            print()
            resp = {"message":"success","data":asssigned_tasks}
        else:
            status = 404
            resp  = {"message":"No tasks"}
    except Exception as e:
        status = 400
        resp = {"message": f"{e}", "status": status}
        print("ERORR (/retrieve/assigned/task)--->", e)
    return jsonify(resp), status

#patient routes
@app.route("/patient/find",methods= ["POST"])
def patient_login():
    status  = 200
    resp  = {}
    try :
        data = request.get_json("data")
        patient_deatail =  data["data"]["patient_deatail"]
        if patient_deatail !="":
            retrieved_patient_name = mongo.db.patients
            if  len(patient_deatail) >= 4:
                response = retrieved_patient_name.find({"name":f"{patient_deatail}"})
                data = parse_json(response)
                if data != []:
                    print("data-->",data)
                    patients_array = []
                    for i in data :

                        payload = {
                            "patient_number":i["patient_number"],
                            "name":i["name"],
                            "surname":i["surname"],
                            "email":i["email"],
                            "phone_number":i["phone_number"]
                        }
                        print(payload)
                        patients_array.append(payload)
                    print(patients_array)
                    resp = {"data":patients_array}
                    return  jsonify(resp),status
            if len(patient_deatail)> 1 and len(patient_deatail)< 4 :
                patient_deatail = patient_deatail.upper()
                response = retrieved_patient_name.find({ "name": { "$gt": f"{patient_deatail}" } })
                data = parse_json(response)
                if data != []:
                    print("data-->",data)
                    patients_array = []
                    for i in data :
                        payload = {
                            "patient_number":i["patient_number"],
                            "name":i["name"],
                            "surname":i["surname"],
                            "email":i["email"],
                            "phone_number":i["phone_number"]
                        }
                        print(payload)
                        patients_array.append(payload)
                    print(patients_array)
                    resp = {"data":patients_array}
                    return  jsonify(resp),status
                else:
                    status = 200
                    resp = {"message":"none","status":status}
            else :
                patient_deatail = patient_deatail.upper()
                response = retrieved_patient_name.find({"name": { "$regex": f"^{patient_deatail}" } })
                data = parse_json(response)
                if data != []:
                    print("data-->",data)
                    patients_array = []
                    for i in data :
                        payload = {
                            "patient_number": i["patient_number"],
                            "name":i["name"],
                            "surname":i["surname"],
                            "email":i["email"],
                            "phone_number":i["phone_number"]
                        }
                        print(payload)
                        patients_array.append(payload)
                    print(patients_array)
                    resp = {"data":patients_array}
                    return  jsonify(resp),status
                else:
                    status = 200
                    resp = {"message":"none","status":status}

        else:
            status = 400
            resp = {"message":"missing credetials","status":status}

    except Exception as e:
        status  = 400
        resp={"message":f"{e}","status":status}
        print("ERORR (patient login route)--->",e)
    return jsonify(resp),status

@app.route("/patient/forgot/password",methods= ["POST"])
def forgotpassword():
    status= 200
    resp= {}
    try:
        data = request.json_get("data")
        email = data["data"]["email"]
        if email !="":
            print("email recieved")
            user_email = mongo.db.user_accounts
            user =user_email.find({"email":f"{email}"})
            if user != None:
                print("user has been found")
                #make user password question check so that not jst anyone can retrieve password
    except Exception as e :
        status  = 400
        resp={"message":f"{e}","status":status}
        print("ERORR (forgotpassword route)--->",e)


@app.route("/patient/profile/creation",methods =["POST"])
def patient_prfile_creation():
    status = 200
    resp  = {}
    try :
        if mongo:
            data =request.get_json("data")
            print(data)
            name = data["data"]["name"]
            surname = data["data"]["surname"]
            email = data["data"]["email"]
            phone_number = data["data"]["phone_number"]
            title = data["data"]["title"]
            id_number  = data["data"]["id_number"]
            premed_issues = data["data"]["preexsiting_medical_issues"]
            allgergies = data["data"]["allgergies"]
            medical_aid_providers = data["data"]["medical_aid_providers"]
            medical_aid_number = data["data"]["medical_aid_number"]
            nearest_family_friend_name = data["data"]["nearest_family_friend_name"]
            nearest_family_friend_phonenumber = data["data"]["nearest_family_friend_phonenumber"]
            nearest_family_friend_id_number = data["data"]["nearest_family_friend_id_number"]
            street_address = data["data"]["street_address"],
            agreement = data["data"]["agreement"]
            city = data["data"]["city"],
            postal_code=data["data"]["postal_code"],


            if name != "" and surname != "" and email != "" and phone_number!="" and title!="" and id_number != "" :
                numbers =parse_json(mongo.db.patients.find({}, {"patient_number":1}))
                patient_number = tools().generate_id(numbers)
                patient_id_analysis  =tools().id_analysis(id_number)
                patients_payload  =  {
                        "patient_number":patient_number,
                        "name" :f"{name}",
                        "surname":f"{surname}",
                        "email":f"{email}",
                        "phone_number":f"{phone_number}",
                        "id_number":f"{id_number}",
                        "date_of_birth":patient_id_analysis[0],
                        "title":f"{title}",
                        "gender":patient_id_analysis[1],
                        "preexsiting_medical_issues":f"{premed_issues}",
                        "allgergies":f"{allgergies}",
                        "medical_aid_providers":f"{medical_aid_providers}",
                        "medical_aid_number":f"{medical_aid_number}",
                        "nearest_family_friend_name":f"{nearest_family_friend_name}",
                        "nearest_family_friend_phonenumber":f"{nearest_family_friend_phonenumber}",
                        "nearest_family_friend_id_number":f"{nearest_family_friend_id_number}",
                        "street_address":f"{street_address}",
                        "city":f"{city}",
                        "postal_code":f"{postal_code}",
                        "agreement":agreement,
                    }

                mongo.db.patients.insert_one(patients_payload)
                status = 200
                resp ={"message":f"New patienst {name} successfully added","status":status}

            else:
                status= 400
                resp={"message":"missing values","status":"fail"}

    except Exception as e:
        status= 400
        resp={"message":f"{e}","status":"fail"}
        print("ERORR (/patient/profile/creation)--->",e)
    return jsonify(resp), status
#route used to coomplete an incomplete profile made at the appointment route (for patients that dont have complet profiles)
@app.route("/patient/profile/complete",methods =["POST"])
def patient_prfile_complete():
    status = 200
    resp  = {}
    try :
        if mongo:
            data =request.get_json("data")
            print(data)
            name = data["data"]["name"]
            surname = data["data"]["surname"]
            email = data["data"]["email"]
            phone_number = data["data"]["phone_number"]
            title = data["data"]["title"]
            id_number  = data["data"]["id_number"]
            premed_issues = data["data"]["preexsiting_medical_issues"]
            allgergies = data["data"]["allgergies"]
            medical_aid_providers = data["data"]["medical_aid_providers"]
            medical_aid_number = data["data"]["medical_aid_number"]
            nearest_family_friend_name = data["data"]["nearest_family_friend_name"]
            nearest_family_friend_phonenumber = data["data"]["nearest_family_friend_phonenumber"]
            nearest_family_friend_id_number = data["data"]["nearest_family_friend_id_number"]
            street_address = data["data"]["street_address"],
            patient_number = data["data"]["patient_number"]
            agreement = data["data"]["agreement"]
            city = data["data"]["city"],
            postal_code=data["data"]["postal_code"],


            if name != "" and surname != "" and email != "" and phone_number!="" and title!="" and id_number != "" :
                patient_id_analysis  =tools().id_analysis(id_number)
                patients_payload  =  {
                        "patient_number":patient_number,
                        "name" :f"{name}",
                        "surname":f"{surname}",
                        "email":f"{email}",
                        "phone_number":f"{phone_number}",
                        "id_number":f"{id_number}",
                        "date_of_birth":patient_id_analysis[0],
                        "title":f"{title}",
                        "gender":patient_id_analysis[1],
                        "preexsiting_medical_issues":f"{premed_issues}",
                        "allgergies":f"{allgergies}",
                        "medical_aid_providers":f"{medical_aid_providers}",
                        "medical_aid_number":f"{medical_aid_number}",
                        "nearest_family_friend_name":f"{nearest_family_friend_name}",
                        "nearest_family_friend_phonenumber":f"{nearest_family_friend_phonenumber}",
                        "nearest_family_friend_id_number":f"{nearest_family_friend_id_number}",
                        "street_address":f"{street_address}",
                        "city":f"{city}",
                        "postal_code":f"{postal_code}",
                        "agreement":agreement,
                    }

                mongo.db.patients.insert_one(patients_payload)
                mongo.db.profile_tocreate.delete_one({"patient_number":patient_number})
                status = 200
                resp ={"message":f"New patienst {name} successfully complete","status":status}

            else:
                status= 400
                resp={"message":"missing values","status":"fail"}

    except Exception as e:
        status= 400
        resp={"message":f"{e}","status":"fail"}
        print("ERORR (/patient/profile/complete)--->",e)
    return jsonify(resp), status

@app.route("/patient/complete/delete", methods= ["POST"])
def delete_profiles_to_complete():
    status = 200
    resp  = {}
    try:
        data = request.get_json()
        patient_number = data["data"]["patient_number"]
        if patient_number != "":
            database_check = parse_json(mongo.db.patients.find({"patient_number": patient_number}))
            if database_check != []:
                mongo.db.patients.delete_one({"patient_number": patient_number})
                resp = {"message": "Profile to complete deleted"}
            else:
                status = 404
                resp = {"message": "Profile to complete not found"}
        else:
            status = 400
            resp = {"message": "No patient_number"}
    except Exception as e:
        status = 400
        resp = {"message": f"{e}", "status": status}
        print("ERORR (/patient/complete/delete route)--->", e)
    return jsonify(resp), status
@app.route("/retrieve/patients/profiles/complete", methods= ["GET"])
def retrieve_profiles_toccomplete():
    status = 200
    resp  = {}
    try:
            patient_tocreate = parse_json( mongo.db.profile_tocreate.find())
            if  patient_tocreate != None:
                array_of_profiles = []
                for i in patient_tocreate:
                    payload = {
                        "name": i["name"],
                        "surname": i["surname"],
                        "email": i["email"],
                        "phone_number": i["phone_number"],
                        "patient_number": i["patient_number"]
                    }
                    array_of_profiles.append(payload)
                status =200
                resp = {"message":"Profiles retieved ","data":array_of_profiles}
            else:
                status  = 404
                resp = {"message":"There are no profiles to complete","create":True}
    except Exception as e :
        status = 400
        resp = {"message": f"{e}", "status": status}
        print("ERORR (/retrieve/patients/profiles/complete route)--->", e)
    return jsonify(resp), status
@app.route("/patient/delete",methods=["POST"])
def patient_delete():
    status = 200
    resp = {}
    try:
        data  = request.get_json()
        patient_number = data["data"]["patient_number"]
        if patient_number != "":
            database_check  = parse_json(mongo.db.patients.find({"patient_number":patient_number}))
            if database_check != []:
                mongo.db.patients.delete_one({"patient_number":patient_number})
                resp = {"message":"Patient deleted"}
            else:
                status = 401
                resp = {"message":"Patient not found"}
        else:
            status  = 400
            resp = {"message":"No patient_number"}


    except Exception as e:
        status = 400
        resp = {"message": f"{e}", "status": status}
        print("ERORR (/patient/delete)--->", e)
    return  jsonify(resp),status
@app.route("/check/to/create",methods=["POST"])
def patient_to_complete_check():
    status = 200
    resp = {}
    try:
        data  = request.get_json()
        patient_number = data["data"]["patient_number"]
        if patient_number != "":
            database_check  = parse_json(mongo.db.profile_tocreate.find({"patient_number":patient_number}))
            if database_check != []:
                resp = {"message":"Patients profile needs to be created"}
            else:
                status = 200
                resp = {"message":"success"}
        else:
            status  = 400
            resp = {"message":"No patient_number"}


    except Exception as e:
        status = 400
        resp = {"message": f"{e}", "status": status}
        print("ERORR (/patient/delete)--->", e)
    return  jsonify(resp),status
@app.route("/patient/edit",methods=["POST"])
def patient_edit():
    status= 200
    resp = {}
    try:
        data = request.get_json("data")
        print(data)
        patient_number = data["data"]["patient_number"]
        name = data["data"]["name"]
        surname = data["data"]["surname"]
        email = data["data"]["email"]
        phone_number = data["data"]["phone_number"]
        medical_aid_providers = data["data"]["medical_aid_providers"]
        medical_aid_number = data["data"]["medical_aid_number"]
        nearest_family_friend_name = data["data"]["nearest_family_friend_name"]
        nearest_family_friend_phonenumber = data["data"]["nearest_family_friend_phonenumber"]
        street_address = data["data"]["street_address"],
        print(street_address)
        city = data["data"]["city"],
        postal_code = data["data"]["postal_code"],
        if name != "" and surname != "" and email != "" and phone_number != "" :
            payload = {"$set": {
                        "name" :f"{name}",
                        "surname":f"{surname}",
                        "email":f"{email}",
                        "phone_number":f"{phone_number}",
                        "medical_aid_providers":f"{medical_aid_providers}",
                        "medical_aid_number":f"{medical_aid_number}",
                        "nearest_family_friend_name":f"{nearest_family_friend_name}",
                        "nearest_family_friend_phonenumber":f"{nearest_family_friend_phonenumber}",
                        "street_address":street_address,
                        "city":city,
                        "postal_code":postal_code


            }
            }
            mongo.db.patients.update_one({"patient_number": f"{patient_number}"}, payload)
            resp = {"message":"Patient information updated"}

    except Exception as e:
        status = 400
        resp = {"message": f"{e}", "status": status}
        print("ERORR (/patient/delete)--->", e)
    return jsonify(resp), status
@app.route("/retrieve/patientlist",methods=["GET"])
def get_patient_list():
    status = 200
    resp  = {}
    try:
        patients = mongo.db.patients
        response  = patients.find()
        if response != None:
            status = 200
            patients_list =[]
            for i in parse_json(response) :
                consultation_number = mongo.db.consultation.count_documents({"patient_number":i["patient_number"]})
                payload = {
                    "patient_number":i["patient_number"],
                    "name":i["name"],
                    "surname":i["surname"],
                    "clist":consultation_number,
                }
                patients_list.append(payload)
            resp = {"data":patients_list,"message":"patients retieved","status":status}
    except Exception as e :
        status  = 400
        resp={"message":f"{e}","status":status}
        print("ERORR (/retrieve/patientlist)--->",e)
    return jsonify(resp),status

@app.route("/retrieve/patient/profile",methods=["POST"])
def get_patient_profile():
    status = 200
    resp  = {}
    try:
        data =request.get_json("data")
        patient_number = data["data"]["patient_number"]
        patients = mongo.db.patients
        response  = patients.find_one({"patient_number":f"{patient_number}"})
        if response != None:
            status = 200
            patients_profile = parse_json(response)
            patients_payload = {
                "name": patients_profile['name'],
                "surname": patients_profile['surname'],
                "email": patients_profile['email'],
                "phone_number": patients_profile['phone_number'],
                "date_of_birth": patients_profile['date_of_birth'],
                "id_number": patients_profile['id_number'],
                "medical_aid_providers": patients_profile['medical_aid_providers'],
                "medical_aid_number": patients_profile['medical_aid_number'],
                "nearest_family_friend_name": patients_profile['nearest_family_friend_name'],
                "nearest_family_friend_phonenumber": patients_profile['nearest_family_friend_phonenumber'],
                "street_address": patients_profile['street_address'],
                "city": patients_profile['city'],
                "postal_code": patients_profile['postal_code'],
            }
            print(patients_payload)
            resp = {"data":patients_payload,"message":"patients retieved","status":status}
    except Exception as e :
        status  = 400
        resp={"message":f"{e}","status":status}
        print("ERORR (patients retrieve route)--->",e)
    return jsonify(resp),status

#doctor route area
@app.route ("/staff/adduser",methods=["POST"])
def staff_adduser():
    status = 200
    response  = {}
    try :
        data = request.json_get("data")
        name = data["data"]["name"]
        surname = data["data"]["surname"]
        id_number  = data["data"]["id_number"]
        email= data["data"]["email"]
        password = data["data"]["password"]
        speciallity = data["data"]["speciallity"]

        if name != "" and surname != ""  and id_number != "":
            doctor_payload  =  {
                        "name":f"{name}",
                        "surname":f"{surname}",
                        "id_number":f"{id_number}",
                        "speciallity":f"{speciallity}",
                        "email":f"{email}",
                        "password":f"{password}",
                        "access_level": 1
                    }
            doctors = mongo.db.staff_accounts.insert(doctor_payload)
            status = 200
            resp ={"message":f"new doctor {name} successfully added","status":status}
        else:
            status= 400
            resp={"message":"missing values","status":"fail"}

    except Exception as e:
        status= 400
        resp={"message":f"{e}","status":"fail"}
        print("ERORR (signup route)--->",e)
    return jsonify(resp), status

@app.route("/staff/retrieve",methods = ["GET"])
def retrieve_staff():
    status = 200
    resp = {}
    try :
        staff = mongo.db.user_accounts
        response = staff.find()
        if response != None:
            status  = 200
            staff_list =[]
            data = parse_json(response)
            for i  in data:

                payload = {
                    "name":i["name"],
                    "surname":i["surname"],
                    "user_number":i["user_number"]
                }
                staff_list.append(payload)

            resp=  {"message":"sucess","status":f"{status}","staff_list":staff_list}

    except Exception as e :
        status= 400
        resp={"message":f"{e}","status":"fail"}
        print("ERORR (retrieve_active_doctorlist route)--->",e)
    return jsonify(resp),status
@app.route("/doctor/signup",methods = ["POST"])
def doctor_signup():
    status = 200
    resp  = {}
    try:
        data  = request.get_json("data")
        print("data==>",data)
        personal  = data["data"]["step1"]
        practise  = data["data"]["step2"]
        finnaces  = data["data"]["step3"]
        if personal != {} and practise !=  {} and finnaces != {}:
            service  = tools()
            # email = personal["email"]
            # name = personal["first_name"]
            payload   =  {
                "personal" : personal,
                "practise"  : practise,
                "finnaces"  : finnaces
            }
            database_check  = parse_json(mongo.db.patients.find({}, {"user_number":1}))
            id  = tools().generate_id(database_check)
            user_account ={
                "user_number":f"{id}",
                "name":personal["name"],
                "surname":personal["name"],
                "email":personal["name"],
                "password":personal["name"],
                "user_type": 1
            }
            # email= service.emailing_services(email,name,"signup")
            # service.doctor_registration_register(personal["first_name"],personal["surname"],practise["practise_number"])
            mongo.db.doctor.insert_one(payload)
            mongo.db.user_accounts.insert_one(user_account)
            resp =  {"message":"successful","response":"1"}
        else:
            resp  =  {"message": "missing information"}



    except Exception as e :
        status= 400
        resp={"message":f"{e}","status":"fail"}
        print("ERORR (/doctor/signup route)--->",e)
    return jsonify(resp),status

# statisics routes 
@app.route ("/stats/patient/consultation",methods= ["POST"])
def stats_patient_consultaion():
    status  = 200
    resp = {}
    try:
       data = request.get_json("data")
       print(data)
       patient_number = data["data"]["patient_number"]
       if patient_number != "":
            consultation_number = mongo.db.consultation.count_documents({"patient_number":patient_number})
            if consultation_number == 0:
                resp ={"message":"Patient does not have consultions"}
            else:
                resp = {"data":consultation_number,"message":"success"}

    except Exception as e :
        status= 403
        resp={"message":f"{e}","status":"fail"}
        print("ERORR (/stats/consultation route)--->",e)
    return jsonify(resp),status
@app.route ("/stats/patient/followups",methods= ["POST"])
def stats_patient_followups():
    status  = 200
    resp = {}
    try:
       data = request.get_json("data")
       patient_number = data["data"]["patient_number"]
       if patient_number != "":
            followups_number = mongo.db.followup.count_documents({"patient_number":patient_number})
            if followups_number == 0:
                resp ={"message":"Patient does not have consultions"}
            else:
                resp = {"data":followups_number,"message":"success"}
       else:
           status = 404
           resp = {"message": "Followup not found", "status": "fail"}

    except Exception as e :
        status= 403
        resp={"message":f"{e}","status":"fail"}
        print("ERORR (/stats/consultation route)--->",e)
    return jsonify(resp),status
@app.route ("/stats/files",methods= ["GET"])
def stats_files():
    status  = 200
    resp = {}
    try:
            doctors_note_number = mongo.db.doctors_note_files.count_documents({})
            perscriptions_number = mongo.db.perscription_files.count_documents({})

            if doctors_note_number == 0 and  perscriptions_number ==0:
                resp ={"message":"No documents created yet"}
            else:
                payload  = {
                    "doctors_note_number":doctors_note_number,
                    "perscriptions_number":perscriptions_number
                }
                resp = {"data":payload,"message":"success"}
   
    except Exception as e :
        status= 403
        resp={"message":f"{e}","status":"fail"}
        print("ERORR (/stats/files route)--->",e)
    return jsonify(resp),status

@app.route ("/retrieve/files",methods= ["GET"])
def retrieve_files():
    status  = 200
    resp = {}
    try:
            doctors_note= mongo.db.doctors_note_files.find({})
            perscriptions= mongo.db.perscription_files.find({})

            if doctors_note == [] and  perscriptions ==[]:
                resp ={"message":"No documents created yet"}
            else:
                array_of_doctors_notes =[]
                array_of_perscriptions =[]
                for i in doctors_note:
                    payload = {
                        "id": i["id"],
                        "patient_number": i["patient_number"],
                        "url": i["url"],
                        "filename": i["filename"],
                        "type": i["type"]
                    } 
                    array_of_doctors_notes.append(payload)
                for i in perscriptions:
                    payload ={
                        "id": i["id"],
                        "patient_number": i["patient_number"],
                        "url": i["url"],
                        "filename": i["filename"],
                        "type": i["type"]
                    }
                    array_of_perscriptions.append(payload)

                payload  = {
                    "doctors_note":array_of_doctors_notes,
                    "perscriptions":array_of_perscriptions
                }
                resp = {"data":payload,"message":"success"}
   
    except Exception as e :
        status= 403
        resp={"message":f"{e}","status":"fail"}
        print("ERORR (/retrieve/files route)--->",e)
    return jsonify(resp),status

@app.route ("/stats/number/patients",methods= ["GET"])
def stats_number_patients():
    status  = 200
    resp = {}
    try:
      
            patient_number = mongo.db.patients.count_documents({})
            if patient_number == 0:
                resp ={"message":"Your practise has no patients"}
            else:
                resp = {"data":patient_number,"message":"success"}

    except Exception as e :
        status= 403
        resp={"message":f"{e}","status":"fail"}
        print("ERORR (/stats/consultation route)--->",e)
    return jsonify(resp),status
@app.route ("/stats/all/consultaions",methods= ["GET"])
def stats_all_consultaions():
    status  = 200
    resp = {}
    try:
            consultation_number = mongo.db.consultation.count_documents({})
            if consultation_number == 0:
                resp ={"message":"There are no consultations"}
            else:
                resp = {"data":consultation_number,"message":"success"}

    except Exception as e :
        status= 403
        resp={"message":f"{e}","status":"fail"}
        print("ERORR (/stats/all/consultaions route)--->",e)
    return jsonify(resp),status

@app.route ("/stats/bargraph/appointments",methods= ["GET"])
def stats_bargraph():
    status  = 200
    resp = {}
    try:
            today = datetime.date.today()
            data = mongo.db.appointment.find_one({"date":f"{today}"})
            if data != None:
                bookings_array = data["bookings"]
                database_check = parse_json(mongo.db.doctor.find())
                service = tools()
                time_slots_array = service.create_time_slots(parse_json(database_check))
                number = 0
                data = []
                counter = 0
                print(len(time_slots_array))
                for i in time_slots_array:
                    for j in bookings_array:
                        if i == j["time_slot"]:
                            number += 1
                            counter += 1
                        else:
                            counter += 1
                    if number == 0 and counter == len(bookings_array):
                        counter = 0
                        number = 0
                        data.append(number)
                    elif number > 0 and counter == len(bookings_array):
                        data.append(number)
                        counter = 0
                        number = 0
                resp ={"data":data,"labels":time_slots_array}
            else:
                status = 404
                resp = {"message":"no data"}

    except Exception as e :
        status= 403
        resp={"message":f"{e}","status":"fail"}
        print("ERORR (/stats/bargraph/appointments route)--->",e)
    return jsonify(resp),status
@app.route ("/stats/daily/bargraph/appointments",methods= ["GET"])
def stats_daily_bargraph():
    status  = 200
    resp = {}
    try:
            database_check = parse_json(mongo.db.appointment.find({}))
            if database_check != []:
                labels = []
                data = []
                for i in database_check:
                    print(i)
                    labels.append(i["date"])
                    array = i["bookings"]
                    data.append(len(array))
                resp ={"data":data,"labels":labels}
            else:
                status = 404
                resp = {"message":"no data"}

    except Exception as e :
        status= 403
        resp={"message":f"{e}","status":"fail"}
        print("ERORR (/stats/daily/bargraph/appointments route)--->",e)
    return jsonify(resp),status

@app.route ("/stats/all/followup",methods= ["GET"])
def stats_followup():
    status  = 200
    resp = {}
    try:
            followup_number = mongo.db.followup.count_documents({})
            if  followup_number == 0:
                resp ={"message":"There are no followups"}
            else:
                resp = {"data":followup_number,"message":"success"}

    except Exception as e :
        status= 403
        resp={"message":f"{e}","status":"fail"}
        print("ERORR (/stats/followup route)--->",e)
    return jsonify(resp),status


@app.route("/stats/all/appointments", methods=["GET"])
def stats_all_appointments():
    status = 200
    resp = {}
    try:
        today = datetime.date.today()
        data = mongo.db.appointment.find_one({"date": f"{today}"})
        if data != None:
            bookings_array = data["bookings"]
            number_of_appointments = len( bookings_array)
            if number_of_appointments == 0 :
                resp = {"message": "success","data":0}
            else:
                resp = {"message": "success","data":number_of_appointments}
        else:
            status= 404
            resp = {"message": "No data"}

    except Exception as e:
        status = 403
        resp = {"message": f"{e}", "status": "fail"}
        print("ERORR (/stats/all/appointments route)--->", e)
    return jsonify(resp), status


@app.route("/stats/active/tasks", methods=["GET"])
def stats_active_tasks():
    status = 200
    resp = {}
    try:

        profile_number = mongo.db.tasks.count_documents({})
        if profile_number == 0:
            resp = {"message": "There are no tasks"}
        else:
            resp = {"data": profile_number, "message": "success"}

    except Exception as e:
        status = 403
        resp = {"message": f"{e}", "status": "fail"}
        print("ERORR (/stats/active/tasks route)--->", e)
    return jsonify(resp), status
@app.route("/stats/profiles/to/complete", methods=["GET"])
def stats_profiles_to_complete():
    status = 200
    resp = {}
    try:

        profile_number = mongo.db.profile_tocreate.count_documents({})
        if profile_number == 0:
            resp = {"message": "There are no profiles"}
        else:
            resp = {"data": profile_number, "message": "success"}

    except Exception as e:
        status = 403
        resp = {"message": f"{e}", "status": "fail"}
        print("ERORR (/stats/profiles/to/complete route)--->", e)
    return jsonify(resp), status

@app.route ("/unprotected",methods= ["POST"])
def unprotected():
    status  = 200
    resp = {}
    try:
        resp   = {"message":"anyone can view this"}
    except Exception as e :
        status= 403
        resp={"message":f"{e}","status":"fail"}
        print("ERORR (/unprotected route)--->",e)
    return jsonify(resp),status
@app.route ("/protected",methods= ["POST"])
def protected():
    status  = 200
    resp = {}
    try:
        data = request.get_json("data")
        token = data["data"]["token"]
        if token == "":
            return jsonify({"message":"invalid"}),403
        try:
            data = jwt.decode(token, app.config["SECRET_KEY"],algorithms=['HS256'])
            resp  = {"message":"valid"}
            return jsonify(resp),200
        except:
            return jsonify({"message":'invalid'}),403

    except Exception as e :
        status= 403
        resp={"message":f"{e}","status":"fail"}
        print("ERORR (/protected route)--->",e)
    return jsonify(resp),status

@app.route ("/user/login",methods= ["POST"])
def user_login():
    status = 200
    resp=  {}
    try:
        data = request.get_json("data")
        email = data["data"]["email"]
        password  = data["data"]["password"]
        if email !="" or password  != "":
            data = parse_json(mongo.db.user_accounts.find({"email":f"{email}"}))
            print(data)
            if data != []:
                database_password = data[0]["password"]
                user_number = data[0]["user_number"]
                if password ==database_password:
                    token = jwt.encode({"user_number":user_number,"exp":datetime.datetime.utcnow()+ datetime.timedelta(minutes=180)},app.config["SECRET_KEY"])
                    status = 200
                    name  = data[0]["name"]
                    surname  = data[0]["surname"]

                    welcome_payload = {
                        "user" :f"{name} {surname }"
                    }
                    resp = {"token":token,"message":welcome_payload,"status":status}
                else:
                    status = 403
                    resp = {"message":"Incorrect password","status":status}
                    return jsonify(resp),status
            else:
                status = 403
                resp = {"message":"Account does not exist","status":status}
                print(resp)
    except Exception as e:
        status  = 400
        resp={"message":f"{e}","status":status}
        print("ERORR /user/login route)--->",e)
    return jsonify(resp),status

@app.route ("/retrieve/user",methods= ["POST"])
def user_retrieve():
    status = 200
    resp=  {}
    try:
        data = request.get_json("data")
        token = data["data"]["token"]
        data = jwt.decode(token, app.config["SECRET_KEY"],algorithms=['HS256'])
        user_number = data["user_number"]
        if user_number != "":
            data = parse_json(mongo.db.doctor.find({}))
            emergency = parse_json(mongo.db.emergancy.find({}))
            print("emergency-->",emergency)
            user_account = parse_json(mongo.db.user_accounts.find_one({"user_number":user_number}))
            if user_account != None and data != []:
                settings ={
                    "practise":data[0]["practise"],
                    "finnaces":data[0]["finnaces"]
                }
                print("settings-->",settings)
                user_account = {
                    "email": user_account["email"],
                    "name": user_account["name"],
                    "surname": user_account["surname"],
                    "user_number": user_account["user_number"]
                }
                print("user_account-->",user_account)
                emergency_payload = {
                    "name":emergency[0]["name"],
                    "phone_number":emergency[0]["phone_number"],
                    "email":emergency[0]["email"]
                }
                print("emergency_payload-->",emergency_payload)
                resp ={"message":"success","settings":settings,"user_account":user_account,"emergency":emergency_payload}
        else:
            status = 404
            resp ={"message":"No user number provide"}
        
    except Exception as e:
        status  = 400
        resp={"message":f"{e}","status":status}
        print("ERORR /retrieve/user route)--->",e)
    return jsonify(resp),status


#appointment route area
@app.route("/Time/slot",methods=["GET"])
def time_slots():
    status  = 200
    resp  = {}
    try:
        #get current data variable
        database_check = parse_json(mongo.db.doctor.find())
        threshhold = database_check[0]
        threshhold = threshhold["finnaces"]["patient_threshhold"]
        service = tools()
        time_slots_array  = service.create_time_slots(parse_json(database_check))
        resp= {"time_slots":time_slots_array}

    except Exception as e:
        status  = 400
        resp={"message":f"{e}","status":status}
        print("ERORR (/time/slot route)--->",e)
    return jsonify(resp),status
@app.route("/patient/appointments",methods=["POST"])
def create_appointment():
    status  = 200
    resp = {}
    try:
        data = request.get_json("data")
        name = data["data"]["name"]
        surname  =data["data"]["surname"]
        email = data["data"]["email"]
        date = data["data"]["date"]
        time_slot = data["data"]["time_slot"]
        phone_number= data["data"]["phone_number"]
        patient_number  = data["data"]["patient_number"]
        service= data["data"]["service"]

        if name != "" and surname != ""and email != "" and date != "" and time_slot!="" and  phone_number != "":
            today = datetime.date.today()
            date_database_check  = parse_json(mongo.db.appointment.find_one({"date":f"{date}"}))
            patient_check  = parse_json(mongo.db.patients.find_one({"patient_number":f"{patient_number}"}))
            if patient_check == None:
                data = parse_json(mongo.db.patients.find())
                id= tools()
                patient_number = id.generate_id(data)
                payload = {
                    "name": f"{name}",
                    "surname": f"{surname}",
                    "email": f"{email}",
                    "date": f"{date}",
                    "time_slot":f"{time_slot}",
                    "phone_number": f"{phone_number}",
                    "patient_number": f"{patient_number}",
                    "service":f"{service}"
                }
                mongo.db.profile_tocreate.insert_one(payload)
            if  date_database_check != None:
                bookings  = date_database_check["bookings"]
                appointment_payload ={
                "name":f"{name}",
                "surname":f"{surname}",
                "email":f"{email}",
                "date":f"{date}",
                "phone_number":f"{phone_number}",
                "time_slot":f"{time_slot}",
                "patient_number":f"{patient_number}",
                "service": f"{service}"
                }
                check = {}
                for i in bookings :
                    if appointment_payload["name"] ==i["name"]:
                        check = i
                if check  != {}:
                    if appointment_payload["date"] == check["date"]:
                        if appointment_payload["time_slot"] == check["time_slot"]:

                            resp ={"message":f"You can not make two appointments for {name} in the same day at the same time"}
                            return jsonify(resp),status
                        else:
                            bookings.append(appointment_payload)
                            payload = {"$set":{
                                    "bookings":bookings,
                                }
                                }
                            mongo.db.appointment.update_one({"date":f"{date}"},payload)
                            resp ={"message":f"New appointment for {name} successfully made","status":status}
                            return jsonify(resp),status
                else:
                    bookings.append(appointment_payload)
                    payload = {"$set":{
                                "bookings":bookings,
                            }
                            }
                    mongo.db.appointment.update_one({"date":f"{date}"},payload)
                    resp ={"message":f"New appointment for {name} successfully made","status":status}
                    return jsonify(resp),status

            else:

                appointment_payload ={
                    "name":f"{name}",
                    "surname":f"{surname}",
                    "email":f"{email}",
                    "date":f"{date}",
                    "phone_number":f"{phone_number}",
                    "time_slot":f"{time_slot}",
                    "patient_number":f"{patient_number}",
                    "service":f"{service}"

                }
                bookings = []
                bookings.append(appointment_payload )
                payload = {
                "date":f"{date}",
                "bookings":bookings,

                 }


                # appointment_email = tools()
                # appointment_email.emailing_services(f"{email}",f"{name}","appointment")
                mongo.db.appointment.insert_one(payload)
                resp ={"message":f"New appointment for {name} successfully made","status":status}
        else:
            status = 200
            resp = {"message":"missings information","status":status}
    except Exception as e:
        status  = 200
        resp={"message":f"{e}","status":status}
        print("ERORR (appointment route)--->",e)
    return jsonify(resp),status

@app.route("/appointment/delete",methods= ["POST"])
def appointment_delete():
    status  = 200
    resp = {}
    try:
        data = request.get_json("data")
        appointment = data["data"]["appointment"]
        today =  datetime.date.today()
        database_check  = parse_json(mongo.db.appointment.find({"date":f"{today}"}))
        if database_check != []:
            array = database_check[0]["bookings"]
            for i in array:
                if i["patient_number"]== appointment["patient_number"]:
                    array.pop(array.index(i))
                else:
                    status = 404
                    resp = {"message":"Appointment not found"}
                payload = {"$set":{
                                "bookings":array,
                            }
                        }
                mongo.db.appointment.update_one({"date":f"{today}"},payload)
            resp ={"message":"Appointment Deleted"}
        else:
            status  = 401
            resp = {"message":"No Appoinmensts Today"}
    except Exception as e:
        status  = 400
        resp={"message":f"{e}","status":status}
        print("ERORR (appointment route)--->",e)
    return jsonify(resp),status
@app.route("/history/appointment/retrieve",methods = ["POST"])
def retieve_history_appointments():
    status  = 200
    resp  = {}
    try:
        data = request.get_json("data")
        date  = data["data"]["date"]
        if date != "":
            appointments  = mongo.db.appointment
            response = parse_json(appointments.find({"date": f"{date}"}))
            if response != None:
                status = 200    
                resp = {"data":response,"message":"appointments retrieved","status":status}
            else :
                status = 401
                resp = {"message":"Appointments dates not present","status":status} 
    except Exception as e:
        status = 400
        resp={"message":f"{e}","status":status}
        print("ERORR (/history/appointment/retrieve)--->",e)
    return jsonify(resp),status
@app.route("/history/appointment/dates/retrieve",methods = ["GET"])
def retieve_appointments_dates():
    status  = 200
    resp  = {}
    try:
        appointments  = mongo.db.appointment
        response = parse_json(appointments.find())
        if response != None:
            status = 200
            dates = []
            for i in response:
                dates.append(i["date"])
            resp = {"data":dates,"message":"appointments dates retrieved","status":status}
        else :
            status = 401
            resp = {"message":"Appointments dates not present","status":status} 
    except Exception as e:
        status = 400
        resp={"message":f"{e}","status":status}
        print("ERORR (/history/appointment/dates/retrieve)--->",e)
    return jsonify(resp),status

@app.route("/alltoday/appointment/retrieve",methods = ["GET"])
def retieve_appointments():
    status  = 200
    resp  = {}
    try:
        today = datetime.date.today()
        appointments  = mongo.db.appointment
        response = parse_json(appointments.find_one({"date":f"{today}"}))
        print(response)
        if response != None:
            data = response
            status = 200
            array_of_appointments = []
            for i in data["bookings"]:
                patient_number = i["patient_number"]
                database_check  = parse_json(mongo.db.profile_tocreate.find_one({"patient_number":patient_number}))
                print(database_check)
                if database_check != None:
                    payload = {
                        "name": i["name"],
                        "surname": i["surname"],
                        "email": i["email"],
                        "date": i["date"],
                        "time_slot": i["time_slot"],
                        "phone_number": i["phone_number"],
                        "patient_number": i["patient_number"],
                        "profile_complete":True
                    }
                    array_of_appointments.append(payload)
                else:
                    payload ={
                        "name": i["name"],
                        "surname": i["surname"],
                        "email": i["email"],
                        "date": i["date"],
                        "time_slot": i["time_slot"],
                        "phone_number": i["phone_number"],
                        "patient_number": i["patient_number"],
                        "profile_complete": False

                    }
                    array_of_appointments.append(payload)
                print(array_of_appointments)
            data["bookings"] = array_of_appointments
            resp = {"data":array_of_appointments,"message":"appointments retrieved","status":status}
    except Exception as e:
        status = 400
        resp={"message":f"{e}","status":status}
        print("ERORR (/alltoday/appointment/retrieve)--->",e)
    return jsonify(resp),status
@app.route("/today/appointment/retrieve",methods = ["GET"])
def today_appointments():
    status  = 200
    resp  = {}
    try:
        today = datetime.date.today()
        appointments  = mongo.db.appointment
        response  = parse_json(appointments.find({"date":f"{today}"}))
        if response != []:
            data = parse_json(response)
            bookings = data[0]["bookings"]
            appointments_array = []
            now = datetime.datetime.now()
            hour = f"{now.hour}:00"
            for i in bookings:
                if i["time_slot"] == hour:
                    patient_number = i["patient_number"]
                    database_check = parse_json(mongo.db.profile_tocreate.find_one({"patient_number": patient_number}))
                    if database_check != None:
                        payload = {
                            "name": i["name"],
                            "surname": i["surname"],
                            "email": i["email"],
                            "date": i["date"],
                            "time_slot":i["time_slot"],
                            "phone_number": i["phone_number"],
                            "patient_number": i["patient_number"],
                            "profile_complete": True
                        }
                        appointments_array.append(payload)
                    else:
                        payload = {
                            "name": i["name"],
                            "surname": i["surname"],
                            "email": i["email"],
                            "date": i["date"],
                            "time_slot": i["time_slot"],
                            "phone_number": i["phone_number"],
                            "patient_number": i["patient_number"],
                            "profile_complete": True

                        }
                        appointments_array.append(payload)
            status = 200
            data[0]["bookings"] = appointments_array
            resp = {"data":data,"message":"Appointmenst Retieved","status":status}
            return jsonify(resp),status
        else:
            resp = {"message":"No Appointments For Today","status":status}
    except Exception as e:
        status = 400
        resp={"message":f"{e}","status":status}
        print("ERORR (retieve_appointments route)--->",e)
    return jsonify(resp),status

@app.route("/consultation/retrieve",methods= ["GET"])
def get_all_consultations():
    status  = 200
    resp = {}
    try:
        response = mongo.db.consultation.find()
        if response  != []:
            resp ={"message":"Consultation retrieved ","data":response}
        else:
            status =400
            resp  = {"message":"No consultations available"}
    except Exception as e :
        status = 400
        resp = {"message": f"{e}", "status": status}
        print("ERORR (/consultation/retrieve)--->", e)
    return jsonify(resp),status

@app.route("/create/doctors/note",methods= ["POST"])
def create_docoters_note():
    status  = 200
    resp = {}
    try:
        data  = request.get_json()
       
        doctor_note = data["data"]["note"]
        organisation_name = data["data"]["organisation_name"]
        patient_number = data["data"]["patient_number"]
        if doctor_note !="" and patient_number != "":
                patient_profile =parse_json(mongo.db.patients.find_one({"patient_number": patient_number}))
                doctor_profile =parse_json(mongo.db.doctor.find({}))
                if patient_profile == None:
                    resp = {"message":"ERROR"}
                    return resp
                if doctor_profile == []:
                    resp = {"message": "ERROR"}
                    return resp

                doctor_practise_name = doctor_profile[0]["practise"]["practise_name"]
                doctor_name = doctor_profile[0]["personal"]["surname"]
                doctor_phone_number = doctor_profile[0]["personal"]["phone_number"]
                doctor_email = doctor_profile[0]["personal"]["email"]
                tool = report()
                name = patient_profile["name"]
                surname = patient_profile["surname"]
                full_name = f"{name} {surname}"

                response = tool.make_doctors_note(full_name,organisation_name,doctor_practise_name,patient_number,doctor_name,doctor_note,doctor_phone_number,doctor_email)
                mongo.db.doctors_note_files.insert_one(response)
                resp  ={"message":"Doctors note has been created"}

    except Exception as e :
        status = 400
        resp = {"message": f"{e}", "status": status}
        print("ERORR (/create/doctors/note)--->", e)
    return jsonify(resp),status
@app.route("/doctor/cousultation/create", methods=["POST"])
def consultation_create():
    status = 200
    resp = {}
    try:
        data = request.get_json("data")
        patient_number = data["data"]["patient_number"]
        patient_vitals  = data["data"]["patient_vitals"]
        patient_diagnoisis = data["data"]["patient_diagnoisis"]
        patiet_doctor_note = data["data"]["patiet_doctor_note"]
        follow_up_instruction  = data["data"]["follow_up_instruction"]
        follow_up_message  = data["data"]["follow_up_message"]
        follow_up_date = data["data"]["follow_up_date"]

        print(data)
        if patient_number != "":
            response = mongo.db.patients.find({"patient_number":f"{patient_number}"})
            id  = tools()
            id_number = id.generate_task_id()
            today = datetime.date.today()
            print(today)
            if response != []:
                payload  = {
                "id":1,
                "date":f"{today}",
                "consultation_number":id_number,
                "patient_number" :f"{patient_number}",
                "patient_vitals" :  patient_vitals,
                "patient_diagnoisis": patient_diagnoisis,
                "patiet_doctor_note": patiet_doctor_note,

                }
                print(payload)
                mongo.db.consultation.insert_one(payload)
                patient_profile =parse_json(mongo.db.patients.find_one({"patient_number": patient_number}))
                doctor_profile =parse_json(mongo.db.doctor.find({}))
                if patient_profile == None:
                    resp = {"message":"ERROR"}
                    return resp
                if doctor_profile == []:
                    resp = {"message": "ERROR"}
                    return resp

                doctor_practise_name = doctor_profile[0]["practise"]["practise_name"]
                doctor_name = doctor_profile[0]["personal"]["surname"]
                doctor_phone_number = doctor_profile[0]["personal"]["phone_number"]
                doctor_email = doctor_profile[0]["personal"]["email"]
                tool = report()
                name = patient_profile["name"]
                surname = patient_profile["surname"]
                full_name = f"{name} {surname}"
                if patient_diagnoisis["drug_lines"] !=[]: 
                    response = tool.make_patient_percription(patient_diagnoisis["drug_lines"],full_name,patient_number,doctor_practise_name,doctor_name,doctor_phone_number,doctor_email)
                    mongo.db.perscription_files.insert_one(response)
                today = datetime.date.today()
                appointment_response =parse_json(mongo.db.appointment.find_one({"date":f"{today}"}))
                if appointment_response != None:
                    array  = appointment_response["bookings"]
                    for i in array:
                        if i["patient_number"]== patient_number:
                            array.pop(array.index(i))
                    payload = {"$set": {
                        "bookings": array,
                    }
                    }
                    mongo.db.appointment.update_one({"date": f"{today}"}, payload)


                resp  = {"message":"Consultaion complete"}
                if follow_up_instruction  != ""  :
                    f_id_number = id.generate_task_id()
                    follow_up_payload ={
                        "follow_up_number":f_id_number,
                        "consultaion_number":id_number,
                        "patient_number":f"{patient_number}",
                        "follow_up_message":follow_up_message,
                        "follow_up_date":follow_up_date,
                        "follow_up_instruction": follow_up_instruction
                    }
                    mongo.db.followup.insert_one(follow_up_payload)
                    resp ={"message":"Consultaion complete and follow up scheduled"}
            else:
                status = 400
                resp = {"messsage": "Patient was not found", "status": status}

    except Exception as e:
        status = 400
        resp = {"message": f"{e}", "status": status}
        print("ERORR (/doctor/cousultation/create)--->", e)
    return  jsonify(resp),status




@app.route("/service/retrieve",methods=["GET"])
def service_retrieve():
    status =200
    resp = {}
    try:
        database_check = parse_json(mongo.db.doctor.find())
        services = database_check[0]
        services =  services["practise"]["sevices"]
        status = 200 
        resp = {"data":services}
        
    except Exception as e :
        status = 400
        resp = {"message": f"{e}", "status": status}
        print("ERORR (/service/retrieve)--->", e)
    return  jsonify(resp),status

@app.route("/service/add",methods=["POST"])
def service_add():
    status =200
    resp = {}
    try:
        data = request.get_json("data")
        service_array = data["data"]["service_array"]
        if service_array !=  []:
            database_check = parse_json(mongo.db.doctor.find())
            data= database_check[0]
            services =  data["practise"]["sevices"]
            for i in service_array :
                services.append(i)
            payload = {"$set": {
                        "practise":{
                            "practise_name":data["practise"]["practise_name"],
                            "working_hours":data["practise"]["working_hours"],
                            "sevices": services,
                            "number_of_employees":data["practise"]["number_of_employees"],
                        }
                        
                    }
                    }
            response  = mongo.db.doctor.update_one({"id": 1}, payload)
            status = 200 
            resp = {"message":"Services updated"}
        
    except Exception as e :
        status = 400
        resp = {"message": f"{e}", "status": status}
        print("ERORR (/service/add)--->", e)
    return  jsonify(resp),status
@app.route("/followup/retrieve",methods=["GET"])
def followup_retrieve():
    status =200
    resp = {}
    try:
        data = parse_json(mongo.db.followup.find())
        if data != []:
            resp  = {"message":"success","data":data}
        else:
            resp ={"message":"There are no Follow Up"}
    except Exception as e :
        status = 400
        resp = {"message": f"{e}", "status": status}
        print("ERORR (/followup/retrieve)--->", e)
    return  jsonify(resp),status

@app.route("/followup/delete",methods=["DELETE"])
def followup_create():
    status = 200
    resp = {}
    try:
        data  = request.get_json("data")
        follow_up_number = data["data"]["follow_up_number"]
        if follow_up_number != "":
            database_check  = parse_json(mongo.db.followup.find({"follow_up_number":follow_up_number}))
            print(database_check)
            if database_check != []:
                mongo.db.followup.delete_one({"follow_up_number":follow_up_number})
                resp = {"message":"Follow up deleted"}
            else:
                status = 401
                resp = {"message":"Follow up not found"}
        else:
            status  = 400
            resp = {"message":"No follow_up_number"}


    except Exception as e:
        status = 400
        resp = {"message": f"{e}", "status": status}
        print("ERORR (/followup/delete)--->", e)
    return  jsonify(resp),status

@app.route("/doctor/cousultation/edit",methods=["PUT"])
def consultation_edit():
    status = 200
    resp = {}
    try:
        data= request.json_get("data")
        patient_name = data["data"]["patient_name"]
        patient_diagnoisis= data["data"]["patient_diagnoisis"]
        patiet_doctor_note = data["data"]["patiet_doctor_note"]
        if patient_name != "":
            response = mongo.db.patients.find({"name",f"{patient_name}"})
            if response != None:
                print("hello")

            else:
                status= 400
                resp = {"messsage":"patient was not found","status":status}

    except Exception as e:
        status= 400
        resp={"message":f"{e}","status":status}
        print("ERORR (consultation_edit route)--->",e)





@app.route("/forgot/passowrd1",methods=["POST"])
def forgot_password1():
    status =200
    resp = {}
    try:
        print("fogotten password")
        data = request.get_json("data")
        email = data["data"]["email"]
        if email != "":
            teacher = mongo.db.teacher.find_one({"email":f"{email}"})
            admin = mongo.db.admin.find_one({ "email":f"{email}"})
            student = mongo.db.student.find_one({"email":f"{email}"})
            domestic = mongo.db.domestic.find_one({"email":f"{email}"})
            security = mongo.db.security.find_one({"email":f"{email}"})
            visitor = mongo.db.visitor.find_one({"email":f"{email}"})
            if parse_json(teacher) != None:
                print("Teacher")
                data = parse_json(teacher)
                email = data["email"]
                name = data["name"]
                user_number  = data["staff_number"]
                password = data["password"]
                #checinking if code has been made
                #getting a token
                q1 = tools()
                number = q1.random_number_creation()
                if number != "":
                    q1.emailing_services(email,name,user_number,"forgot_password","","",number)
                    forgot_user_payload={
                        "name":f"{name}",
                        "email":f"{email}",
                        "user_number":f"{user_number}",
                        "verification_number":f"{number}",
                        "password":f"{password}"
                    }
                    mongo.db.forgot.insert_one(forgot_user_payload)
                    status = 200
                    resp ={"meassage":"email sent","token":"active"}
                else:
                    print("Verification number was not created")
                    status = 400
                    resp = {"message":"Verification number was not created","status":status}

            if parse_json(admin) != None:
                print("Admin")
                data = parse_json(admin)
                email = data["email"]
                name = data["name"]
                user_number  = data["admin_number"]
                password = data["password"]
                #getting a token
                q1 = tools()
                number = q1.random_number_creation()
                if number != "":
                    q1.emailing_services(email,name,user_number,"forgot_password","","",number)
                    forgot_user_payload={
                        "name":f"{name}",
                        "email":f"{email}",
                        "user_number":f"{user_number}",
                        "verification_number":f"{number}",
                        "password":f"{password}"

                    }
                    mongo.db.forgot.insert_one(forgot_user_payload)
                    status = 200
                    resp ={"meassage":"email sent","token":"active"}
                else:
                    print("Verification number was not created")
                    status = 400
                    resp = {"message":"Verification number was not created","status":status}

            if parse_json(student) != None:
                print("Student")
                data = parse_json(student)
                email = data["email"]
                name = data["name"]
                user_number  = data["student_number"]
                password = data["password"]
                #getting a token
                q1 = tools()
                number = q1.random_number_creation()
                if number != "":
                    q1.emailing_services(email,name,user_number,"forgot_password","","",number)
                    forgot_user_payload={
                        "name":f"{name}",
                        "email":f"{email}",
                        "user_number":f"{user_number}",
                        "verification_number":f"{number}",
                        "password":f"{password}"
                    }
                    mongo.db.forgot.insert_one(forgot_user_payload)
                    status = 200
                    resp ={"meassage":"email sent","token":"active"}
                else:
                    print("Verification number was not created")
                    status = 400
                    resp = {"message":"Verification number was not created","status":status}

            if parse_json(security) != None:
                print("Security")
                data = parse_json(security)
                email = data["email"]
                name = data["name"]
                user_number  = data["staff_number"]
                password = data["password"]
                #getting a token
                q1 = tools()
                number = q1.random_number_creation()
                if number != "":
                    q1.emailing_services(email,name,user_number,"forgot_password","","",number)
                    forgot_user_payload={
                        "name":f"{name}",
                        "email":f"{email}",
                        "user_number":f"{user_number}",
                        "verification_number":f"{number}",
                        "password":f"{password}"
                    }
                    mongo.db.forgot.insert_one(forgot_user_payload)
                    status = 200
                    resp ={"meassage":"email sent","token":"active"}
                else:
                    print("Verification number was not created")
                    status = 400
                    resp = {"message":"Verification number was not created","status":status}

            if parse_json(domestic) != None:
                print("Domestic")
                data = parse_json(domestic)
                email = data["email"]
                name = data["name"]
                user_number  = data["staff_number"]
                password = data["password"]
                print(name)
                #getting a token
                q1 = tools()
                number = q1.random_number_creation()
                print(number)
                if number != "":
                    q1.emailing_services(email,name,user_number,"forgot_password","","",number,"")
                    forgot_user_payload={
                        "name":f"{name}",
                        "email":f"{email}",
                        "user_number":f"{user_number}",
                        "verification_number":f"{number}",
                        "password":f"{password}"
                    }
                    mongo.db.forgot.insert_one(forgot_user_payload)
                    status = 200
                    resp ={"meassage":"email sent","token":"active"}
                else:
                    print("Verification number was not created")
                    status = 400
                    resp = {"message":"Verification number was not created","status":status}

            if parse_json(visitor) != None:
                print("Vistor")
                data = parse_json(visitor)
                email = data["email"]
                name = data["name"]
                user_number  = data["visitor_number"]
                password = data["password"]
                #getting a token
                q1 = tools()
                number = q1.random_number_creation()
                if number != "":
                    q1.emailing_services(email,name,user_number,"forgot_password","","",number)
                    forgot_user_payload={
                        "name":f"{name}",
                        "email":f"{email}",
                        "user_number":f"{user_number}",
                        "verification_number":f"{number}",
                        "password":f"{password}"
                    }
                    mongo.db.forgot.insert_one(forgot_user_payload)
                    status = 200
                    resp ={"meassage":"email sent","token":"active"}
                else:
                    print("Verification number was not created")
                    status = 400
                    resp = {"message":"Verification number was not created","status":status}

        else:
            status = 400
            resp = {"message":"Missing credential","status":status}
    except Exception as e:
        status  = 400
        resp={"message":f"{e}","status":status}
        print("ERORR (/forgot/passowrd1 route)--->",e)
    return jsonify(resp),status


@app.route("/forgot/passoword/send",methods=["POST"])
def forgot_paswword_send():
    status = 200
    resp ={}
    try:
        data = request.get_json("data")
        verification_number = data["data"]["verification_number"]
        if verification_number != "":
            forgort_password_user = mongo.db.forgot.find_one({"verification_number":f"{verification_number}"})
            if parse_json(forgort_password_user) != None:
                data  = parse_json(forgort_password_user)
                database_veri_num = data["verification_number"]
                if verification_number == database_veri_num:
                    email = data["email"]
                    name = data["name"]
                    user_number  = data["user_number"]
                    password  = data["password"]
                    q1 = tools()
                    q1.emailing_services(email,name,user_number,"forgot_password_send","","","",password)
                    mongo.db.forgot.delete_many({"email":f"{email}"})
                    status = 200
                    resp = {"message":"sucess","status":status}
                else:
                    print("verification number incorect not found")
                    status = 400
                    resp = {"message":"verification number incorect not found","response":"false","status":status}

            else:
                print("forgort_password_user not found")
                status = 400
                resp = {"message":"forgort_password_user not found","status":status}

        else:
            print("Data payload is  empty")
            status = 400
            resp = {"message":"Data payload is  empty","status":status}

    except Exception as e:
        status  = 400
        resp={"message":f"{e}","status":status}
        print("ERORR (/forgot/passowrd1 route)--->",e)
    return jsonify(resp),status

# set up practise daily purge functions

@app.route("/end/of/day",methods =["GET"])
def end_of_day():
    status  = 200
    resp  = {}
    try:
        print("purge")

    except Exception as e:
        status  = 400
        resp={"message":f"{e}","status":status}
        print("ERORR (/end/of/day route)--->",e)
    return jsonify(resp),status





if __name__  =="__main__":
    app.run(debug=True)