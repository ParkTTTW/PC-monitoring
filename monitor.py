# 시스템 정보 수집 모듈
import psutil
import os

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