import pandas as pd
import tkinter as tk

def home():
    root = tk.Tk()
    root.title("GBP Timesheet")
    root.configure(background="green")

    l1 = tk.Label(text='ID: ')
    l1.grid(row=0,column=0)
    id = tk.Entry(root)
    id.insert(0, "") # fill string to prefill field
    id.grid(row=0,column=1)

    var = tk.IntVar()
    b1=tk.Button(root, text='submit', command = lambda: var.set(1))
    b1.grid(row=8,column=1)
    b1.wait_variable(var)
    
    id = id.get()
    root.destroy()
    root.mainloop()
    return id

def main():
    id=home()
    print(id)
    # time = pd.read_csv('timesheet.csv')
    # print(time)

if __name__ == "__main__":
    main()