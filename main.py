import tkinter as tk
from tkinter import ttk
import sys
import datetime as dt
import pandas as pd

def home(message):
    '''creates homepage with fast access to clock in/out'''
    root = tk.Tk()
    root.title('GBP Timesheet')
    root.configure(background='green')
    root.geometry('500x300')

    info = tk.Label(text=message, font='Ariel 10 bold', background='green')
    info.grid(row=0,column=0, pady=(20,10), padx=(10,0))

    l1 = tk.Label(text='Swipe Student ID: ', font='Ariel 14 bold', background='green')
    l1.grid(row=1,column=0, pady=(20,10), padx=(10,0))
    id = tk.Entry(root, width=30)
    id.insert(0, '') # fill string to prefill field
    id.grid(row=1,column=1, pady=(20,10), padx=(0,10))

    button = tk.IntVar()
    b1=tk.Button(root, text='Clock In/ Out', command = lambda: button.set(0), width=15)
    b1.grid(row=2,column=0, pady=10, padx=10)

    b2=tk.Button(root, text='Add Staff', command = lambda: button.set(1), width=15)
    b2.grid(row=2,column=1, pady=10, padx=10)

    b3=tk.Button(root, text='View Staff Hours', command = lambda: button.set(2), width=15)
    #password protect
    b3.grid(row=3,column=0, pady=10, padx=10)

    b4=tk.Button(root, text='Exit', command = lambda: button.set(3), width=15)
    #password protect
    b4.grid(row=3,column=1, pady=10, padx=10)

    b3.wait_variable(button)

    id = id.get()
    root.destroy()
    root.mainloop()
    return button.get(), id

def add_staff(message=''):
    '''add staff to csv'''
    root=tk.Tk()
    root.title('GBP Timesheet: Add New Staff')
    root.configure(background='green')
    root.geometry('500x300')

    info = tk.Label(text=message, font='Ariel 10 bold', background='green')
    info.grid(row=0,column=0, pady=(20,10), padx=(10,0))

    l1 = tk.Label(text='Swipe Student ID: ', font='Ariel 14 bold', background='green')
    l1.grid(row=1,column=0, pady=(20,10), padx=(10,0))
    id = tk.Entry(root, width=30)
    id.insert(0, '') # fill string to prefill field
    id.grid(row=1, column=1, pady=(20,10), padx=(0,10))

    l2 = tk.Label(text='Name on Workday account: ', font='Ariel 14 bold', background='green')
    l2.grid(row=2,column=0, pady=(20,10), padx=(10,0))
    name = tk.Entry(root, width=30)
    name.insert(0, '') # fill string to prefill field
    name.grid(row=2,column=1, pady=(20,10), padx=(0,10))

    button = tk.IntVar()
    b1=tk.Button(root, text='Submit', command = lambda: button.set(0), width=15)
    b1.grid(row=3, column=0, pady=10, padx=10)

    b2=tk.Button(root, text='Exit', command = lambda: button.set(1), width=15)
    b2.grid(row=4, column=0, pady=10, padx=10)

    b3=tk.Button(root, text='Back', command = lambda: button.set(2), width=15)
    b3.grid(row=3, column=1, pady=10, padx=10)

    b1.wait_variable(button)

    if button.get() == 1:
        sys.exit()
    elif button.get() == 2:
        root.destroy()
        return ''

    id = id.get()
    name = name.get()

    staff = pd.read_csv('staff.csv')

    if (id == '') or (name == ''):
        root.destroy()
        return add_staff('Fields cannot be blank')

    if id in staff['student_id'].to_list():
        root.destroy()
        return add_staff('This student id already exists')

    staff.loc[len(staff)] = [id, name, dt.date.today()]
    staff.to_csv('staff.csv', index=False)

    root.destroy()
    return 'Staff Successfully added'

def clock(id, message=''):
    '''add worked hours to time clock'''
    timesheet = pd.read_csv('time.csv')
    timesheet['in'] = pd.to_datetime(timesheet['in'])

    staff = pd.read_csv('staff.csv')

    if id == '':
        return 'ID cannot be blank'
    if id not in staff['student_id'].to_list():
        return 'Invalid ID: Please add staff member'
    
    name = staff[staff['student_id'] == id]['name'].to_list()[0]

    open_entries = timesheet[(timesheet['student_id'] == id) & (timesheet['out'].isna())]

    if open_entries.empty:
        new_row = pd.DataFrame([{'student_id': id,
                                 'name':name,
                                 'in': dt.datetime.now(),
                                 'out': pd.NaT,
                                 'minutes': pd.NaT,
                                 'hours': pd.NaT}])
        timesheet = pd.concat([timesheet, new_row], ignore_index=True)
        timesheet.to_csv('time.csv', index=False)
        return 'Successfully Clocked In'
    else:
        latest_open_index = open_entries['in'].idxmax()
        now = dt.datetime.now()
        timesheet.loc[latest_open_index, 'out'] = now
        minutes = (now - timesheet.loc[latest_open_index, 'in']) / pd.Timedelta(minutes=1)
        timesheet.loc[latest_open_index, 'minutes'] = minutes
        timesheet.loc[latest_open_index, 'hours'] = minutes/60
        timesheet.to_csv('time.csv', index=False)
        return 'Successfully Clocked Out'


