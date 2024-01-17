import subprocess
import os
import sys
sys.path.append('..')
import helper.utils as utils
import helper.log as log
import time


TCPDUMP_START_TIMEOUT = 10.0


class Sniffer(object):
    """Capture network traffic using tcpdump."""

    def __init__(self):
        self.pcap_file = '/dev/null'  # uggh, make sure we set a path
        self.pcap_filter = ''
        self.p0 = None
        self.is_recording = False

    def set_pcap_path(self, pcap_filename):
        """Set filename and filter options for capture."""
        self.pcap_file = pcap_filename

    def set_capture_filter(self, _filter):
        self.pcap_filter = _filter

    def get_pcap_path(self):
        """Return capture (pcap) filename."""
        return self.pcap_file

    def get_capture_filter(self):
        """Return capture filter."""
        return self.pcap_filter

    def start_capture(self, pcap_path=None, pcap_filter=""):
        """Start capture. Configure sniffer if arguments are given."""
        if pcap_filter:
            self.set_capture_filter(pcap_filter)
        if pcap_path:
            self.set_pcap_path(pcap_path)
        
        
        command = 'sudo tcpdump -p -s 0 -i eth0 -w {} -f {} and not port 22'\
            .format(self.pcap_file, self.pcap_filter)

        self.p0 = subprocess.Popen(command, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, shell=True)
        timeout = TCPDUMP_START_TIMEOUT  # in seconds
        while timeout > 0 and not self.is_tcpdump_running():
            time.sleep(0.1)
            timeout -= 0.1
        
        print("INFO\ttcpdump started in {}, command{}".format(utils.cal_now_time(),command))
        self.is_recording = True

    def is_tcpdump_running(self):
        for proc in utils.gen_all_children_procs(self.p0.pid):
            if "tcpdump" in proc.cmdline():
                return True
        return False

    def stop_capture(self):
        """Kill the tcpdump process."""
        utils.kill_all_children(self.p0.pid)  # self.p0.pid is the shell pid
        self.p0.kill()
        self.is_recording = False
        if os.path.isfile(self.pcap_file):
            log.wl_log.info('Tcpdump killed. Capture size: %s Bytes %s' %
                        (os.path.getsize(self.pcap_file), self.pcap_file))
        else:
            log.wl_log.warning('Tcpdump killed but cannot find capture file: %s'
                           % self.pcap_file)

if __name__ == "__main__":
    print('test ok!')
