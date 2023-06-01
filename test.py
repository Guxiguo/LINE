import os

def get_download_path():
    """获取系统的默认下载路径"""
    if os.name == 'nt': # Windows系统
        download_path = os.path.expanduser("~\\Downloads")
    elif os.name == 'posix': # macOS或Linux系统
        download_path = os.path.expanduser("~/Downloads")
    else:
        download_path = None
    return download_path

download_path = get_download_path()
filename = os.listdir(download_path)[-1] 
print(filename)
