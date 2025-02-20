from flask import *
import os
from werkzeug.utils import secure_filename
import label_image

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from datetime import datetime
import image_fuzzy_clustering as fem
import os
import secrets
from PIL import Image
from flask import url_for, current_app

from flask import Flask, request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

from models import db, Patient, HealthMetrics, HeartRisk
 
def load_image(image):
    text = label_image.main(image)
    return text

app = Flask(__name__)
model = None

UPLOAD_FOLDER = os.path.join(app.root_path ,'static','img')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:/Users/Sahyadri/Downloads/Heart Disease Project 0/patients.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)


with app.app_context():
    db.create_all()

def prepare_image(image, target):
    # if the image mode is not RGB, convert it
    if image.mode != "RGB":
        image = image.convert("RGB")

    # resize the input image and preprocess it
    image = image.resize(target)
    image = img_to_array(image)
    image = np.expand_dims(image, axis=0)
    image = imagenet_utils.preprocess_input(image)

    # return the processed image
    return image






class MyHandler(FileSystemEventHandler):

    def _init_(self, observer):
        self.observer = observer

    def on_modified(self, event):
        print("Restarting Flask app...")
        print("hekp")
        # os.system("pkill -f 'python my_app.py'")  # Kill the Flask app process
         # Restart the Flask app
        self.observer.stop()
        os.system("python app1.py &") 



UPLOAD_FOLDER = os.path.join(app.root_path ,'static','img')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/')
@app.route('/first')
def first():
    return render_template('first.html')

 
  

    
@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/chart')
def chart():
    return render_template('chart.html')

@app.route('/upload')
def upload():
    return render_template('index1.html')

@app.route('/success', methods=['POST'])
def success():
    if request.method == 'POST':
        i=request.form.get('cluster')
        f = request.files['file']
        fname, f_ext = os.path.splitext(f.filename)
        original_pic_path=save_img(f, f.filename)
        destname = 'em_img.jpg'
        fem.plot_cluster_img(original_pic_path,i)
    return render_template('success.html')

def save_img(img, filename):
    picture_path = os.path.join(current_app.root_path, 'static/images', filename)
    # output_size = (300, 300)
    i = Image.open(img)
    # i.thumbnail(output_size)
    i.save(picture_path)

    return picture_path



@app.route('/index')
def index():
    return render_template('index.html')
    

# if request.method == 'POST':
#         aadhaar_number = request.form['aadhaarNumber']
#         name=request.form["name"]
#         age=request.form["age"]
#         if len(aadhaar_number) == 12:
#             new_patient = Patient(aadhaar_number=aadhaar_number,age=age,name=name)
#             db.session.add(new_patient)
#             db.session.commit()
#             return "Patient Information Added Successfully"
#         else:
#             return "Invalid Aadhaar Number", 400
#     return render_template('index.html')

@app.route("/check_aadhaar",methods=['POST'])
def checkAadhar():
    aadhaar_number=request.form["aadhaar_number"]
    # aadhaar_number="789654125639"
    patient = Patient.query.filter_by(aadhaar_number=aadhaar_number).first()
    if len(aadhaar_number) != 12:
        return jsonify(success=False,message="Invalid Aadhar Number\n Must be 12 digits"),200
    patient = Patient.query.filter_by(aadhaar_number=aadhaar_number).first()
    if not patient:
        return jsonify(success=False,message="The given Aadhar number is not present in the database"),200
    health_metrics = [{
    "date": metric.date.strftime('%Y-%m-%d %H:%M:%S'),
    "bmi": metric.bmi,
    "sbp": metric.sbp,
    "dbp": metric.dbp,
    "haemoglobin": metric.haemoglobin
    } 
    for metric in patient.health_metrics.order_by(HealthMetrics.date.asc())]  # Changed to asc()

    heart_risks = [{
        "date": risk.date.strftime('%Y-%m-%d %H:%M:%S'),
        "risk_level": risk.risk_level
    }
    for risk in patient.heart_risks.order_by(HeartRisk.date.asc())]  # Changed to asc()

    # Now, the most recent record will be the last item in each list
    most_recent_heart_risk = heart_risks[-1] if heart_risks else {}  # Getting the last item
    return jsonify(success=True,
                   patient_name=patient.name, 
                   dob=patient.dob.strftime('%Y-%m-%d'), 
                   health_metrics=health_metrics, 
                   heart_risks=heart_risks, 
                   most_recent_heart_risk=most_recent_heart_risk),200

