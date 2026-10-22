# 임시 파일 및 캐시 정리
# 레지스트리 청소 (위험)
# 시작 프로그램 및 서비스 관리
# 디스크 및 메모리 최적화

import os
import tempfile


temp_dir = tempfile.gettempdir() # 임시 디렉토리 경로 가져오기
with os.scandir(temp_dir) as it:
        temp = list(it)
        for entry in temp:
            print(entry.name)
            print(entry.is_file()) # 파일여부 True/False
            print(entry.is_dir()) # 디렉토리 여부 True/False
            print(int(entry.stat().st_size/1024)) # 파일 크기 (KB)
            print(entry.stat().st_mtime) # 마지막 수정 시간