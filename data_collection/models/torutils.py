import os
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver import firefox
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
import shutil
import socket
import stem.process
from stem.util import term
import sys
from http.client import CannotSendRequest
sys.path.append('..')
import helper.utils as utils
import helper.log as log
import time
import random

def get_tor_data_path(tor_path):
    data_path = os.path.join('Browser', 'TorBrowser', 'Data', 'Tor')
    return os.path.join(tor_path, data_path)

def get_tor_bin_path(tor_path):
    """Return a binary path for Tor."""
    bin_path = os.path.join('Browser', 'TorBrowser', 'Tor', 'tor')
    return os.path.join(tor_path, bin_path)

def get_tbb_profile_path(tor_path):
    profile_path = os.path.join('Browser', 'TorBrowser', 'Data', 'Browser', 'profile.default')
    return os.path.join(tor_path, profile_path)

def get_tb_bin_path(tor_path):
    """Return a binary path for Tor Browser."""
    bin_path = os.path.join('Browser', 'firefox')
    return os.path.join(tor_path, bin_path)

def prepend_to_env_var(env_var, new_value):
    """Add the given value to the beginning of the environment var."""
    if os.environ.get(env_var, None):
        if new_value not in os.environ[env_var].split(':'):
            os.environ[env_var] = "%s:%s" % (new_value, os.environ[env_var])
    else:
        os.environ[env_var] = new_value

class TorController(object):
    def __init__(self, tbb_path):
        self.controller = None
        self.tmp_tor_data_dir = None
        self.tor_process = None
        self.tbb_path = tbb_path
        self.circuit_id = None

    def tor_log_handler(self, line):
        log.wl_log.info(term.format(line))

    def restart_tor(self, tor_config, sleep_time=utils.INTERVAL_WAIT_FOR_RESTART):
        """Kill current Tor process and run a new one."""
        self.kill_tor_proc()
        self.launch_tor_service(tor_config)
        print(f'INFO\tSleep {sleep_time}s to wait for Tor to be ready')
        time.sleep(sleep_time)

    def kill_tor_proc(self):
        """Kill Tor process."""
        if self.tor_process:
            self.tor_process.kill()
        if self.tmp_tor_data_dir and os.path.isdir(self.tmp_tor_data_dir):
            shutil.rmtree(self.tmp_tor_data_dir)

    def launch_tor_service(self,tor_config):
        """Launch Tor service and return the process."""

        self.tmp_tor_data_dir = utils.clone_dir_with_timestap(get_tor_data_path(self.tbb_path))
        tor_binary = get_tor_bin_path(self.tbb_path)
        prepend_to_env_var("LD_LIBRARY_PATH", os.path.dirname(tor_binary))

        if not os.path.isfile(tor_binary):
            raise StemLaunchError("Invalid Tor binary")

        while True:
            try:
                print('INFO\tTry to launch tor with stem in {}'.format(utils.cal_now_time()))
                self.tor_process = stem.process.launch_tor_with_config(
                    config=tor_config,
                    tor_cmd=tor_binary,
                    timeout=25,
                    completion_percent = 80
                    )
                print('INFO\tLaunch tor with stem finish in {}'.format(utils.cal_now_time()))
                break
            except stem.SocketError as exc:
                log.wl_log.critical("Unable to connect to tor on port %s: %s" %
                                (utils.USED_SOCKS_PORT, exc))
                sys.exit(1)
            except:
                # most of the time this is due to another instance of
                # tor running on the system
                log.wl_log.critical(f"Error launching Tor", exc_info=True)
                # print(tor_config)
                time.sleep(5)

        print("INFO\tTor running at port {0} & controller port {1}."
                    .format(utils.USED_SOCKS_PORT, utils.USED_CONTROL_PORT))
        return self.tor_process

    def establish_circuit(self, middle_fingerprint):
        assert middle_fingerprint is not None
        guard_list = []
        exit_list = []
        for relay in self.controller.get_network_statuses():
            if 'Guard' in relay.flags:
                guard_list.append(relay)
            if 'Exit' in relay.flags:
                exit_list.append(relay)
        while True:
            try:
                guard_chosen = random.choice(guard_list)
                guard_fingeprint = guard_chosen.fingerprint
                exit_chosen = random.choice(exit_list)
                exit_fingerprint = exit_chosen.fingerprint
                path = [guard_fingeprint, middle_fingerprint, exit_fingerprint]
                return self.controller.new_circuit(path, await_build = True), guard_chosen.address
            except Exception as e:
                pass


    def close_all_streams(self):
        """Close all streams of a controller."""
        log.wl_log.debug("Closing all streams")
        try:
            utils.timeout(utils.STREAM_CLOSE_TIMEOUT)
            for stream in self.controller.get_streams():
                log.wl_log.debug("Closing stream %s %s %s " %
                             (stream.id, stream.purpose,
                              stream.target_address))
                self.controller.close_stream(stream.id)  # MISC reason
        except utils.TimeExceededError:
            log.wl_log.critical("Closing streams timed out!")
        except:
            log.wl_log.debug("Exception closing stream")
        finally:
            utils.cancel_timeout()


