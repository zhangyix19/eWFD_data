import os
import sys

sys.path.append(".")
sys.path.append("models")
from models.crawler import Crawler
import helper.utils as utils
import helper.log as log
import argparse
import traceback
import random

if __name__ == "__main__":
    # Parse arguments
    parser = argparse.ArgumentParser(description="Crawl a list of URLs in several batches.")

    # Add arguments
    parser.add_argument("--scenario", default="cw", type=str, help="close world(cw)/open world(ow)")
    parser.add_argument("--urls_file", default="", type=str, help="URLs file path")
    parser.add_argument(
        "--batch", default="1", type=str, help="Number of batches, for cw int, for ow float < 1"
    )
    parser.add_argument("--outputdir", default="outputdir", type=str)
    parser.add_argument(
        "--tbbpath", default="../tbb/tor-browser_zh-CN", type=str, help="Path of tbb"
    )
    parser.add_argument("--xvfb", default=True, type=bool, help="Use XVFB (for headless testing)")
    parser.add_argument("--screenshot", default=True, type=bool, help="Capture page screenshots)")
    parser.add_argument("--torrc_dir_path", default="", type=str, help="path to torrc config dir")
    parser.add_argument("--ewfd", action="store_true", help="enable ewfd")

    args = parser.parse_args()

    scenario = args.scenario
    urls_file = args.urls_file
    num_batches = args.batch
    output = args.output
    tbb_path = args.tbbpath
    xvfb = args.xvfb
    screenshot = args.screenshot
    torrc_dir_path = args.torrc_dir_path
    enable_ewfd = args.ewfd

    assert scenario in ["cw", "ow"]

    if scenario == "cw":
        num_batches = int(num_batches)
        assert num_batches > 1
    elif scenario == "ow":
        num_batches = float(num_batches)
        assert num_batches < 1 and num_batches > 0

    # read urls
    assert os.path.isfile(urls_file)
    with open(urls_file, "r") as fp:
        urls = fp.read().splitlines()
    random.shuffle(urls)
    assert os.path.isdir(torrc_dir_path)
    torrc_paths = [
        os.path.join(torrc_dir_path, torrc_path) for torrc_path in os.listdir(torrc_dir_path)
    ]
    # init crawler
    crawler = Crawler(urls, torrc_paths, tbb_path, output, xvfb, screenshot, enable_ewfd)
    print("INFO\tInit crawler finish in {}".format(utils.cal_now_time()))
    print("INFO\tCommand line parameters: %s" % sys.argv)

    # Run the crawl

    try:
        crawler.crawl(num_batches)
    except KeyboardInterrupt:
        log.wl_log.warning(
            "WARNING\tKeyboard interrupt! Quitting in {}...".format(utils.cal_now_time())
        )
    except Exception as e:
        log.wl_log.error(
            "ERROR\tException in {}: \n {}".format(utils.cal_now_time(), traceback.format_exc())
        )
    finally:
        crawler.stop_crawl()

    print("INFO\tData Collection done in {}".format(utils.cal_now_time()))