@app.route('/new_patient', methods=['POST'])
def new_patient():
    aadhaar_number = request.form['aadhaar_number']
    dob_str = request.form["age"]
    dob = datetime.strptime(dob_str, '%Y-%m-%d')
    name=request.form["name"] 
    risk_level=request.form["riskAssessment"]
    patient = Patient.query.filter_by(aadhaar_number=aadhaar_number).first()
    if(patient):
         return jsonify(success=False, message="Patient's Aadhaar already present in the database"),200
     # Handle age if provided
    print("New Patient")
    if len(aadhaar_number) == 12:
        new_patient = Patient(aadhaar_number=aadhaar_number, dob=dob,name=name)
        db.session.add(new_patient)
        db.session.commit()
        new_risk = HeartRisk(risk_level=risk_level, patient_id=new_patient.id)
        db.session.add(new_risk)
        db.session.commit()
        return jsonify(success=True, message="Patient Information added successfully.")
    else:
        return jsonify(success=False, message="Invalid Aadhaar Number."), 200

@app.route('/add_data',methods=['POST','GET'])
def add_patient_data():
    p1 = {
        "aadhaar_number": "789654125639",
        "BMI": ["19.3", "19.4", "19.2", "19.5"],
        "Sbp": ["114", "90", "95", "90"],  # Removed 'mm hg' for simplicity
        "DBP": ["80", "79.8", "80.2", "79.7"],
        "Hbg": ["13.6", "13.3", "13.5", "13.7"],
        "Heart attack risk": ["High risk", "mild risk", "low risk", "completely healthy"],
        "Date": ["23/01/2024", "19/02/2024", "14/03/2024", "03/04/2024", "30/04/2024"],
        "Heart attack risk": [2, 1, 0, 0]
    }
    p2={
    "aadhaar_number": "989654125639",
    "id":["1B12"],
    "BMI":["20.3","20.4","20.2","20.5"],
    "Sbp":["130 ","129.3","128.4 ","125 "],
    "DBP":["90 ","88.3 ","89 ","89.2 "],
    "Hbg":["14.6 ","14.3 ","13.5 ","13.7 "],
   "Heart attack risk":[2,1,0,0,1,0],
   "Date": ["23/01/2024","19/02/2024","14/03/2024","3/04/2024","30/04/2024"]
}

    # Check if patient exists
    patient = Patient.query.filter_by(aadhaar_number=p2['aadhaar_number']).first()
    if not patient:
        return "Patient not found", 200

    # Convert string risk levels to integers or enums as required
    date_format = "%d/%m/%Y"
    for i in range(len(p2['BMI'])):
        # Create HealthMetrics entry
        date = datetime.strptime(p2['Date'][i], date_format)
        health_metric = HealthMetrics(
            patient_id=patient.id,
            date=date,
            bmi=float(p2['BMI'][i]),
            sbp=float(p2['Sbp'][i]),
            dbp=float(p2['DBP'][i]),
            haemoglobin=float(p2['Hbg'][i])
        )
        db.session.add(health_metric)

        # Create HeartRisk entry
        heart_risk = HeartRisk(
            patient_id=patient.id,
            date=date,
            risk_level=p2['Heart attack risk'][i]
        )
        db.session.add(heart_risk)

    # Commit the session to save all data
    db.session.commit()

    return "Patient data added successfully", 200




@app.route('/update_patient', methods=['POST'])
def update_patient():
    aadhaar_number = request.form['aadhaar_number']
    risk_level=request.form["riskAssessment"]
    print("Risk Level ",risk_level)
    patient = Patient.query.filter_by(aadhaar_number=aadhaar_number).first()
    print("Update Patient")
    if patient:
        new_risk = HeartRisk(risk_level=risk_level, patient_id=patient.id)
        db.session.add(new_risk)
        db.session.commit()
        return jsonify(success=True, message="Patient Information updated successfully.")
    else:
        return jsonify(success=False, message="Patient not found with provided Aadhaar ID."), 200


@app.route('/patients',methods=['GET'])
def list_patients():
    all_patients = Patient.query.all()
    patients_list = [{
        'id': patient.id,
        'name': patient.name,
        'dob': patient.dob.strftime('%Y-%m-%d'),  # Assuming dob is a date object
        'aadhaar_number': patient.aadhaar_number
    } for patient in all_patients]

    return jsonify(patients_list)


@app.route('/base')
def base():
    return render_template('base.html')

# @app.route('/index')
# def index():
#     return "Hello, World!"




@app.route('/predict', methods=['GET', 'POST'])
def upload1():
    if request.method == 'POST':
        # Get the file from post request
        f = request.files['file']
        file_path = secure_filename(f.filename)
        f.save(file_path)
        # Make prediction
        result = load_image(file_path)
        result = result.title()
        d = {"1":" → Low Risk",
	        '2':"  → Mild Risk ",
            '3':"  → Elevated Risk",
            '4':"  → High Risk",
            "0":"  → No Risk You are Healthy!"}
        result = d[result]
        #result2 = result+d[result]
        #result = [result]
        #result3 = d[result]        
        print(result)
        #print(result3)
        os.remove(file_path)
        return result
        #return result3
        return None

if __name__ == '__main__':
    # event_handler = MyHandler()
    # observer = Observer()
    # observer.schedule(MyHandler(observer), '.', recursive=True)
    # observer.start()
    app.run(debug=True,port=5050)