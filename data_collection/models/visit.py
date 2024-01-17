from selenium.webdriver.common.keys import Keys
from torutils import TorBrowserDriver
import sys
sys.path.append('../..')
import helper.utils as utils
from xvfbwrapper import Xvfb
import os
from dumputils import Sniffer
import time


class Visit(object):
    """Hold info about a particular visit to a page."""

    def __init__(self, page_url, url_dir, tor_controller, 
                 tbb_path, xvfb, screenshot):
        # load
        self.page_url = page_url
        self.url_dir = url_dir
        self.tor_controller = tor_controller
        self.tbb_path = tbb_path
        self.visit_dir = None
        self.visit_log_dir = None
        self.xvfb = xvfb
        self.screenshot = screenshot
        
        # init visit dir
        self.init_visit_dir()
        self.pcap_path = os.path.join(self.visit_dir, "tcp.pcap")
        
        # use xvfb
        if self.xvfb:
            self.xvfb_display = utils.start_xvfb()
        
        # Create new instance of TorBrowser driver
        self.tb_driver = TorBrowserDriver(
            tbb_logfile_path=os.path.join(self.visit_dir, "logs", "firefox.log"), tbb_path=self.tbb_path)

        self.sniffer = Sniffer()  # sniffer to capture the network traffic

    def init_visit_dir(self):
        """Create results and logs directories for this visit."""
        self.visit_dir = self.url_dir
        self.visit_log_dir = os.path.join(self.visit_dir, 'logs')
        utils.create_dir(self.visit_log_dir)

    def cleanup_visit(self):
        """Kill sniffer and Tor browser if they're running."""
        print("INFO\tCleaning up visit.")
        print("INFO\tCancelling timeout")
        utils.cancel_timeout()

        if self.sniffer and self.sniffer.is_recording:
            print("INFO\tStopping sniffer...")
            self.sniffer.stop_capture()
        if self.tb_driver and self.tb_driver.is_running:
            # shutil.rmtree(self.tb_driver.prof_dir_path)
            print("INFO\tQuitting selenium driver...")
            self.tb_driver.quit()

        # close all open streams to prevent pollution
        print("INFO\tClose all open streams")
        self.tor_controller.close_all_streams()
        if self.xvfb:
            print("INFO\tStop xvfb")
            utils.stop_xvfb(self.xvfb_display)

    def take_screenshot(self, url):
        try:
            if 'http://' in url or 'https://' in url:
                url = url.split('//')[1]
            out_png = os.path.join(self.visit_dir, '{}.png'.format(url))
            print("INFO\tTaking screenshot of %s to %s" % (self.page_url, out_png))
            self.tb_driver.get_screenshot_as_file(out_png)
        except:
            print("ERROE\tException while taking screenshot of: %s" % self.page_url)
            return False
        return True

    def get(self):
        """Call the specific visit function depending on the experiment."""

        utils.timeout(utils.HARD_VISIT_TIMEOUT)
      
        print('INFO\tcapture start in {} path {}'.format(utils.cal_now_time(),self.pcap_path))
        self.sniffer.start_capture(
            self.pcap_path,
            f'tcp and host {utils.MY_IP}')


        try:
            self.tb_driver.set_page_load_timeout(utils.SOFT_VISIT_TIMEOUT)
        except:
            print("INFO\tException setting a timeout {}".format(self.page_url))

        time.sleep(utils.WAIT_AFTER_DUMP)

        page_url = self.page_url
        if 'http://' in page_url or 'https://' in page_url:
            newTab = 'window.open("%s");' % page_url
        else:
            newTab = 'window.open("https://%s");' % page_url 
        print('INFO\tCrawling URL: {} in {}'. format(page_url, utils.cal_now_time()))
        self.tb_driver.execute_script(newTab)
        self.tb_driver.switch_to.window(self.tb_driver.window_handles[-1])

        time.sleep(utils.WAIT_FOR_VISIT) if not '.onion' in page_url else time.sleep(utils.WAIT_FOR_VISIT_ONION)
        print('INFO\tEnd crawling url in {}'.format(utils.cal_now_time()))
        
        if self.screenshot:
            self.tb_driver.switch_to.window(self.tb_driver.window_handles[1])
            self.take_screenshot(page_url)
        self.cleanup_visit()


if __name__ == "__main__":
    print('test ok!')
