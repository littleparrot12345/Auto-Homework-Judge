from check_answer import check_answer
from config import version, autosave_interval, api_key
from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
from pickle import load, dump
from threading import Thread
from time import sleep
from pathlib import Path
from datetime import datetime
from json import loads

data = None
running = True
current_homework=None
current_project=None
current_problem=None

def is_ascii(c):
    return ord(c) < 128

def info(msg):
    msg = "[INFO] [" + datetime.now().strftime("%H:%M:%S") + "] " + msg
    try:
        cnt=0
        for c in msg:
            cnt+=1
            cnt+=not is_ascii(c)
            # if cnt>39:
            #    log_text.insert(END, "\n")
            #    cnt=0
            log_text.insert(END, c)
        log_text.insert(END, "\n")
    except:
        pass
    print(msg)

def warn(msg):
    msg = "[WARN] [" + datetime.now().strftime("%H:%M:%S") + "] " + msg
    try:
        cnt=0
        for c in msg:
            cnt+=1
            cnt+=not is_ascii(c)
            # if cnt>39:
            #     log_text.insert(END, "\n")
            #     cnt=0
            log_text.insert(END, c)
        log_text.insert(END, "\n")
    except:
        pass
    print(msg)

def data_load():
    global data
    try:
        with open("data.ahj", "rb") as f:
            data = load(f)
        info("数据加载成功。")
    except Exception as e:
        warn(f"无法加载数据。正在重置。错误信息: {str(e)}")
        data = {}

def data_save():
    try:
        with open("data.ahj", "wb") as f:
            dump(data, f)
        info("数据保存成功。")
    except Exception as e:
        warn(f"无法保存数据。错误信息: {str(e)}")

def homework_list_flush():
    global current_project, homework_listbox, data
    homework_listbox.delete(0, END)
    if current_project is not None:
        data.setdefault('project_homeworks', {})
        data['project_homeworks'].setdefault(current_project, [])
        data.setdefault('project_homework_status', {})
        data['project_homework_status'].setdefault(current_project, {})
        for homework in data['project_homeworks'][current_project]:
            homework_filename = Path(homework).name
            if len(homework_filename) > 20:
                homework_filename = homework_filename[:20] + "..."
            homework_listbox.insert(END, homework_filename + ("[已批改]" if \
                data['project_homework_status'][current_project].get(homework, False) else \
                    "[未批改]"))
        info(f"作业列表已刷新，当前项目: {current_project}")

def on_project_select(event):
    if not project_listbox.curselection():
        return
    global current_project
    current_project = project_listbox.get(project_listbox.curselection())
    info(f"已选择项目: {current_project}")
    homework_list_flush()

def project_list_flush():
    global project_listbox, data
    project_listbox.delete(0, END)
    for project in data.get('projects', []):
        project_listbox.insert(END, project)
    info("项目列表已刷新")

def on_project_add():
    global root
    subwindow = Toplevel(root)
    subwindow.title("添加项目")
    subwindow.geometry("400x225")
    subwindow.iconbitmap("icon.ico")

    Label(subwindow, text="项目名称：").grid(row=0, column=0, padx=10, pady=10, sticky='w')
    entry_project_name = Entry(subwindow)
    entry_project_name.grid(row=0, column=1, padx=10, pady=10, sticky='ew')

    Label(subwindow, text="题目数量：").grid(row=1, column=0, padx=10, pady=10, sticky='w')
    entry_problem_count = Entry(subwindow)
    entry_problem_count.grid(row=1, column=1, padx=10, pady=10, sticky='ew')

    Label(subwindow, text="答案：").grid(row=2, column=0, padx=10, pady=10, sticky='nw')
    text_answer = Text(subwindow, height=5, width=20)
    text_answer.grid(row=2, column=1, padx=10, pady=10, sticky='nsew')

    def on_confirm():
        global data
        project_name = entry_project_name.get()
        answer = text_answer.get("1.0", END).strip()
        if not project_name:
            warn("项目名称不能为空")
            messagebox.showwarning("警告", "项目名称不能为空。")
            return
        if project_name in data.get('projects', []):
            warn("项目名称已存在")
            messagebox.showwarning("警告", "项目名称已存在。")
            return
        if not entry_problem_count.get().isdigit():
            warn("题目数量必须为数字")
            messagebox.showwarning("警告", "题目数量必须为数字。")
            return
        data.setdefault('projects', []).append(project_name)
        data.setdefault('project_answers', {})
        data['project_answers'][project_name] = answer
        data.setdefault('project_problem_count', {})
        data['project_problem_count'][project_name] = int(entry_problem_count.get())
        info(f"项目 '{project_name}' 已添加")
        project_list_flush()
        subwindow.destroy()

    btn_confirm = Button(subwindow, text="确定", command=on_confirm)
    btn_confirm.grid(row=3, column=0, columnspan=2, pady=10)

    subwindow.grid_rowconfigure(1, weight=1)
    subwindow.grid_columnconfigure(1, weight=1)

