"""
特定のコマンドが動作している間のgpuの使用状況を記録します。
参考サイト
https://qiita.com/tomotaka_ito/items/1da001c98b46ecf28ec7
"""
import subprocess
import time, sys
from logging import config, getLogger
from pathlib import Path
import psutil


try:
  config.fileConfig(Path.cwd()/'config/logging.conf')
  logger = getLogger(__name__)
except:
  print('ログファイルの作成に失敗しました。', file=(sys.stderr))
  exit(1)


DEFAULT_ATTRIBUTES = (
    'timestamp',
    'memory.total',
    'memory.free',
    'memory.used',
    'utilization.gpu',
    'utilization.memory'
)

def get_gpu_info(nvidia_smi_path='nvidia-smi', keys=DEFAULT_ATTRIBUTES, no_units=True):
    nu_opt = '' if not no_units else ',nounits'
    cmd = '%s --query-gpu=%s --format=csv,noheader%s' % (nvidia_smi_path, ','.join(keys), nu_opt)
    output = subprocess.check_output(cmd, shell=True)
    lines = output.decode().split('\n')
    return [ line.strip() for line in lines if line.strip() != '' ]



"""
参考サイト 【コピペでOK】pythonで実行中のプロセス一覧を取得する方法
https://web-lh.fromation.co.jp/archives/10000047001
"""
def get_task(procexe, cmdline):
    result = False
    for proc in psutil.process_iter():
        try:
            if procexe in proc.exe():
                if cmdline in str(proc.cmdline()):
                    result = True
        except psutil.AccessDenied:
            result = False
    return result

if __name__ == '__main__':
    procexe = 'python.exe'
    cmdline = 'run_model.py'
    while True:
        time.sleep(1)
        if get_task(procexe, cmdline):
            logger.info(get_gpu_info())
        else:
            break
