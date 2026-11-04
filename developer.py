import os
import psutil
import tkinter as tk
from tkinter import ttk, messagebox

# get process information
# systemRoot 안에만
# name 예외처리
# allowRoot 만

OS_ROOTS = os.environ.get("SystemRoot").lower()

PROTECTED_NAMES = {
    "system", "registry", "smss.exe", "csrss.exe", "wininit.exe",
    "winlogon.exe", "services.exe", "lsass.exe",
    "explorer.exe", "dwm.exe", "sihost.exe", "ctfmon.exe",
    "taskhostw.exe", "fontdrvhost.exe",
    "svchost.exe", "runtimebroker.exe", "searchhost.exe",
    "msmpeng.exe", "securityhealthservice.exe", "code.exe", "python.exe"
}

ALLOWED_ROOTS = [
    ("ProgramFiles",      ""),
    ("ProgramFiles(x86)", ""),
    ("LOCALAPPDATA",      "Programs"),
]

allowed = []
for proc in psutil.process_iter(["pid", "name", "exe", 'memory_info','create_time']):
    target_root = proc.info["exe"]
    if target_root is None:
        continue
    if str(target_root).lower().startswith(OS_ROOTS) :
        continue
    for env_var, sub_path in ALLOWED_ROOTS:
        try:
            safe_path = os.path.join(os.environ.get(env_var), sub_path)
            if str(target_root).lower().startswith(safe_path.lower()):
                name = proc.info["name"] or ""
                if name == "":
                    continue
                if name.lower() not in PROTECTED_NAMES:
                    pid = proc.info["pid"]
                    # 메모리 정보를 MB 단위로 변환
                    memory = round(proc.info['memory_info'].rss / (1024 * 1024), 1)
                    create_time = proc.info['create_time']
                    allowed.append((pid, name, memory, create_time))
        except Exception as e:
            print(f"Error processing {proc.info['name']}: {e}")




window = tk.Tk()

tree = ttk.Treeview(window, columns=("pid", "name","memory","create_time"), show="headings")
tree.pack(padx=10, pady=10)

tree.heading("pid", text="PID")
tree.heading("name", text="프로세스 이름")
tree.heading("memory", text="메모리 (MB)")
tree.heading("create_time", text="생성 시간")

tree.column("pid", width=80, anchor=tk.CENTER)
tree.column("name", width=250, anchor=tk.W)
tree.column("memory", width=120, anchor=tk.E)


tree['displaycolumns'] = ('pid', 'name', 'memory')  # create_time 열은 숨기기


for pid, name, memory, create_time in allowed:
    tree.insert("", tk.END, values=(pid, name, memory, create_time))

def get_tree_selection():
  selected_item = tree.selection()  # 선택된 행의 ID 리스트
  if selected_item:
    item_values = tree.item(selected_item[0])["values"]
    print(f"선택된 데이터: {item_values}")


#btn = tk.Button(window, text="행 데이터 가져오기", command=lambda: print(tree.selection())) # lamda(예약)를 해야 지금 선택된 행의 데이터를 가져올 수 있음. 그냥 print(tree.selection()) 하면 print() 바로 호출 실행
btn = tk.Button(window, text="행 데이터 가져오기", command=get_tree_selection)
btn.pack()

window.mainloop()

  