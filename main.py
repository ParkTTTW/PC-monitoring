"""
PC 클리너 - 임시 파일 스캔 및 삭제 (Windows 전용)

[구현 범위]
1. 임시 파일 및 캐시 정리   <- 스캔/삭제 기능 구현 완료 (기능 테스트 완료 *심볼릭 링크 테스트는 추후에)
2. 시작 프로그램 관리       <- 활성화, 비활성화 기능 구현 완료
3. 디스크 및 메모리 최적화  <-  프로세스 종료 기능 구현 완료 (기능 테스트 완료)
(레지스트리 청소는 위험도가 높아 구현 제외)
"""
import sys,os
if sys.stdout is None:
    sys.stdout = open(os.devnull, "w")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w")

import psutil
import tkinter as tk
import speedtest
from tkinter import ttk
from process import ProcessInfo
from startup import StartupManager
from systeminfo import SystemMonitorApp
from cleaning import CleanProcess

class MainApplication(tk.Tk):
    
    def __init__(self):
        super().__init__()
        self.title("SystemManager")
        self.geometry("600x500")
        self.resizable(False, False)
        self.style = ttk.Style()
        self.style.theme_use("clam")
                
        
        # 모든 프레임이 배치될 기본 컨테이너 생성
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        
        # 각 화면(프레임) 인스턴스를 저장할 딕셔너리
        self.frames = {}
        
        # 사용할 화면 클래스들을 등록
        for PageClass in (SystemMonitorApp, ProcessInfo, StartupManager, CleanProcess):
            page_name = PageClass.__name__
            # parent=container, controller=self(MainApplication)로 전달
            frame = PageClass(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self._create_navigation_bar()
    
    def _create_navigation_bar(self):
        """상단에 고정되어 화면 전환을 도와주는 메뉴 버튼 영역입니다."""
        nav_frame = tk.Frame(self, bg = "#e0e0e0",  padx=5, pady=5)
        nav_frame.pack(side="top", fill="x")

        # 시스템 정보 모니터링 화면으로 가기
        btn_system = ttk.Button(nav_frame, text="💻 시스템 정보 모니터링", 
                                 command=lambda: self.show_frame("SystemMonitorApp"))
        btn_system.pack(side="left", padx=5)
        
        # 프로세스 관리 화면으로 가기
        btn_process = ttk.Button(nav_frame, text="⚙️ 프로세스 관리", 
                                 command=lambda: self.show_frame("ProcessInfo"))
        btn_process.pack(side="left", padx=5)
        
        # 시작프로그램 관리 화면으로 가기
        btn_startup = ttk.Button(nav_frame, text="🚀 시작프로그램 관리", 
                                 command=lambda: self.show_frame("StartupManager"))
        btn_startup.pack(side="left", padx=5)   


        # 클리너화면으로 가기
        btn_cleaning = ttk.Button(nav_frame, text="🧹 클리너", 
                                         command=lambda: self.show_frame("CleanProcess"))
        btn_cleaning.pack(side="left", padx=5)
        
            
        # 처음에 보여줄 화면 지정
        self.show_frame("SystemMonitorApp")  # 초기 화면은 시스템 정보 모니터링 화면으로 설정
        
    def show_frame(self, page_name):
        """지정한 이름의 프레임을 맨 위로 올려 화면에 표시합니다."""
        frame = self.frames[page_name]
        frame.tkraise()

if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()




class SystemInfo:
    def __init__(self):
        pass

    # CPU 정보
    def get_cpu(self):
        cpu_percent = psutil.cpu_percent(interval=0.1, percpu=False)
        cpu_core = psutil.cpu_count()
        return cpu_percent, cpu_core

    # 메모리 정보 MB
    def get_memory(self):
        virtual_memory = psutil.virtual_memory()
        total_memory = virtual_memory.total // (1024*1024)
        available_memory = virtual_memory.available // (1024*1024)
        used_memory = total_memory - available_memory
        return total_memory, available_memory, used_memory

    # 디스크 정보 GB
    def get_disk(self):
        disk_usage = psutil.disk_usage('/')
        total_disk_space = disk_usage.total // (1024*1024*1024)
        used_disk_space = disk_usage.used // (1024*1024*1024)
        free_disk_space = disk_usage.free // (1024*1024*1024)
        return total_disk_space, used_disk_space, free_disk_space

    # 네트워크 속도 측정
    def speed_test(self):
        st = speedtest.Speedtest()
        download_speed = st.download() / (1024 * 1024)  # Mbps
        upload_speed = st.upload() / (1024 * 1024)      # Mbps
        return download_speed, upload_speed




