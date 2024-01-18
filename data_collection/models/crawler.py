import sys
import os

sys.path.append("..")
import helper.utils as utils
from torutils import TorController
from visit import Visit
from selenium.common.exceptions import TimeoutException
import random
import time

from shutil import copyfile


class Crawler:
    """
    Provides methods to collect traffic traces.
    """

    def __init__(self, urls, torrc_paths, tbb_path, output, xvfb, screenshot, enable_ewfd=False):
        # Create instance of Tor controller and sniffer used for the crawler
        self.crawl_dir = None
        self.crawl_logs_dir = None
        self.visit = None
        self.urls = urls
        self.tbb_path = tbb_path
        self.xvfb = xvfb
        self.screenshot = screenshot
        self.torrc_paths = torrc_paths
        self.enable_ewfd = enable_ewfd

        # Initializes
        self.init_crawl_dirs(output)
        self.tor_controller = TorController(tbb_path)
        self.tor_process = None
        self.tb_driver = None

    def init_crawl_dirs(self, output):
        # Creates results and logs directories for this crawl.
        self.crawl_dir, self.crawl_logs_dir = self.create_crawl_dir(output)
        self.log_env_variables()

    def create_crawl_dir(self, output):
        # Create a timestamped crawl.
        if not os.path.exists(output):
            utils.create_dir(output)  # ensure that we've a results dir
        # 'output/crawl-xtab'
        crawl_dir_wo_ts = os.path.join(output, "crawl")
        # 'output/crawl+timestamped'
        crawl_dir = utils.create_dir(crawl_dir_wo_ts)
        # 'output/crawl+timestamped/logs'
        crawl_logs_dir = os.path.join(crawl_dir, "logs")
        utils.create_dir(crawl_logs_dir)
        return crawl_dir, crawl_logs_dir

    def log_env_variables(self):
        # Dump my IP and the roter IP
        with open(os.path.join(self.crawl_dir, "ip"), "w") as f:
            f.write(f"{utils.MY_IP}\n")
            f.write(f"{utils.USED_GATEWAY_IP}\n")

        # Dump now timestamp
        with open(os.path.join(self.crawl_dir, "timestamp"), "w") as f:
            f.write(str(int(time.time())))

        # Copy torrc
        for torrc_path in self.torrc_paths:
            copyfile(torrc_path, os.path.join(self.crawl_dir, os.path.basename(torrc_path)))

        # Dump utils
        copyfile(utils.__file__, os.path.join(self.crawl_dir, "utils.py"))

        # Dump settings
        with open(os.path.join(self.crawl_dir, "settings"), "w") as f:
            for torrc_path in self.torrc_paths:
                f.write(torrc_path + "\n")

        # Dump urllist
        with open(os.path.join(self.crawl_dir, "urls-crawled.csv"), "w") as f:
            [f.write(i + "\n") for i in self.urls]

    def crawl(self, num_batches=10):
        torrc = None
        url_list = self.urls if num_batches > 1 else self.urls[: int(len(self.urls) * num_batches)]
        total_time = len(url_list) * num_batches * (utils.INTERVAL_WAIT_FOR_RESTART+utils.WAIT_AFTER_DUMP+utils.WAIT_FOR_VISIT+utils.INTERVAL_BETWEEN_VISIT)
        print("INFO\tTotal time: {} H".format(round(total_time/3600,1)))
        end_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time() + total_time ))
        print("INFO\tEnd time: {}".format(end_time))
        num_batches = 1 if num_batches < 1 else num_batches
        # for each batch
        print(
            "INFO\tCrawl configuration: batches: {0}, total number: {1}, crawl dir: {2}".format(
                num_batches, len(url_list), self.crawl_dir
            )
        )

        for batch_num in range(num_batches):
            print("INFO\tStarting batch {} in {}".format(batch_num, utils.cal_now_time()))
            site_num = 0
            batch_dir = utils.create_dir(os.path.join(self.crawl_dir, "batch-" + str(batch_num)))
            random.shuffle(url_list)
            for website in url_list:
                print(
                    "INFO\tCrawling {} url: {} in {}".format(
                        site_num, website, utils.cal_now_time()
                    )
                )
                url_dir = utils.create_dir(os.path.join(batch_dir, "url-" + str(site_num)))
                print("INFO\tRestarting Tor in {}".format(utils.cal_now_time()))
                torrc = random.choice(self.torrc_paths)
                print("INFO\tUse torrc: {}".format(torrc))
                # analyse torrc
                torrc_content,conf = utils.readtorrc(torrc)
                if self.enable_ewfd:
                    if "Log" not in conf:
                        conf["Log"] = []
                    os.makedirs(os.path.join(url_dir, "torlog"), exist_ok=True)
                    conf["Log"].append("NOTICE stdout")
                    conf["Log"].append(f'my file {os.path.join(url_dir,"torlog","my.log")}')
                    assert "MiddleNodes" in conf, f"MiddleNodes should be in {torrc}"
                    assert conf["MiddleNodes"] is not None, "MiddleNodes should not be None"
                    # print('INFO\tMiddle fingerprint: ', conf['MiddleNodes'])
                self.tor_controller.restart_tor(conf)

                with open(os.path.join(url_dir, "label"), "w") as fp:
                    fp.write(website + "\n")
                with open(os.path.join(url_dir, "torrc"), "w") as fp:
                    fp.write(torrc_content + "\n")

                self.visit = None
                try:
                    print("INFO\tInit visit in {}".format(utils.cal_now_time()))
                    self.visit = Visit(
                        website,
                        url_dir,
                        self.tor_controller,
                        self.tbb_path,
                        self.xvfb,
                        self.screenshot,
                    )
                    print("INFO\tStart visit in {}".format(utils.cal_now_time()))
                    start_time = time.time()
                    self.visit.get()
                    end_time = time.time()
                    with open(os.path.join(url_dir, "time"), "w") as fp:
                        fp.write(f"{start_time}\n")
                        fp.write(f"{end_time}\n")
                    # delete chched files

                except KeyboardInterrupt:  # CTRL + C
                    raise KeyboardInterrupt
                except TimeoutException as exc:
                    print("CRITICAL\tVisit timed out! %s %s" % (exc, type(exc)))
                    if self.visit:
                        self.visit.cleanup_visit()
                except Exception as exc:
                    print("CRITICAL\tException crawling: %s" % exc)
                    if self.visit:
                        self.visit.cleanup_visit()
                # END - for each visit
                site_num += 1
                time.sleep(utils.INTERVAL_BETWEEN_VISIT)

    def stop_crawl(self, pack_results=True):
        """Cleans up crawl and kills tor process in case it's running."""
        print("Stopping crawl...")
        if self.visit:
            self.visit.cleanup_visit()
        self.tor_controller.kill_tor_proc()


if __name__ == "__main__":
    print("test")