def auto_save():
    global running
    count = 0
    while running:
        if count == autosave_interval:
            count = 0
            data_save()
        count += 1
        sleep(1)

def on_project_del():
    global project_listbox, data, current_project
    selected_index = project_listbox.curselection()
    if not selected_index:
        messagebox.showwarning("警告", "请先选择一个项目。")
        return
    selected_index = int(selected_index[0])
    project_name = project_listbox.get(selected_index)
    if messagebox.askyesno("删除项目", 
        "确定要删除项目“{}”吗？\n它将永远消失（真的很久）！".format(project_name)):
        current_project = None
        homework_list_flush()
        del data['projects'][selected_index]
        del data['project_answers'][project_name]
        del data['project_homeworks'][project_name]
        info(f"项目 '{project_name}' 已删除")
        project_list_flush()

def problem_list_flush():
    problem_listbox.delete(0, END)
    if current_homework is not None:
        for i in range(1,data['project_problem_count'][current_project]+1):
           problem_listbox.insert(END, str(i))
        data.setdefault('project_homework_status', {}).setdefault(current_project, {})\
            .setdefault(current_homework_idx, False)
    if current_homework is not None and data['project_homework_status'][current_project]\
        [data['project_homeworks'][current_project][current_homework_idx]]:
        problem_judge_button.config(text="重新开始批改所有题目", command=on_problem_judge)
        count = 0
        for x in data['project_results'][current_project]\
            [data['project_homeworks'][current_project][current_homework_idx]]:
            if x['status']=='AC':
                count += 1
        problem_analysis_label.config(text=\
                f"正确题目数：{count}（共{data['project_problem_count'][current_project]}题）")
    else:
        problem_judge_button.config(text="开始批改所有题目", command=on_problem_judge)
        problem_analysis_label.config(text="未批改")

def on_homework_select(event):
    if not homework_listbox.curselection():
        return
    global current_homework, problem_listbox, current_homework_idx, problem_judge_button, \
        problem_analysis_label
    current_homework_idx = homework_listbox.curselection()[0]
    current_homework = homework_listbox.get(homework_listbox.curselection())
    info(f"已选择作业: {current_homework}")
    problem_list_flush()

def on_homework_add():
    global data, current_project
    if not current_project:
        messagebox.showwarning("警告", "请先选择一个项目。")
        return
    file_paths = filedialog.askopenfilenames(title="选择作业文件", 
                                           filetypes=[("图片文件",
                                                        "*.png;*.jpg;*.jpeg;*.bmp"),
                                                          ("所有文件", "*.*")])
    if not file_paths:
        messagebox.showwarning("警告", "请先选择至少一个作业文件。")
        return
    for file_path in file_paths:
        if file_path not in data['project_homeworks'][current_project]:
            data['project_homeworks'][current_project].append(file_path)
            info(f"作业文件 '{file_path}' 已添加到项目 '{current_project}'")
    homework_list_flush()

def on_homework_del():
    global data, current_project, current_homework
    if not current_project:
        messagebox.showwarning("警告", "请先选择一个项目。")
        return
    selected_index = homework_listbox.curselection()
    if not selected_index:
        messagebox.showwarning("警告", "请先选择一个作业。")
        return
    selected_index = int(selected_index[0])
    if messagebox.askyesno("删除作业", 
        "确定要删除作业“{}”吗？\n它将永远消失（真的很久）！".format(data['project_homeworks'][current_project][selected_index])):
        deleted_homework = data['project_homeworks'][current_project][selected_index]
        del data['project_homeworks'][current_project][selected_index]
        info(f"作业 '{deleted_homework}' 已从项目 '{current_project}' 中删除")
        current_homework = None
        homework_list_flush()
        problem_list_flush()

def on_problem_select(event):
    global current_problem, problem_listbox, current_problem_idx
    if not problem_listbox.curselection():
        return
    current_problem = problem_listbox.get(problem_listbox.curselection())
    current_problem_idx=problem_listbox.curselection()
    info(f"已选择问题: {current_problem}")

def on_problem_judge():
    global current_homework, current_project, data, problem_judge_button,\
        current_homework_idx
    if not current_homework:
        messagebox.showwarning("警告", "请先选择一个作业。")
        return
    problem_judge_button.config(state=DISABLED)
    current_homework=data['project_homeworks'][current_project][current_homework_idx]
    info(f"正在判断作业 '{current_homework}' 的答案")
    answer = data['project_answers'][current_project]
    problem_count = data['project_problem_count'][current_project]
    result_json = check_answer(current_homework, answer, problem_count, logger=info)
    try:
        result = loads(result_json)
        data.setdefault('project_results', {}).setdefault(current_project, {})
        data.setdefault('project_homework_status').setdefault(current_project, {})
        data['project_results'][current_project][current_homework] = result
        data['project_homework_status'][current_project][current_homework] = True
        homework_list_flush()
        problem_list_flush()
        info(f"作业 '{current_homework}' 的答案已判断")
    except Exception as e:
        warn(f"作业 '{current_homework}' 的答案判断失败: {e}")
        messagebox.showerror("错误", f"作业 '{current_homework}' 的答案判断失败: \n{e}")
        raise e
    finally:
        problem_judge_button.config(state=NORMAL)

