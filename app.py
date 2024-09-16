from flask import Flask, render_template, request, redirect, url_for, session
from pymongo import MongoClient

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Connect to MongoDB
client = MongoClient('mongodb+srv://aditya001patidar:Myoutlook%402021@cloudapplication.6sh78.mongodb.net/')
db = client['DiabetesHealthcareApp']

# Collections
patients_collection = db['patients']
doctors_collection = db['doctors']
admins_collection = db['admins']
analysis_results_collection = db['Analysis Results']  # Added the correct collection for predicted values

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    user_type = request.form['user_type']

    if user_type == 'patient':
        user = patients_collection.find_one({"username": username, "password": password})
        if user:
            session['username'] = username
            session['user_type'] = 'patient'
            return redirect(url_for('patient_dashboard'))
    
    elif user_type == 'doctor':
        user = doctors_collection.find_one({"username": username, "password": password})
        if user:
            session['username'] = username
            session['user_type'] = 'doctor'
            return redirect(url_for('doctor_dashboard'))
    
    elif user_type == 'admin':
        user = admins_collection.find_one({"username": username, "password": password})
        if user:
            session['username'] = username
            session['user_type'] = 'admin'
            return redirect(url_for('admin_dashboard'))
    
    return render_template('login.html', error="Invalid credentials")

@app.route('/patient_dashboard')
def patient_dashboard():
    if 'username' in session and session['user_type'] == 'patient':
        user = patients_collection.find_one({"username": session['username']})
        user_data = {
            'latest_sugar_level': round(user.get('latest_sugar_level', 0), 2),
            'avg_sugar_level': round(user.get('avg_sugar_level', 0), 2),
            'latest_systolic': round(user.get('latest_systolic', 0), 2),
            'latest_diastolic': round(user.get('latest_diastolic', 0), 2),
            'avg_systolic': round(user.get('avg_systolic', 0), 2),
            'avg_diastolic': round(user.get('avg_diastolic', 0), 2),
            'latest_cholesterol': round(user.get('latest_cholesterol', 0), 2),
            'avg_cholesterol': round(user.get('avg_cholesterol', 0), 2),
            'latest_bmi': round(user.get('latest_bmi', 0), 2),
            'avg_bmi': round(user.get('avg_bmi', 0), 2),
            'latest_hba1c': round(user.get('latest_hba1c', 0), 2),
            'avg_hba1c': round(user.get('avg_hba1c', 0), 2),
        }

        suggestions = {}  # Add logic to fetch suggestions

        return render_template('patient_dashboard.html', user=user, user_data=user_data, suggestions=suggestions)
    return redirect(url_for('home'))

@app.route('/doctor_dashboard', methods=['GET', 'POST'])
def doctor_dashboard():
    if 'username' in session and session['user_type'] == 'doctor':
        doctor = doctors_collection.find_one({"username": session['username']})
        patients = doctor.get('patients', [])  # Retrieve the list of patients for the logged-in doctor
        
        if request.method == 'POST':
            patient_id = request.form.get('patient_id')
            # Find patient info for the entered patient_id in the list of patients
            patient = next((p for p in patients if p['patient_id'] == patient_id), None)
            search = True
        else:
            patient = None
            search = False

        return render_template('doctor_dashboard.html', doctor=doctor, patients=patients, patient=patient, search=search)
    return redirect(url_for('home'))

# New route for displaying patient IDs to the doctor
@app.route('/doctor_patients')
def doctor_patients():
    if 'username' in session and session['user_type'] == 'doctor':
        # Fetch the doctor object from the database using the session username
        doctor = doctors_collection.find_one({"username": session['username']})
        
        # Fetch the list of patients associated with this doctor
        patients = doctor.get('patients', [])

        # Pass both doctor and patients data to the template
        return render_template('doctor_patients.html', doctor=doctor, patients=patients)

    # Redirect to home if the session is invalid or user is not a doctor
    return redirect(url_for('home'))


@app.route('/admin_dashboard')
def admin_dashboard():
    if 'username' in session and session['user_type'] == 'admin':
        # Fetch admin-specific data
        user = admins_collection.find_one({"username": session['username']})
        # Replace the mock data with actual logic to fetch from the database
        total_users = 10000  # Example placeholder value
        active_sessions = 1  # Example placeholder value
        system_health = 'Good'  # Example placeholder value
        return render_template('admin_dashboard.html', user=user, total_users=total_users, active_sessions=active_sessions, system_health=system_health)
    return redirect(url_for('home'))

@app.route('/suggestions')
def suggestions():
    if 'username' in session and session['user_type'] == 'patient':
        # Fetch user information
        user = patients_collection.find_one({"username": session['username']})
        
        if user:
            # Use the username to fetch the predicted values from the Analysis Results collection
            predicted_data = analysis_results_collection.find_one({"patient_id": user.get('username')})
            
            if predicted_data:
                predicted_data = {
                    'sugar_level': predicted_data.get('predicted_sugar_level', 'N/A'),
                    'blood_pressure': predicted_data.get('predicted_blood_pressure', 'N/A'),
                    'cholesterol': predicted_data.get('predicted_cholesterol', 'N/A'),
                    'bmi': predicted_data.get('predicted_bmi', 'N/A'),
                    'hba1c': predicted_data.get('predicted_hba1c', 'N/A'),
                    'guidance_sugar_level': predicted_data.get('Guidance_SugarLevel', 'No guidance available'),
                    'guidance_blood_pressure': predicted_data.get('Guidance_BloodPressure', 'No guidance available'),
                    'guidance_cholesterol': predicted_data.get('Guidance_Cholesterol', 'No guidance available'),
                    'guidance_bmi': predicted_data.get('Guidance_BMI', 'No guidance available'),
                    'guidance_hba1c': predicted_data.get('Guidance_HbA1c', 'No guidance available')
                }
            else:
                predicted_data = {
                    'sugar_level': 'N/A',
                    'blood_pressure': 'N/A',
                    'cholesterol': 'N/A',
                    'bmi': 'N/A',
                    'hba1c': 'N/A',
                    'guidance_sugar_level': 'No guidance available',
                    'guidance_blood_pressure': 'No guidance available',
                    'guidance_cholesterol': 'No guidance available',
                    'guidance_bmi': 'No guidance available',
                    'guidance_hba1c': 'No guidance available'
                }
        
            return render_template('suggestions.html', user=user, predicted_data=predicted_data)
    
    return redirect(url_for('home'))

@app.route('/insurance')
def insurance():
    if 'username' in session and session['user_type'] == 'patient':
        # Fetch user information
        user = patients_collection.find_one({"username": session['username']})
        
        if user:
            # Fetch the insurance information for the user
            insurance_data = user.get('insurance', 'N/A')
            
            return render_template('insurance.html', user=user, insurance_data=insurance_data)
    
    return redirect(url_for('home'))


@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('user_type', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
