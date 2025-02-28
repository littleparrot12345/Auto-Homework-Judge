from check_answer import check_answer
from config import version, autosave_interval
from tkinter import *
from pickle import load, dump
from threading import Thread
from time import sleep

data=None
running=True

def data_load():
    global data
    try:
        with open("data.ahj", "rb") as f:
           data=load(f)
    except:
        print("无法加载数据。正在重置。")
        data={}

def data_save():
    try:
        with open("data.ahj", "wb") as f:
            dump(data, f)
    except:
        print("无法保存数据。")

def on_project_select(event):
    pass

def project_list_flush():
    global project_listbox, data
    project_listbox.delete(0, END)
    for project in data.get('projects', []):
        project_listbox.insert(END, project)

def on_project_add():
    global root
    subwindow=Toplevel(root)
    subwindow.title("添加项目")
    subwindow.geometry("400x225")
    subwindow.iconbitmap("icon.ico")

    Label(subwindow, text="项目名称：").grid(row=0, column=0, padx=10, pady=10, sticky='w')
    entry_project_name = Entry(subwindow)
    entry_project_name.grid(row=0, column=1, padx=10, pady=10, sticky='ew')

    Label(subwindow, text="答案：").grid(row=1, column=0, padx=10, pady=10, sticky='nw')
    text_answer = Text(subwindow, height=5, width=20)
    text_answer.grid(row=1, column=1, padx=10, pady=10, sticky='nsew')

    def on_confirm():
        global data
        project_name = entry_project_name.get()
        answer = text_answer.get("1.0", END).strip()
        data.setdefault('projects', []).append(project_name)
        data.setdefault('project_answers',{})
        data['project_answers'][project_name]=answer
        project_list_flush()
        subwindow.destroy()

    btn_confirm = Button(subwindow, text="确定", command=on_confirm)
    btn_confirm.grid(row=2, column=0, columnspan=2, pady=10)

    subwindow.grid_rowconfigure(1, weight=1)
    subwindow.grid_columnconfigure(1, weight=1)


def auto_save():
    global running
    count=0
    while running:
        if count==autosave_interval:
            count=0
            data_save()
        count+=1
        sleep(1)

def main():
    global data, running, root, project_listbox
    data_load()
    auto_save_thread=Thread(target=auto_save)
    auto_save_thread.start()

    root=Tk()
    root.title("Auto Homework Judge "+version)
    root.geometry("800x450")
    root.iconbitmap("icon.ico")

    for i in range(2):
        root.grid_rowconfigure(i, weight=1)
        root.grid_columnconfigure(i, weight=1)

    project_frame=Frame(root)
    project_frame.grid(row=0, column=0, sticky="nsew")
    project_label=Label(project_frame, text="项目")
    project_label.pack()
    project_listbox=Listbox(project_frame,selectmode=SINGLE)
    project_listbox.pack()
    
    project_list_flush()

    project_add_button=Button(project_frame, text="添加项目", command=on_project_add)
    project_add_button.pack()

    homework_frame=Frame(root)
    homework_frame.grid(row=0, column=1, sticky="nsew")

    log_frame=Frame(root)
    log_frame.grid(row=1, column=0, columnspan=2, sticky="nsew")

    problem_frame=Frame(root)
    problem_frame.grid(row=1, column=1, sticky="nsew")

    root.mainloop()

    running=False
    data_save()

if __name__ == "__main__":
    main()