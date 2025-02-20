from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    dob = db.Column(db.Date, nullable=False) 
    aadhaar_number=db.Column(db.String(12),nullable=False)
    health_metrics = db.relationship('HealthMetrics', backref='patient', lazy='dynamic')
    heart_risks = db.relationship('HeartRisk', backref='patient', lazy='dynamic')

class HealthMetrics(db.Model):
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), primary_key=True)
    date = db.Column(db.DateTime, primary_key=True, default=datetime.utcnow)
    bmi = db.Column(db.Float)
    sbp = db.Column(db.Integer)  # Systolic Blood Pressure
    dbp = db.Column(db.Integer)  # Diastolic Blood Pressure
    haemoglobin = db.Column(db.Float)

class HeartRisk(db.Model):
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), primary_key=True)
    date = db.Column(db.DateTime, primary_key=True, default=datetime.utcnow)
    risk_level = db.Column(db.Integer)