"""
PC 클리너 - 임시 파일 스캔 및 삭제 (Windows 전용)

[구현 범위]
1. 임시 파일 및 캐시 정리   <- 스캔/삭제 기능 구현 완료 (기능 테스트 완료 *심볼릭 링크 테스트는 추후에)
2. 시작 프로그램 관리       <- 예정
3. 디스크 및 메모리 최적화  <- 예정
(레지스트리 청소는 위험도가 높아 구현 제외)
"""

import os
import winreg

# 정리 대상 목록: (환경변수 이름, 그 아래 하위 경로)
# 경로를 직접 적지 않고 환경변수로 조합하므로 사용자명이나 PC가 달라도 동작함
CACHE_TARGETS = [
    ("TEMP",         ""),                                          # 사용자 임시 폴더
    ("LOCALAPPDATA", r"Google\Chrome\User Data\Default\Cache"),    # Chrome 캐시
    ("LOCALAPPDATA", r"Microsoft\Edge\User Data\Default\Cache"),   # Edge 캐시
    ("LOCALAPPDATA", r"Microsoft\Windows\INetCache"),              # 인터넷 임시 파일
]
startup_key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"  # 시작 프로그램 레지스트리 경로
# 스캔 기능: 지정한 폴더 안의 파일과 폴더를 조사하여 통계를 출력한다.
def scan_directory(scan_path):
    # with 블록이 끝나면 scandir 핸들이 자동으로 닫힘
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
                    filesize_total += entry.stat().st_size / 1024  # 바이트 -> KB

                    # 확장자 추출 (앞의 점 제거, 소문자로 통일)
                    extension = (os.path.splitext(entry.name)[1][1:]).lower()
                    if extension == '':
                        extension = "unknown"  # 확장자가 없는 파일의 표시용 이름

                    if extension not in extension_names:
                        extension_names.append(extension)

                # 폴더: 개수와 폴더 항목 자체의 크기만 집계
                elif entry.is_dir():
                    dir_count += 1
                    dirsize_total += entry.stat().st_size / 1024

            # 스캔 중 파일이 사라졌거나 접근이 거부된 경우: 해당 항목만 건너뛰고 계속 진행
            except OSError as e:
                print(f"Error accessing {entry.name}: {e}")

        # --- 결과 출력 ---
        print(extension_names)
        print(f"임시 파일 개수: {file_count}")
        print(f"임시 디렉토리 개수: {dir_count}")
        print(f"임시 파일 총 용량: {filesize_total:.2f} KB")
        print(f"임시 디렉토리 총 용량: {dirsize_total:.2f} KB")
        print(f"파일 확장자: {','.join(extension_names)}")


# 삭제 기능: 지정한 폴더 안의 모든 파일과 하위 폴더를 삭제한다. (링크/정션은 건드리지 않음)
# topdown=True를 쓰는 이유: 상위 폴더부터 탐색해야 링크/정션 폴더를 만났을 때
# dirs에서 제거해 그 내부로 내려가지 않게 막을 수 있기 때문
# (topdown=False는 하위 폴더를 먼저 탐색하므로 이런 차단이 불가능함)
def delete_file_contents(scan_path,dry_run=True):
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

# 메인 실행부: 정리 대상 경로를 하나씩 순회
for env_var, sub_path in CACHE_TARGETS:
    scan_path = os.path.join(os.environ.get(env_var), sub_path)  # 환경변수 값 + 하위 경로로 전체 경로 조합
    print(f"Scanning: {scan_path}")
    if not os.path.isdir(scan_path):
        print(f"경로(폴더)가 존재하지 않음: {scan_path}")
        continue  # 경로가 없으면 다음 대상으로 넘어감
    # scan_directory(scan_path)          # 스캔 (읽기 전용, 파일을 지우지 않음)
    # delete_file_contents(scan_path)    # 삭제 (실제로 지우므로 충분히 테스트한 뒤 활성화)




