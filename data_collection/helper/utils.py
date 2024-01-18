import os
import re
from time import strftime
import distutils.dir_util as du
import sys
import signal
import shutil
import psutil
import time
from pyvirtualdisplay import Display

# Need modify for different server
# geckodrive_path = '/root/wfp/geckodriver'  # geckodriver path
MY_IP = "myip"  # The host ip (run 'ifconfig' in terminal)
NOISE_IP = [
    "100.100.30.25",
    "100.100.30.26",
    "100.100.35.30",
    "100.103.0.47",
    "100.103.0.45",
    "100.100.103.57",
    "100.100.30.60",
    "100.100.98.18",
]
USED_GATEWAY_IP = "routeip"  # run 'route -n' in terminal
LOCALHOST_IP = "127.0.0.1"  # default localhost IP (run 'ifconfig' in terminal)

# Hyperparameter
STREAM_CLOSE_TIMEOUT = 5  # wait 5 seconds before raising an alarm signal
INTERVAL_BETWEEN_VISIT = 0  # Interval time between instances
WAIT_AFTER_DUMP = 2  # Waiting time after opening dumpcap

# BOTH < INTERVAL_DUMP - INTERVAL_WAIT_FOR_RESTART - INTERVAL_BETWEEN_VISIT
# BOTH < SOFT_VISIT_TIMEOUT
WAIT_FOR_VISIT = 90  # Waiting time for each url
WAIT_FOR_VISIT_ONION = 360  # Waiting time for each onion url (onion sites are slower)

MAX_SITES_PER_TOR_PROCESS = 0
SOFT_VISIT_TIMEOUT = 105  # timeout used by selenium and dumpcap
HARD_VISIT_TIMEOUT = SOFT_VISIT_TIMEOUT + 10  # signal based hard timeout in case soft timeout fails
INTERVAL_DUMP = 240  # for client-bridge sync
INTERVAL_WAIT_FOR_RESTART = 20
# Constant
DEFAULT_SOCKS_PORT = 9050  # SYSTEM TOR PORTS
DEFAULT_CONTROL_PORT = 9051
TBB_SOCKS_PORT = 9150  # TBB TOR PORTS
TBB_CONTROL_PORT = 9151
STEM_SOCKS_PORT = 9250  # STEM port
STEM_CONTROL_PORT = 9251
USED_SOCKS_PORT = DEFAULT_SOCKS_PORT
USED_CONTROL_PORT = DEFAULT_CONTROL_PORT

DEFAULT_XVFB_WIN_W = 1280  # Default dimensions for the virtual display
DEFAULT_XVFB_WIN_H = 800


def start_xvfb(win_width=DEFAULT_XVFB_WIN_W, win_height=DEFAULT_XVFB_WIN_H):
    """Start and return virtual display using XVFB."""
    print("INFO\tStarting XVFB: {} x {}".format(win_width, win_height))
    xvfb_display = Display(visible=0, size=(win_width, win_height))
    xvfb_display.start()
    return xvfb_display


def stop_xvfb(xvfb_display):
    """Stop the given virtual display."""
    if xvfb_display:
        xvfb_display.stop()


class TimeExceededError(Exception):
    pass


def cal_now_time(_flag=False):
    res_time = None
    if _flag:
        res_time = time.time()
    else:
        stamp = time.localtime(time.time())
        res_time = time.strftime("%Y-%m-%d %H:%M:%S", stamp)
    return res_time


def create_dir(dir_path):
    """Create a directory if it doesn't exist."""
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    return dir_path


def append_timestamp(_str=""):
    """Append a timestamp to a string and return it."""
    return _str + strftime("%y%m%d_%H%M%S")


def clone_dir_with_timestap(orig_dir_path):
    """Copy a folder into the same directory and append a timestamp."""
    new_dir = create_dir(append_timestamp(orig_dir_path))
    try:
        du.copy_tree(orig_dir_path, new_dir)
    except Exception as e:
        print("ERROR\tError while cloning the dir with timestamp" + str(e))
    finally:
        return new_dir


def get_tor_data_path(version, os_name="linux", lang="zh-CN"):
    """Return the path for Data dir of Tor."""
    major = get_tbb_major_version(version)
    data_path = TOR_DATA_DIR_DICT[major]
    tbb_path = get_tbb_path(version, os_name, lang)
    return join(tbb_path, data_path)


def get_filename_from_url(url, prefix):
    """Return base filename for the url."""
    url = url.replace("https://", "")
    url = url.replace("http://", "")
    url = url.replace("www.", "")
    dashed = re.sub(r"[^A-Za-z0-9._]", "-", url)
    return "%s-%s" % (prefix, re.sub(r"-+", "-", dashed))


def cancel_timeout():
    """Cancel a running alarm."""
    signal.alarm(0)


def gen_all_children_procs(parent_pid):
    parent = psutil.Process(parent_pid)
    for child in parent.children(recursive=True):
        yield child


def kill_all_children(parent_pid):
    """Kill all child process of a given parent."""
    for child in gen_all_children_procs(parent_pid):
        child.kill()


def raise_signal(signum, frame):
    raise TimeExceededError


def timeout(duration):
    """Timeout after given duration."""
    signal.signal(signal.SIGALRM, raise_signal)  # linux only !!!
    signal.alarm(duration)  # alarm after X seconds


def kill_all_children(parent_pid):
    """Kill all child process of a given parent."""
    for child in gen_all_children_procs(parent_pid):
        child.kill()


def readtorrc(torrc):
    assert os.path.isfile(torrc), "Invalid torrc path{}".format(torrc)
    with open(torrc, "r") as f:
        content = f.read()
    with open(torrc, "r") as f:
        lines = f.readlines()
        lines = [line.strip().split(" ", 1) for line in lines]
        lines = [line for line in lines if len(line) == 2]
        conf = {}
        conf = {line[0]: line[1] for line in conf if line[0]}
        for line in lines:
            if line[0] not in conf:
                conf[line[0]] = []
            conf[line[0]].append(line[1])
        conf["DataDirectory"] = "/tmp/tor"
    return content,conf


if __name__ == "__main__":
    print("test")
