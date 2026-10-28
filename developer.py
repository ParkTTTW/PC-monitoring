import winreg
import os
import re
from icoextract import IconExtractor,IconExtractorError
save_path = r"C:\Users\qkrxo\PC_monitoring\icons"
with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_READ) as key:
    count = winreg.QueryInfoKey(key)[1] # 11
    for i in range(count):
        name, data, type_ = winreg.EnumValue(key, i)
        print(f"Name: {name}, Data: {data}, Type: {type_}")
    test = [data]
    print(test)
    data_path = re.findall(r'"([^"]*)"', data)[0] # 따옴표 안의 경로 추출

#        data_path = re.findall(r'"([^"]*)"', data)[0]  # 따옴표 안의 경로 추출
    try:
        extractor = IconExtractor(data_path)
        ico_file = os.path.join(save_path, name + ".ico")
        extractor.export_icon(ico_file)
    except IconExtractorError as e:
        print(f"Error extracting icon for {name}: {e}")

