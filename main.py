"""
PC 클리너 - 임시 파일 스캔 및 삭제 (Windows 전용)

[구현 범위]
1. 임시 파일 및 캐시 정리   <- 스캔/삭제 기능 구현 완료 (기능 테스트 완료 *심볼릭 링크 테스트는 추후에)
2. 시작 프로그램 관리       <- 활성화, 비활성화 기능 구현 완료
3. 디스크 및 메모리 최적화  <-  프로세스 종료 기능 구현 완료 (기능 테스트 완료)
(레지스트리 청소는 위험도가 높아 구현 제외)
"""

# 시스템 정보 수집 모듈
import psutil


# CPU 정보
def get_cpu():
    cpu_percent = psutil.cpu_percent(interval=0.1, percpu=False)
    cpu_core = psutil.cpu_count()
    return cpu_percent,cpu_core

# 메모리 정보 MB
def get_memory():
    virtual_memory = psutil.virtual_memory()
    total_memory = virtual_memory.total // (1024*1024)
    available_memory = virtual_memory.available // (1024*1024)
    used_memory = total_memory - available_memory
    return total_memory, available_memory, used_memory

# 디스크 정보 GB
def get_disk():
    disk_usage = psutil.disk_usage('/')
    total_disk_space = disk_usage.total // (1024*1024*1024)
    used_disk_space = disk_usage.used // (1024*1024*1024)
    free_disk_space = disk_usage.free // (1024*1024*1024)
    return total_disk_space, used_disk_space, free_disk_space







print(get_memory())