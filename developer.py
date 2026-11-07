from curses import window
import os
import psutil
import tkinter as tk
from tkinter import ttk, messagebox

# get process information
# systemRoot 안에만
# name 예외처리
# allowRoot 만
class ProcessInfo(tk.Frame):

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        
        
        self.tree = ttk.Treeview(self, columns=("pid", "name","memory","create_time"), show="headings")
        self.tree.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

        self.tree.heading("pid", text="PID")
        self.tree.heading("name", text="프로세스 이름")
        self.tree.heading("memory", text="메모리 (MB)")
        self.tree.heading("create_time", text="생성 시간")

        self.tree.column("pid", width=80, anchor=tk.CENTER)
        self.tree.column("name", width=250, anchor=tk.W)
        self.tree.column("memory", width=120, anchor=tk.E)


        self.tree['displaycolumns'] = ('pid', 'name', 'memory')  # create_time 열은 숨기기

        btn = tk.Button(self, text="행 데이터 가져오기", command=lambda: print(self.tree.item(self.tree.selection()[0])["values"])) # lamda(예약)를 해야 지금 선택된 행의 데이터를 가져올 수 있음. 그냥 print(self.tree.selection()) 하면 print() 바로 호출 실행
        btn.pack(side=tk.LEFT, padx=5)

        refresh_btn = tk.Button(self, text="🔄새로고침", command=self.refresh_tree)
        refresh_btn.pack(side=tk.LEFT, padx=5)

        terminate_btn = tk.Button(self, text="작업 끝내기", command=lambda: self.terminate_process(self.get_tree_selection()[0], 
                                                                self.get_tree_selection()[1], self.get_tree_selection()[3]), fg="red")
        
        terminate_btn.pack(side=tk.LEFT, padx=5)



        self.refresh_tree()  # 초기 로드



    def get_allowed_processes(self):
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
        return allowed

    def refresh_tree(self):
        """현재 실행 중인 프로세스 목록을 가져와 표를 갱신합니다."""
        # 기존 목록 삭제
        for item in self.tree.get_children():
            self.tree.delete(item)

        # 프로세스 정보 수집 및 추가
        for pid, name, memory, create_time in self.get_allowed_processes():
            self.tree.insert("", tk.END, values=(pid, name, memory, create_time))





    def get_tree_selection(self):
      selected_item = self.tree.selection()  # 선택된 행의 ID 리스트
      if selected_item:
        item_values = self.tree.item(selected_item[0])["values"]
        selected_pid = item_values[0]  # PID 값
        selected_name = item_values[1]  # 프로세스 이름 값 
        selected_memory = item_values[2]  # 메모리 값
        selected_create_time = item_values[3]  # 생성 시간 값

        return selected_pid, selected_name, selected_memory, selected_create_time



    def terminate_process(self, pid, expected_name, expected_ctime):
        try:
            proc = psutil.Process(pid)  # 프로세스 객체 생성
            proc_name = str(proc.name())
            proc_ctime = str(proc.create_time())
            if expected_name.lower() != proc_name.lower() or expected_ctime != proc_ctime:
                messagebox.showerror("오류", "프로세스 정보가 일치하지 않습니다. 종료를 취소합니다.")
                return
            proc.terminate()  # 프로세스 종료
            messagebox.showinfo("성공", f"프로세스(PID: {pid})가 종료되었습니다.")
            # 목록 갱신
            self.refresh_tree()
        except Exception as e:
            messagebox.showerror("오류", f"프로세스 종료 중 오류 발생: {e}")

if __name__ == "__main__":
    ProcessInfo()



  