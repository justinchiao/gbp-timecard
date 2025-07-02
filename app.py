import datetime as dt
from flask import Flask, render_template, request, redirect, url_for, make_response
from waitress import serve
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

app = Flask(__name__)
ADMIN_PASSWORD = 'a'

# google sheets setup
scope = ['https://www.googleapis.com/auth/spreadsheets']
creds = Credentials.from_service_account_file('cred.json', scopes=scope)
client = gspread.authorize(creds)

staff_key='1i2zzjM0DNfcaXMsKsivN99xPn9hgJrvaw08S8_oRO-E'
time_key='1PYtJKFJh1OCno3YHexR17fMXM3txfAQZwJPf_64-SM0'

@app.route('/')
def home():
    return render_template('home.html', message=request.args.get('message', ''))

@app.route('/clock', methods=['POST'])
def clock():
    student_id = request.form['student_id']
    staff_sheet = client.open_by_key(staff_key).sheet1
    time_sheet = client.open_by_key(time_key).sheet1
    staff = pd.DataFrame(staff_sheet.get_all_records())
    print(staff)
    timesheet = pd.DataFrame(time_sheet.get_all_records())
    print(timesheet)
    timesheet['in'] = pd.to_datetime(timesheet['in'])

    if student_id not in staff['student_id'].values:
        return redirect(url_for('home', message='Invalid ID: Please add staff member'))

    name = staff[staff['student_id'] == student_id]['name'].values[0]
    open_entries = timesheet[(timesheet['student_id'] == student_id) & (timesheet['out'] == '')]
    print(open_entries)

    if open_entries.empty:
        time_sheet.append_row([student_id, name, dt.datetime.now().strftime('%m/%d/%Y, %H:%M:%S'),'','','',])
        message = "Successfully Clocked In"
    else:
        idx = open_entries['in'].idxmax() + 2
        print(idx)
        minutes = (dt.datetime.now() - timesheet.loc[idx-2, 'in']) / pd.Timedelta(minutes=1)
        hours = minutes / 60

        time_sheet.update_cell(idx, 4, dt.datetime.now().strftime('%m/%d/%Y, %H:%M:%S'))
        time_sheet.update_cell(idx, 5, minutes)
        time_sheet.update_cell(idx, 6, hours)
        message = "Successfully Clocked Out"

    return redirect(url_for('home', message=message))

@app.route('/add_staff', methods=['GET', 'POST'])
def add_staff():
    if request.method == 'POST':
        student_id = request.form['student_id']
        name = request.form['name']
        staff_sheet = client.open_by_key(staff_key).sheet1
        staff = pd.DataFrame(staff_sheet.get_all_records())

        if not student_id or not name:
            return render_template('add_staff.html', message='Fields cannot be blank')

        if student_id in staff['student_id'].values:
            return render_template('add_staff.html', message='This student ID already exists')

        staff_sheet.append_row([student_id, name, dt.datetime.now().strftime('%m/%d/%Y, %H:%M:%S')])
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
    time_sheet = client.open_by_key(time_key).sheet1
    timesheet = pd.DataFrame(time_sheet.get_all_records())
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
    serve(app, host='127.0.0.1', port=5000)
