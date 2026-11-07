import winreg, struct, time
import os
import re
from icoextract import IconExtractor,IconExtractorError
import tkinter as tk
import tkinter.ttk as ttk
from PIL import Image, ImageTk


class StartupManager(tk.Frame):

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.startup_key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"  # 시작 프로그램 레지스트리 경로
        self.icons = {}

        self.tree = ttk.Treeview(self, columns=("data",), show="tree headings")
        self.tree.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

        
        
        
        self.tree.heading("#0", text="프로세스 이름")
        self.tree.heading("data", text="활성화 상태")

        self.tree.column("#0", width=80, anchor=tk.CENTER)
        self.tree.column("data", width=250, anchor=tk.CENTER)


        refresh_btn = tk.Button(self, text="🔄새로고침", command=self.check_startup)
        refresh_btn.pack(side=tk.LEFT, padx=5)

        enabled_btn = tk.Button(self, text="활성화", command=lambda: self.set_startup_enabled([self.tree.item(self.tree.selection()[0])["values"][0]]), fg="red")
        enabled_btn.pack(side=tk.LEFT, padx=5)

        disabled_btn = tk.Button(self, text="비활성화", command=lambda: self.set_startup_disabled([self.tree.item(self.tree.selection()[0])["values"][0]]), fg="red")
        disabled_btn.pack(side=tk.LEFT, padx=5)

        self.check_startup()  # 초기 로드

    def make_placeholder_icon(self, ico_file, size=64):
        """평범한 회색 사각형 임시 아이콘 생성"""
        Image.new("RGBA", (size, size), (150, 150, 150, 255)).save(ico_file, format="ICO")
    
    def load_images(self, name):
        try:
            # 원본 이미지를 16x16 크기로 조절
            img = Image.open(rf"C:\Users\qkrxo\PC_monitoring\icons\{name}.ico").resize((20, 20))
            self.user_icon = ImageTk.PhotoImage(img)
            self.icons[name] = self.user_icon
        except:
            # 이미지 파일이 없을 때 에러 방지용 더미 이미지
            self.user_icon = tk.PhotoImage(width=20, height=20)
            self.user_icon.put("#CCCCCC", to=(0, 0, 16, 16))
            self.icons[name] = self.user_icon
        return self.user_icon


    def icon_extract(self):
        # 경로 환경변수로 변경 필요
        global save_path
        save_path = r"C:\Users\qkrxo\PC_monitoring\icons"

        # 폴더 내 icon 파일 삭제 (초기화)
        for filename in os.listdir(save_path):
          file_path = os.path.join(save_path, filename)
          if os.path.isfile(file_path):
            os.remove(file_path)
        
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_READ) as key:
            count = winreg.QueryInfoKey(key)[1]
            for i in range(count):
                # REG_EXPAND_SZ에 저장된 값을 가지고 오는거라 환경변수로 되어있는 PC에서는 누락 발생 가능
                name, data, type_ = winreg.EnumValue(key, i)
                #print(f"Name: {name}, Data: {data}, Type: {type_}")
                m = re.match(r'"([^"]*)"', data)
                # type(data) == list 리스트 안 객체로 파악해서 false 반환
                if m :    
                    data_path = m.group(1) # (1) "경로" -> 경로
                else :
                   idx = data.lower().rfind(".exe")  # 마지막 exe 추출 (이상한 경로 예외)
                   if idx == -1 :
                       continue
                   else :
                       data_path = data[:idx + 4]
                ico_file = os.path.join(save_path, name + ".ico") # 아이콘 이름을 name으로 해놔서 나중에 name으로 비교 후 짝 지으면 됨
                try:
                    extractor = IconExtractor(data_path)
                    extractor.export_icon(ico_file)
                except (IconExtractorError, OSError) as e:
                    print(f"Error extracting icon for {name}: {e}")
    

    
    # 시작프로그램 레지스트리 값 확인 (새로고침)
    def check_startup(self):
        
        startup_programs = []
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run", 0, winreg.KEY_READ) as key:
            count = winreg.QueryInfoKey(key)[1]
            for i in range(count):
                name, data, type_ = winreg.EnumValue(key, i)
                startup_programs.append((name, data, type_))

        for item in self.tree.get_children():
            self.tree.delete(item)
        self.icons.clear() 
        self.icon_extract()

        for name, data, type_ in startup_programs:
            if data[0] == 2:
                data = "활성화"
            elif data[0] == 3:
                data = "비활성화"
            self.tree.insert("", tk.END, text=name, image= self.load_images(name), values=(data,))
            



    # 시작프로그램 활성화
    def set_startup_enabled(self, selected_en): # selected_en 에는 무조건 list형태 이어야함

        enabled = bytes([2]) + bytes(11)
        with winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run", 0, winreg.KEY_SET_VALUE) as key:
                for process in selected_en:
                    winreg.SetValueEx(key,process, 0, winreg.REG_BINARY, enabled)    
        self.check_startup()  # 활성화 후 새로고침



    # 시작프로그램 비활성화
    def set_startup_disabled(self, selected_dis): # selected_dis 에는 무조건 list형태 이어야함
        # 시각 바이트가 리틀엔디안 이므로 struct.pack("<Q", ft) 낮은 바이트 부터 작성 
        # 시각 바이트는 틀려도 상관 x  첫바이트 (02,03)으로 구별 
        ft = int((time.time() + 11644473600) * 10_000_000)
        disabled = bytes([3]) + bytes(3) + struct.pack("<Q", ft)
        with winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run", 0, winreg.KEY_SET_VALUE) as key:
            for process in selected_dis:
                winreg.SetValueEx(key,process, 0, winreg.REG_BINARY, disabled)
        self.check_startup()  # 비활성화 후 새로고침