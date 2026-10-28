import os
import subprocess

BASE = r"D:\test_cleaner"          # 본인 환경에 맞게 변경 (중요 데이터 없는 곳)
DUMMY = os.path.join(BASE, "dummy")
TARGET = os.path.join(BASE, "target")

# 폴더 생성
for d in [
    DUMMY,
    os.path.join(DUMMY, "sub1", "deep"),
    os.path.join(DUMMY, "sub2"),
    os.path.join(DUMMY, "empty_dir"),
    TARGET,
]:
    os.makedirs(d, exist_ok=True)

# 파일 생성 (크기를 다르게 해서 용량 집계도 확인)
files = {
    os.path.join(DUMMY, "a.tmp"): 1024,
    os.path.join(DUMMY, "b.log"): 2048,
    os.path.join(DUMMY, "noext"): 512,
    os.path.join(DUMMY, "sub1", "c.tmp"): 4096,
    os.path.join(DUMMY, "sub1", "deep", "d.tmp"): 8192,
    os.path.join(DUMMY, "sub2", "e.log"): 1024,
    os.path.join(TARGET, "keep.txt"): 100,   # 지워지면 안 됨
}
for path, size in files.items():
    with open(path, "wb") as f:
        f.write(b"x" * size)

# 정션 생성 (dummy 안에서 target을 가리킴, 관리자 권한 불필요)
junction = os.path.join(DUMMY, "junc_a")
if not os.path.exists(junction):
    subprocess.run(["cmd", "/c", "mklink", "/J", junction, TARGET], check=True)

print("더미 환경 생성 완료")