def on_problem_check():
    global data, root, current_homework, current_project, current_homework_idx
    if not current_problem:
        messagebox.showwarning("警告", "请先选择一个题目。")
        return
    current_homework=data['project_homeworks'][current_project][current_homework_idx]
    data.setdefault('project_homework_status', {}).setdefault(current_project, {})\
        .setdefault(current_homework, False)
    if not data['project_homework_status'][current_project][current_homework]:
        messagebox.showwarning("警告", "请先判断答案。")
        return
    subwindow = Toplevel(root)
    subwindow.title("题目详情")
    subwindow.geometry("400x225")
    subwindow.iconbitmap("icon.ico")
    Label(subwindow, text="状态："+\
          data['project_results'][current_project][current_homework][int(current_problem)-1]\
            ["status"]).grid(
              row=0, column=0, sticky="e")
    Label(subwindow, text="详情："+\
          data['project_results'][current_project][current_homework][int(current_problem)-1]\
            ["analysis"]).grid(
              row=1, column=0, sticky="e")

def main():
    if not api_key:
        messagebox.showerror("错误", "请先在 config.py 中设置 API 密钥。")
        return
    global data, running, root, project_listbox, homework_listbox, log_text,\
          problem_listbox, problem_judge_button, problem_analysis_label
    data_load()
    auto_save_thread = Thread(target=auto_save)
    auto_save_thread.start()

    root = Tk()
    root.title("Auto Homework Judge " + version)
    root.geometry("1200x675")
    root.iconbitmap("icon.ico")

    for i in range(2):
        root.grid_rowconfigure(i, weight=1)
        root.grid_columnconfigure(i, weight=1)

    project_frame = Frame(root)
    project_frame.grid(row=0, column=0, sticky="nsew")
    project_label = Label(project_frame, text="项目")
    project_label.pack()
    project_listbox = Listbox(project_frame, selectmode=SINGLE)
    project_listbox.pack()
    project_listbox.bind('<<ListboxSelect>>', on_project_select)
    project_list_flush()
    project_add_button = Button(project_frame, text="添加项目", command=on_project_add)
    project_add_button.pack()
    project_del_button = Button(project_frame, text="删除项目", command=on_project_del)
    project_del_button.pack()

    homework_frame = Frame(root)
    homework_frame.grid(row=0, column=1, sticky="nsew")
    homework_label = Label(homework_frame, text="作业")
    homework_label.pack()
    homework_listbox = Listbox(homework_frame, selectmode=SINGLE, width=40)
    homework_listbox.pack()
    homework_listbox.bind('<<ListboxSelect>>', on_homework_select)
    homework_list_flush()
    homework_add_button = Button(homework_frame, text="添加作业", command=on_homework_add)
    homework_add_button.pack()
    homework_del_button = Button(homework_frame, text="删除作业", command=on_homework_del)
    homework_del_button.pack()

    log_frame = Frame(root)
    log_frame.grid(row=1, column=0, sticky="nsew")
    log_label = Label(log_frame, text="日志")
    log_label.pack()
    log_text = Text(log_frame, height=10, wrap=WORD, width=50)
    log_text.pack()
    log_debug_button = Button(log_frame, text="Debug", command=lambda: print("data=",data))
    log_debug_button.pack()

    problem_frame = Frame(root)
    problem_frame.grid(row=1, column=1, sticky="nsew")
    problem_label = Label(problem_frame, text="题目")
    problem_label.pack()
    problem_listbox = Listbox(problem_frame, selectmode=SINGLE, width=40)
    problem_listbox.pack()
    problem_listbox.bind('<<ListboxSelect>>', on_problem_select)
    problem_judge_button = Button(problem_frame, text="开始批改所有题目", 
                                  command=on_problem_judge)
    problem_judge_button.pack()
    problem_check_button = Button(problem_frame, text="查看题目详情", command=on_problem_check)
    problem_check_button.pack()
    problem_analysis_label = Label(problem_frame, text="未批改")
    problem_analysis_label.pack()

    data.setdefault("info",False)
    data.setdefault("lincense",False)
    data.setdefault("warning",False)
    if data["info"] == False:
        messagebox.showinfo("信息", 
                            """本软件是一个开源项目。
项目地址：https://github.com/littleparrot12345/Auto-Homework-Judge""")
        data["info"] = True
    if data["lincense"] == False:
        messagebox.showwarning("警告", 
                               """本软件使用GNU 通用公共许可证v3.0，请确保您已经阅读并同意该许可证。
许可证内容详见LICENSE文件。""")
        data["lincense"] = True
    if data["warning"] == False:
        messagebox.showwarning("警告", 
                               "在批改过程中未响应是正常的，请耐心等待。")
        data["warning"] = True

    root.mainloop()

    running = False
    data_save()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        running = False
        data_save()
        messagebox.showerror("错误", "程序运行时发生错误：\n" + str(e))
        raise e