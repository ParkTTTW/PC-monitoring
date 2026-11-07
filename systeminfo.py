import tkinter as tk
from tkinter import ttk
import platform
import psutil

class SystemMonitorApp(tk.Frame):
    def __init__(self,  parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        
        # 스타일 설정 (깔끔한 UI용)
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        self.create_widgets()
        self.update_dynamic_info()

    def create_widgets(self):
        # 1. 정적 시스템 정보 프레임 (OS, CPU 모델명 등)
        static_frame = ttk.LabelFrame(self, text=" 시스템 기본 정보 ", padding=15)
        static_frame.pack(fill="x", padx=15, pady=10)
        
        # OS 정보
        os_info = f"{platform.system()} {platform.release()} ({platform.architecture()[0]})"
        ttk.Label(static_frame, text=f"운영체제: {os_info}", font=("Malgun Gothic", 10)).pack(anchor="w", pady=2)
        
        # CPU 모델 정보
        cpu_model = platform.processor() or "알 수 없음"
        ttk.Label(static_frame, text=f"프로세서: {cpu_model}", font=("Malgun Gothic", 10)).pack(anchor="w", pady=2)
        
        # 2. 동적 시스템 정보 프레임 (실시간 사용량)
        dynamic_frame = ttk.LabelFrame(self, text=" 실시간 자원 사용량 ", padding=15)
        dynamic_frame.pack(fill="both", expand=True, padx=15, pady=10)
        
        # CPU 사용량 표시
        ttk.Label(dynamic_frame, text="🔲CPU 사용량:", font=("Malgun Gothic", 10, "bold")).pack(anchor="w", pady=(0, 2))
        self.cpu_progress = ttk.Progressbar(dynamic_frame, orient="horizontal", mode="determinate")
        self.cpu_progress.pack(fill="x", pady=(0, 5))
        self.cpu_label = ttk.Label(dynamic_frame, text="0.0%", font=("Malgun Gothic", 9))
        self.cpu_label.pack(anchor="e", pady=(0, 10))
        
        # RAM 사용량 표시
        ttk.Label(dynamic_frame, text="🧮메모리(RAM) 사용량:", font=("Malgun Gothic", 10, "bold")).pack(anchor="w", pady=(0, 2))
        self.ram_progress = ttk.Progressbar(dynamic_frame, orient="horizontal", mode="determinate")
        self.ram_progress.pack(fill="x", pady=(0, 5))
        self.ram_label = ttk.Label(dynamic_frame, text="0.0 GB / 0.0 GB (0.0%)", font=("Malgun Gothic", 9))
        self.ram_label.pack(anchor="e", pady=(0, 10))
        
        # 디스크 사용량 표시
        ttk.Label(dynamic_frame, text="💾디스크(C:) 사용량:", font=("Malgun Gothic", 10, "bold")).pack(anchor="w", pady=(0, 2))
        self.disk_progress = ttk.Progressbar(dynamic_frame, orient="horizontal", mode="determinate")
        self.disk_progress.pack(fill="x", pady=(0, 5))
        self.disk_label = ttk.Label(dynamic_frame, text="0.0 GB / 0.0 GB (0.0%)", font=("Malgun Gothic", 9))
        self.disk_label.pack(anchor="e", pady=(0, 5))

    def update_dynamic_info(self):
        # CPU 사용량 업데이트 (interval=None으로 주어야 GUI가 멈추지 않음)
        cpu_usage = psutil.cpu_percent(interval=None)
        self.cpu_progress['value'] = cpu_usage
        self.cpu_label.config(text=f"{cpu_usage}%")
        
        # RAM 사용량 업데이트
        ram = psutil.virtual_memory()
        ram_used = ram.used / (1024 ** 3) # GB 단위 변환
        ram_total = ram.total / (1024 ** 3)
        self.ram_progress['value'] = ram.percent
        self.ram_label.config(text=f"{ram_used:.1f} GB / {ram_total:.1f} GB ({ram.percent}%)")
        
        # 디스크 사용량 업데이트
        try:
            disk = psutil.disk_usage('/')
            disk_used = disk.used / (1024 ** 3)
            disk_total = disk.total / (1024 ** 3)
            self.disk_progress['value'] = disk.percent
            self.disk_label.config(text=f"{disk_used:.1f} GB / {disk_total:.1f} GB ({disk.percent}%)")
        except Exception:
            self.disk_label.config(text="디스크 정보를 불러올 수 없습니다.")

        # 1초(1000ms)마다 이 함수를 반복 실행하여 실시간 새로고침 구현
        self.after(1000, self.update_dynamic_info)

