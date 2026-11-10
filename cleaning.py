import os
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox
# 임시 파일 및 폴더 정리 스크립트

class CleanProcess(tk.Frame):
    # 정리 대상 목록: (환경변수 이름, 그 아래 하위 경로)
    # 경로를 직접 적지 않고 환경변수로 조합하므로 사용자명이나 PC가 달라도 동작함
    def __init__(self, parent, controller):
        
        super().__init__(parent)
        self.controller = controller
        self.CACHE_TARGETS = [
            ("TEMP",         ""),                                          # 사용자 임시 폴더
            ("LOCALAPPDATA", r"Google\Chrome\User Data\Default\Cache"),    # Chrome 캐시
            ("LOCALAPPDATA", r"Microsoft\Edge\User Data\Default\Cache"),   # Edge 캐시
            ("LOCALAPPDATA", r"Microsoft\Windows\INetCache"),              # 인터넷 임시 파일
        ]
    
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TLabel", font=("맑은 고딕", 12))                   # 모든 Label
        self.style.configure("TLabelframe.Label", font=("맑은 고딕", 12, "bold"))  # 프레임 제목

        
        self.file_frame = ttk.LabelFrame(self, text="📄임시파일", padding=12)
        self.file_frame.pack(fill="x", padx=10, pady=10)
        self.file_frame.columnconfigure(1, weight=1)
        self.dir_frame = ttk.LabelFrame(self, text="📁디렉토리", padding=12)
        self.dir_frame.pack(fill="x", padx=10, pady=10)
        self.dir_frame.columnconfigure(1, weight=1)

        ttk.Label(self.file_frame, text="파일 수").grid(row=0, column=0, sticky="w", pady=3)
        self.file_count_label = ttk.Label(self.file_frame, text="-")
        self.file_count_label.grid(row=0, column=1, sticky="e", pady=3)


        ttk.Label(self.file_frame, text="총 용량").grid(row=1, column=0, sticky="w", pady=3)
        self.file_size_label = ttk.Label(self.file_frame, text="-")
        self.file_size_label.grid(row=1, column=1, sticky="e", pady=3)
        
        ttk.Label(self.dir_frame, text="디렉토리 수").grid(row=0, column=0, sticky="w", pady=3)
        self.dir_count_label = ttk.Label(self.dir_frame, text="-")
        self.dir_count_label.grid(row=0, column=1, sticky="e", pady=3)
        

        ttk.Label(self.dir_frame, text="총 용량").grid(row=1, column=0, sticky="w", pady=3)
        self.dir_size_label = ttk.Label(self.dir_frame, text="-")
        self.dir_size_label.grid(row=1, column=1, sticky="e", pady=3)

        self.refresh()        

        refresh_btn = tk.Button(self, text="🔄새로고침", command=self.refresh_with_message)
        refresh_btn.pack(side=tk.LEFT, padx=5)
        
        delete_btn = tk.Button(
                            self,
                            text="🗑️정리",
                            command=self.start_cleaning,
                            bg="#d9534f",              # 배경: 빨간색
                            fg="white",                # 글자: 흰색
                            activebackground="#c9302c",  # 누르고 있을 때 배경 (조금 더 진한 빨강)
                            activeforeground="white",    # 누르고 있을 때 글자
                            font=("맑은 고딕", 11, "bold"),
                            
                            padx=12, pady=4,)
        delete_btn.pack(side=tk.LEFT, padx=5)
    def refresh_with_message(self):
        self.refresh()
        messagebox.showinfo("완료", "새로고침이 완료되었습니다.")
    def refresh(self):
        file_count, file_size, dir_count, dir_size = self.scan_directory()

        self.file_count_label.config(text=f"{file_count} 개")
        self.file_size_label.config(text=f"{file_size} MB")
        self.dir_count_label.config(text=f"{dir_count} 개")
        self.dir_size_label.config(text=f"{dir_size} MB")

    def start_cleaning(self):
        """임시 파일 및 폴더를 삭제하는 메서드입니다."""
        # 사용자에게 확인 메시지 표시
        confirm = messagebox.askyesno("확인", "정말로 임시 파일과 폴더를 삭제하시겠습니까?")
        if confirm:
            # 안내 창 띄우기
            win = tk.Toplevel(self)
            win.title("정리 중")
            win.geometry("250x80")
            tk.Label(win, text="삭제 중입니다...").pack(expand=True)
            win.update()   # 삭제 시작 전에 창을 먼저 화면에 그림
            self.delete_file_contents(dry_run=False)
            win.destroy()
            self.refresh()
            messagebox.showinfo("완료", "임시 파일과 폴더가 삭제되었습니다.")
            


    # 스캔 기능: 지정한 폴더 안의 파일과 폴더를 조사하여 통계를 출력한다.
    def scan_directory(self):
        file_total_count = 0
        file_total_size = 0
        dir_total_count = 0
        dir_total_size = 0
        # 메인 실행부: 정리 대상 경로를 하나씩 순회
        for env_var, sub_path in self.CACHE_TARGETS:
            scan_path = os.path.join(os.environ.get(env_var), sub_path)  # 환경변수 값 + 하위 경로로 전체 경로 조합
            print(f"Scanning: {scan_path}")
            if not os.path.isdir(scan_path):
                print(f"경로(폴더)가 존재하지 않음: {scan_path}")
                continue  # 경로가 없으면 다음 대상으로 넘어감
        
        
            with os.scandir(scan_path) as it:
                temp = list(it)  # 폴더 안의 항목을 리스트로 한 번에 저장

                # --- 집계용 변수 ---
                file_count = 0        # 파일 개수
                dir_count = 0         # 폴더 개수
                filesize_total = 0    # 파일 총 용량 (KB)
                dirsize_total = 0     # 폴더 항목 자체의 용량 (KB, 폴더 안의 내용물 크기는 미포함)
                extension_names = []  # 발견된 확장자 목록 (중복 제외)

                for entry in temp:
                    try:
                        # 심볼릭 링크는 가리키는 원본을 건드릴 위험이 있으므로 가장 먼저 검사해서 건너뜀
                        if entry.is_symlink():
                            continue

                        # 파일: 개수, 용량, 확장자 집계
                        elif entry.is_file():
                            file_count += 1
                            filesize_total += entry.stat().st_size / (1024*1024)  # 바이트 -> MB

                            # 확장자 추출 (앞의 점 제거, 소문자로 통일)
                            extension = (os.path.splitext(entry.name)[1][1:]).lower()
                            if extension == '':
                                extension = "unknown"  # 확장자가 없는 파일의 표시용 이름

                            if extension not in extension_names:
                                extension_names.append(extension)

                        # 폴더: 개수와 폴더 항목 자체의 크기만 집계
                        elif entry.is_dir():
                            dir_count += 1
                            dirsize_total += entry.stat().st_size / (1024*1024)  # 바이트 -> MB

                    # 스캔 중 파일이 사라졌거나 접근이 거부된 경우: 해당 항목만 건너뛰고 계속 진행
                    except OSError as e:
                        print(f"Error accessing {entry.name}: {e}")
                print(file_count)
            file_total_count += file_count
            file_total_size += filesize_total
            dir_total_count += dir_count
            dir_total_size += dirsize_total

        return round(file_total_count,2), round(file_total_size,2), round(dir_total_count,2), round(dir_total_size,2)

    # 삭제 기능: 지정한 폴더 안의 모든 파일과 하위 폴더를 삭제한다. (링크/정션은 건드리지 않음)
    # topdown=True를 쓰는 이유: 상위 폴더부터 탐색해야 링크/정션 폴더를 만났을 때
    # dirs에서 제거해 그 내부로 내려가지 않게 막을 수 있기 때문
    # (topdown=False는 하위 폴더를 먼저 탐색하므로 이런 차단이 불가능함)
    def delete_file_contents(self,dry_run):
        
        for env_var, sub_path in self.CACHE_TARGETS:
            scan_path = os.path.join(os.environ.get(env_var), sub_path)  # 환경변수 값 + 하위 경로로 전체 경로 조합
            print(f"Scanning: {scan_path}")
            if not os.path.isdir(scan_path):
                print(f"경로(폴더)가 존재하지 않음: {scan_path}")
                continue  # 경로가 없으면 다음 대상으로 넘어감
            safe_dirs = []   # 삭제해도 안전한 폴더 경로 모음
            safe_files = []  # 삭제해도 안전한 파일 경로 모음
            # 1단계: 삭제 대상 수집 (이 단계에서는 아무것도 지우지 않음)
            for root, dirs, files in os.walk(scan_path, topdown=True):  # 상위 폴더 -> 하위 폴더 순으로 탐색
                for dirname in dirs[:]:  # 복사본을 순회 (원본을 순회하며 remove하면 다음 항목을 건너뛰기 때문)
                    dir_path = os.path.join(root, dirname)
                    if not os.path.isjunction(dir_path) and not os.path.islink(dir_path):
                        safe_dirs.append(dir_path)  # 링크도 정션도 아닌 일반 폴더: 삭제 대상에 추가
                    else:
                        # 링크/정션 폴더: 원본 dirs에서 제거 -> os.walk가 이 폴더 내부로 내려가지 않음
                        # (삭제 대상에도 추가하지 않으므로 폴더 자체도 그대로 남음)
                        dirs.remove(dirname)
                for filename in files:
                    file_path = os.path.join(root, filename)
                    # 링크 파일은 삭제 대상에서 제외
                    if not os.path.islink(file_path):
                        safe_files.append(file_path)

            # 2단계: 파일 먼저 삭제 (사용 중이거나 권한이 없는 파일은 오류만 출력하고 건너뜀)
            for filename in safe_files:
                try:
                    if not dry_run:
                        os.remove(filename)
                    else:
                        print(f"[DRY RUN] Would delete: {filename}")
                except OSError as e:
                    print(f"Error deleting {filename}: {e}")

            # 3단계: 폴더 삭제. 수집 순서가 상위 -> 하위이므로 역순으로 돌려 하위 폴더부터 지움
            # (rmdir은 빈 폴더만 삭제할 수 있기 때문)
            for dirname in reversed(safe_dirs):
                try:
                    if not dry_run:
                        os.rmdir(dirname)
                    else:
                        print(f"[DRY RUN] Would delete: {dirname}")
                except OSError as e:
                    print(f"Error deleting {dirname}: {e}")










