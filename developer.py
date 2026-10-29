import winreg, struct, time
import os
import re
from icoextract import IconExtractor,IconExtractorError


# 아이콘 추출 및 자동 폴더 초기화
def icon_extract():
    # 세이프 파일 경로 변경 필요
    save_path = r"C:\icons"
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


            try:
                extractor = IconExtractor(data_path)
                ico_file = os.path.join(save_path, name + ".ico") # 아이콘 이름을 name으로 해놔서 나중에 name으로 비교 후 짝 지으면 됨
                extractor.export_icon(ico_file)
            except IconExtractorError as e:
                print(f"Error extracting icon for {name}: {e}")

    stop = input("대기: space pass")
    # 폴더 내 icon 파일 삭제 (초기화)
    for filename in os.listdir(save_path):
      file_path = os.path.join(save_path, filename)
      if os.path.isfile(file_path):
        os.remove(file_path)


with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run", 0, winreg.KEY_READ) as key:
    for i in range(winreg.QueryInfoKey(key)[1]):
        name, data, type_ = winreg.EnumValue(key, i)
        print(name, data.hex(), type_)


# 시작프로그램 활성화
def set_startup_enabled(selected_en): # selected_en 에는 무조건 list형태 이어야함

    enabled = bytes([2]) + bytes(11)
    with winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run", 0, winreg.KEY_SET_VALUE) as key:
            for process in selected_en:
                winreg.SetValueEx(key,process, 0, winreg.REG_BINARY, enabled)    




# 시작프로그램 비활성화
def set_startup_disabled(selected_dis): # selected_dis 에는 무조건 list형태 이어야함
    # 시각 바이트가 리틀엔디안 이므로 struct.pack("<Q", ft) 낮은 바이트 부터 작성 
    # 시각 바이트는 틀려도 상관 x  첫바이트 (02,03)으로 구별 
    ft = int((time.time() + 11644473600) * 10_000_000)
    disabled = bytes([3]) + bytes(3) + struct.pack("<Q", ft)
    with winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run", 0, winreg.KEY_SET_VALUE) as key:
        for process in selected_dis:
            winreg.SetValueEx(key,process, 0, winreg.REG_BINARY, disabled)
