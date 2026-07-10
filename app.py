from flask import Flask, request, render_template
import joblib
import pandas as pd

app = Flask(
    __name__,
    static_folder='static', 
    static_url_path='/static'
    )

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/bunk-calculator')
def calculator():
    return render_template('bunk-calculator.html')

@app.route('/cgpa-predictor')
def cgpa():
    return render_template('cgpa-predictor.html')

@app.route('/smart-alerts')
def alerts():
    return render_template('smart-alerts.html')

@app.route('/calculate-bunk-status', methods=['POST'])
def calculate_bunk_status():
    total_classes = int(request.form['total_classes'])
    classes_attended = int(request.form['classes_attended'])
    classes_bunked = int(request.form['classes_bunked'])
    rule = int(request.form['rule'])

    if total_classes <= 0:
        return render_template('bunk-calculator.html', prediction="Total classes must be greater than zero.")
    if (classes_attended + classes_bunked) > total_classes:
        return render_template('bunk-calculator.html', prediction="Attended + Bunked classes cannot exceed total semester classes!", status="DANGER")

    attendance_percentage = (classes_attended / total_classes) * 100
    classes_needed = int(((rule / 100) * total_classes) - classes_attended)

    if classes_needed > (total_classes - classes_attended - classes_bunked):
        status = 'DANGER'
        max = ((classes_attended + (total_classes - classes_attended - classes_bunked)) / total_classes) * 100
        prediction = f"Mathematically Impossible! Even if you attend all the remaining classes, your attendance will be {max:.2f}%."
        return render_template('bunk-calculator.html', status=status, prediction=prediction)
    
    if attendance_percentage > rule:
        max_bunks = int((classes_attended - (rule / 100) * total_classes) / (rule / 100))

        if max_bunks > 0:
            prediction = f"You are safe! You can bunk {max_bunks} more classes."
            status = "SAFE"
        else:
            prediction = "You are safe right now, but don't bunk next the next class!"
            status = "WARNING"

    elif attendance_percentage == rule:
        prediction = "You are right on the edge! Attend the next class (if it is there) to stay safe."
        status = "WARNING"
    
    else:
        status = "DANGER"
        prediction = f"Attendance short! You must attend the next {classes_needed} consecutively to reach the minimum required attendance of {rule}%."

    if classes_needed <= 0:
        status = 'SAFE'
        prediction = f'You are safe! You have reached your target for the semester. You can bunk all the remaining classes (if there)'
        return render_template('bunk-calculator.html', status=status, prediction=prediction)
    
    return render_template('bunk-calculator.html', status=status, prediction=prediction)

@app.route('/predict_cgpa', methods=['POST'])
def predict_cgpa():
    model = joblib.load('cgpa_model.pkl')
    attendance = int(request.form['attendance'])
    study_hours = int(request.form['study_hours'])
    sleep_hours = int(request.form['sleep_hours'])
    stress = int(request.form['stress'])
    marks = int(request.form['marks'])

    data = pd.DataFrame([[study_hours, sleep_hours, attendance, stress, marks]], columns=['study_hours', 'sleep_hours', 'attendance', 'stress_level', 'marks'])

    predictions = model.predict(data)
    cgpa = predictions[0].round(2)

    if cgpa > 7:
        return render_template('cgpa-predictor.html', prediction=cgpa, status='SAFE')
    
    elif 5 <= cgpa <= 7:
        return render_template('cgpa-predictor.html', prediction=cgpa, status='WARNING')
    
    elif cgpa < 5:
        return render_template('cgpa-predictor.html', prediction=cgpa, status='DANGER')
    
    else:
        return render_template('cgpa-predictor.html', prediction=0, status='ERROR OCCURRED')
    
@app.route('/alerts', methods=['POST'])
def alert_msgs():
    social_media = int(request.form['social_media'])
    netflix = int(request.form['netflix'])  
    sleep_hours = int(request.form['sleep_hours'])
    attendance =int(request.form['attendance'])

    distraction = netflix + social_media

    if attendance < 75 or distraction > 6:
        return render_template('smart-alerts.html', status='DANGER', prediction="You are currently in the Danger Zone. Your metrics show you are highly vulnerable to falling behind or getting debarred from exams. Immediate changes to your daily routine are required.", title="🚨 Critical Academic Risk Alert!")
    
    elif attendance > 80 and distraction < 4 and sleep_hours >= 6:
        return render_template('smart-alerts.html', status='SAFE', title="✅ All Clear! Keep it Up", prediction="Excellent job! You are firmly in the Safe Zone. Your attendance is solid, and you are successfully managing your daily digital distractions. You are on track for a strong semester.")
    
    elif 75 <= attendance <= 80 or 4 <= distraction <= 6 or sleep_hours < 5:
        return render_template('smart-alerts.html', status='WARNING', title="⚠️ Warning: Balance Slipping", prediction="You are in the Warning Zone. While you aren't in deep trouble yet, your habits are borderline. Catching up now is easy, but ignoring these numbers will push you into the danger zone.")
    
@app.route('/get-started')
def get_started():
    return render_template('get-started.html')

if __name__ == '__main__':
    app.run(debug=True)
