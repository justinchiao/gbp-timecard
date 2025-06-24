from flask import Flask, render_template, request, redirect, url_for, make_response
import pandas as pd
import datetime as dt

app = Flask(__name__)
ADMIN_PASSWORD = 'a'

@app.route('/')
def home():
    return render_template('home.html', message=request.args.get('message', ''))

@app.route('/clock', methods=['POST'])
def clock():
    student_id = request.form['student_id']
    staff = pd.read_csv('staff.csv')
    timesheet = pd.read_csv('time.csv')
    timesheet['in'] = pd.to_datetime(timesheet['in'])

    if student_id not in staff['student_id'].values:
        return redirect(url_for('home', message='Invalid ID: Please add staff member'))

    name = staff[staff['student_id'] == student_id]['name'].values[0]
    open_entries = timesheet[(timesheet['student_id'] == student_id) & (timesheet['out'].isna())]

    if open_entries.empty:
        new_row = pd.DataFrame([{
            'student_id': student_id,
            'name': name,
            'in': dt.datetime.now(),
            'out': pd.NaT,
            'minutes': pd.NaT,
            'hours': pd.NaT
        }])
        timesheet = pd.concat([timesheet, new_row], ignore_index=True)
        message = "Successfully Clocked In"
    else:
        idx = open_entries['in'].idxmax()
        now = dt.datetime.now()
        timesheet.loc[idx, 'out'] = now
        minutes = (now - timesheet.loc[idx, 'in']) / pd.Timedelta(minutes=1)
        timesheet.loc[idx, 'minutes'] = minutes
        timesheet.loc[idx, 'hours'] = minutes / 60
        message = "Successfully Clocked Out"

    timesheet.to_csv('time.csv', index=False)
    return redirect(url_for('home', message=message))

@app.route('/add_staff', methods=['GET', 'POST'])
def add_staff():
    if request.method == 'POST':
        student_id = request.form['student_id']
        name = request.form['name']
        staff = pd.read_csv('staff.csv')

        if not student_id or not name:
            return render_template('add_staff.html', message='Fields cannot be blank')

        if student_id in staff['student_id'].values:
            return render_template('add_staff.html', message='This student ID already exists')

        staff.loc[len(staff)] = [student_id, name, dt.date.today()]
        staff.to_csv('staff.csv', index=False)
        return redirect(url_for('home', message='Staff successfully added'))

    return render_template('add_staff.html', message='')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form['password']
        if password != ADMIN_PASSWORD:
            return render_template('login.html', message='Invalid Password')
        resp = make_response(redirect(url_for('view_hours')))
        resp.set_cookie('logged_in', 'true', max_age=60*60)  # 1 hour cookie
        return resp
    return render_template('login.html', message='')

@app.route('/logout')
def logout():
    resp = make_response(redirect(url_for('home')))
    resp.delete_cookie('logged_in')
    return resp

@app.route('/view_hours', methods=['GET', 'POST'])
def view_hours():
    if request.cookies.get('logged_in') != 'true':
        return redirect(url_for('login'))

    if request.method == 'POST':
        if request.form['submit_button'] == 'logout':
            return render_template('home.html', message='Admin Logged Out')

        try:
            start = dt.datetime.strptime(request.form['start'], '%m/%d/%Y')
            end = dt.datetime.strptime(request.form['end'], '%m/%d/%Y')
            if start > end:
                raise ValueError
        except:
            return render_template('view_hours.html', message='Invalid date format or range')

        return redirect(url_for('table',
                                start=start.strftime('%Y-%m-%d'),
                                end=end.strftime('%Y-%m-%d')))

    return render_template('view_hours.html', message='')

@app.route('/table', methods=['GET', 'POST'])
def table():
    if request.cookies.get('logged_in') != 'true':
        return redirect(url_for('login'))

    if request.method == 'POST':
        if request.form['submit_button'] == 'logout':
            return render_template('home.html', message='Admin Logged Out')
        
    start = pd.to_datetime(request.args['start'])
    end = pd.to_datetime(request.args['end'])
    timesheet = pd.read_csv('time.csv')
    timesheet['in'] = pd.to_datetime(timesheet['in'])
    timesheet['out'] = pd.to_datetime(timesheet['out'])

    df = timesheet[(timesheet['in'] >= start) & (timesheet['out'] <= end)]
    data = df.groupby('student_id').agg({
        'name': 'max',
        'minutes': 'sum',
        'hours': 'sum'
    }).reset_index()

    return render_template('table.html', data=data.to_dict(orient='records'))

if __name__ == '__main__':
    app.run(debug=True)