def login(message=''):
    '''admin login'''
    password='a'
    root=tk.Tk()
    root.title('GBP Timesheet: Add New Staff')
    root.configure(background='green')
    root.geometry('500x300')

    info = tk.Label(text=message, font='Ariel 10 bold', background='green')
    info.grid(row=0,column=0, pady=(20,10), padx=(10,0))

    l1 = tk.Label(text='Password: ', font='Ariel 14 bold', background='green')
    l1.grid(row=1,column=0, pady=(20,10), padx=(10,0))
    entry = tk.Entry(root, width=30)
    entry.insert(0, '') # fill string to prefill field
    entry.grid(row=1,column=1, pady=(20,10), padx=(0,10))

    button = tk.IntVar()
    b1=tk.Button(root, text='Login', command = lambda: button.set(0), width=15)
    b1.grid(row=2, column=0, pady=10, padx=10)

    b2=tk.Button(root, text='Exit', command = lambda: button.set(1), width=15)
    b2.grid(row=3, column=0, pady=10, padx=10)

    b3=tk.Button(root, text='Back', command = lambda: button.set(2), width=15)
    b3.grid(row=2, column=1, pady=10, padx=10)

    b1.wait_variable(button)

    if button.get() == 1:
        sys.exit()
    elif button.get() == 2:
        root.destroy()
        return ''

    entry = entry.get()
    if entry != password:
        root.destroy()
        return login('Invalid Password')

    root.destroy()
    return view_hours()

def view_hours(message=''):
    '''view staff worked hours given period of dates'''
    root=tk.Tk()
    root.title('GBP Timesheet: Select Dates')
    root.configure(background='green')
    root.geometry('500x300')

    info = tk.Label(text=message, font='Ariel 10 bold', background='green')
    info.grid(row=0,column=0, pady=(20,10), padx=(10,0))

    l1 = tk.Label(text='Start(mm/dd/yyyy): ', font='Ariel 14 bold', background='green')
    l1.grid(row=1,column=0, pady=(20,10), padx=(10,0))
    start = tk.Entry(root, width=30)
    start.insert(0, '') # fill string to prefill field
    start.grid(row=1, column=1, pady=(20,10), padx=(0,10))

    l2 = tk.Label(text='End(mm/dd/yyyy): ', font='Ariel 14 bold', background='green')
    l2.grid(row=2,column=0, pady=(20,10), padx=(10,0))
    end = tk.Entry(root, width=30)
    end.insert(0, '') # fill string to prefill field
    end.grid(row=2,column=1, pady=(20,10), padx=(0,10))

    button = tk.IntVar()
    b1=tk.Button(root, text='Submit', command = lambda: button.set(0), width=15)
    b1.grid(row=3, column=0, pady=10, padx=10)

    b2=tk.Button(root, text='Exit', command = lambda: button.set(1), width=15)
    b2.grid(row=4, column=0, pady=10, padx=10)

    b3=tk.Button(root, text='Logout', command = lambda: button.set(2), width=15)
    b3.grid(row=3, column=1, pady=10, padx=10)

    b1.wait_variable(button)

    if button.get() == 1:
        sys.exit()
    elif button.get() == 2:
        root.destroy()
        return 'Admin Logged Out'

    start = start.get()
    end = end.get()

    #date validation
    try:
        start = dt.datetime.strptime(start, '%m/%d/%Y')
    except:
        root.destroy()
        return view_hours('Invalid Date Format')
    
    try:
        end = dt.datetime.strptime(end, '%m/%d/%Y')
    except:
        root.destroy()
        return view_hours('Invalid Date Format')
    
    if start > end:
        root.destroy()
        return view_hours('Start Must be Earlier than End')

    root.destroy()
    return table(start, end)


def table(start, end):
    '''generates window with table of hours'''
    root=tk.Tk()
    root.title('Worked Hours')
    root.configure(background='green')
    root.geometry('500x1000')

    button = tk.IntVar()
    b1=tk.Button(root, text='Back', command = lambda: button.set(0), width=15)
    b1.grid(row=0, column=0, pady=10, padx=10)

    b2=tk.Button(root, text='Logout', command = lambda: button.set(1), width=15)
    b2.grid(row=0, column=1, pady=10, padx=10)

    b3=tk.Button(root, text='Exit', command = lambda: button.set(2), width=15)
    b3.grid(row=0, column=2, pady=10, padx=10)

    timesheet = pd.read_csv('time.csv')
    timesheet['in'] = pd.to_datetime(timesheet['in'])
    timesheet['out'] = pd.to_datetime(timesheet['out'])

    data = (timesheet[(timesheet['in'] >= start) & (timesheet['out'] <= end)]
            [['student_id','name', 'minutes', 'hours']]
            .groupby('student_id').agg(
                name=('name', 'max'),
                minutes=('minutes', 'sum'),
                hours=('hours', 'sum')
            ))

    tree = ttk.Treeview(root)
    tree["columns"] = list(data.columns)
    tree["show"] = "headings"

    for col in data.columns:
        tree.heading(col, text=col)
        tree.column(col, width=100, anchor="center")

    # Insert rows
    for _, row in data.iterrows():
        tree.insert("", "end", values=list(row))

    tree.grid(row=1,
              column=0,
              columnspan=3,
              padx=10,
              pady=10,
              sticky='nsew')

    b1.wait_variable(button)

    if button.get() == 2:
        sys.exit()
    elif button.get() == 0:
        root.destroy()
        return view_hours()
    elif button.get() == 1:
        root.destroy()
        return 'Admin Logged Out'

def main():
    '''main loop'''
    message=''
    while True:
        state, id = home(message)
        if state == 0:
            message = clock(id)
        elif state == 1:
            message = add_staff()
        elif state == 2:
            message = login()
        elif state == 3:
            sys.exit()

if __name__ == '__main__':
    main()