class TorBrowserDriver(webdriver.Firefox, firefox.webdriver.RemoteWebDriver):
    def __init__(self, tbb_binary_path=None, tbb_profile_dir=None,
                 tbb_logfile_path=None,
                 tbb_path=None, DISABLE_RANDOMIZEDPIPELINENING=False):
        self.is_running = False
        self.tbb_path = tbb_path
        prepend_to_env_var("LD_LIBRARY_PATH", os.path.dirname(get_tor_bin_path(tbb_path)))

        # Initialize Tor Browser's profile
        self.profile = self.init_tbb_profile()

        # set homepage to a blank tab
        self.profile.set_preference('browser.startup.page', "0")
        self.profile.set_preference('browser.startup.homepage', 'about:newtab')

        # Other
        #self.profile.set_preference('extensions.torbutton.prompted_language', True)

        # configure Firefox to use Tor SOCKS proxy
        self.profile.set_preference('network.proxy.type', 1)
        self.profile.set_preference('network.proxy.socks', '127.0.0.1')
        self.profile.set_preference('network.proxy.socks_port', utils.USED_SOCKS_PORT)
        if DISABLE_RANDOMIZEDPIPELINENING:
            self.profile.set_preference(
                'network.http.pipelining.max-optimistic-requests', 5000)
            self.profile.set_preference(
                'network.http.pipelining.maxrequests', 15000)
            self.profile.set_preference('network.http.pipelining', False)

        self.profile.set_preference(
            'extensions.torlauncher.prompt_at_startup',
            0)

        # Disable cache - Wang & Goldberg's setting
        self.profile.set_preference('network.http.use-cache', False)

        # http://www.w3.org/TR/webdriver/#page-load-strategies-1
        # wait for all frames to load and make sure there's no
        # outstanding http requests (except AJAX)
        # https://code.google.com/p/selenium/wiki/DesiredCapabilities
        self.profile.set_preference('webdriver.load.strategy', 'conservative')
        # Note that W3C doesn't mention "conservative", this may change in the
        # upcoming versions of the Firefox Webdriver
        # https://w3c.github.io/webdriver/webdriver-spec.html#the-page-load-strategy

        # prevent Tor Browser running it's own Tor process
        self.profile.set_preference('extensions.torlauncher.start_tor', False)
        self.profile.set_preference(
            'extensions.torbutton.versioncheck_enabled', False)
        self.profile.set_preference('permissions.memory_only', False)
        self.profile.update_preferences()
        # Initialize Tor Browser's binary
        self.binary = self.get_tbb_binary(logfile=tbb_logfile_path)

        # Initialize capabilities
        self.mycapabilities = DesiredCapabilities.FIREFOX
        self.mycapabilities.update({'handlesAlerts': True,
                                  'databaseEnabled': True,
                                  'javascriptEnabled': True,
                                  'browserConnectionEnabled': True})

        try:
            super(TorBrowserDriver, self)\
                .__init__(firefox_profile=self.profile,
                          firefox_binary=self.binary,
                          capabilities=self.mycapabilities)
                          #executable_path=utils.geckodrive_path)
            self.is_running = True
        except WebDriverException as error:
            log.wl_log.error("WebDriverException while connecting to Webdriver %s"
                         % error)
        except socket.error as skterr:
            log.wl_log.error("Error connecting to Webdriver", exc_info=True)
            log.wl_log.error(skterr.message)
        except Exception as e:
            log.wl_log.error("Error connecting to Webdriver: %s" % e,
                         exc_info=True)


    def get_tbb_binary(self, binary=None, logfile=None):
        """Return FirefoxBinary pointing to the TBB's firefox binary."""
        tbb_logfile = None
        if not binary:
            binary = get_tb_bin_path(self.tbb_path)
        if logfile:
            tbb_logfile = open(logfile, 'a+')

        # in case you get an error for the unknown log_file, make sure your
        # Selenium version is compatible with the Firefox version in TBB.
        tbb_binary = FirefoxBinary(firefox_path=binary,
                                   log_file=tbb_logfile)
        return tbb_binary

    def init_tbb_profile(self):
        profile_directory = get_tbb_profile_path(self.tbb_path)
        self.prof_dir_path = utils.clone_dir_with_timestap(profile_directory)
        try:
            tbb_profile = webdriver.FirefoxProfile(self.prof_dir_path)
        except Exception:
            log.wl_log.error("Error creating the TB profile", exc_info=True)
        else:
            return tbb_profile

    def quit(self, _timeout=600):
        """
        Overrides the base class method cleaning the timestamped profile.

        """
        utils.timeout(_timeout)
        self.is_running = False
        try:
            log.wl_log.info("Quit: Removing profile dir")
            shutil.rmtree(self.prof_dir_path)
            super(TorBrowserDriver, self).quit()
            utils.cancel_timeout()
        except CannotSendRequest:
            log.wl_log.error("CannotSendRequest while quitting TorBrowserDriver",
                         exc_info=False)
            # following is copied from webdriver.firefox.webdriver.quit() which
            # was interrupted due to an unhandled CannotSendRequest exception.

            # kill the browser
            self.binary.kill()
            # remove the profile folder
            try:
                shutil.rmtree(self.profile.path)
                if self.profile.tempfolder is not None:
                    shutil.rmtree(self.profile.tempfolder)
                utils.cancel_timeout()
            except Exception as e:
                print(str(e))
        except Exception:
            log.wl_log.error("Exception while quitting TorBrowserDriver",
                         exc_info=True)
            utils.cancel_timeout()

if __name__ == "__main__":
    print('test ok!')