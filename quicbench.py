import argparse
import copy
import json
import os.path

import pandas as pd
import validators

from selenium import webdriver
from selenium.webdriver.chrome import service
from selenium.webdriver.common.devtools.v118.network import RequestWillBeSent, ResponseReceived
from selenium.webdriver.common.devtools.v118.util import parse_json_event

from utils import plot

# usage TODO
# python3 quicbench.py chromedriver uris [uris ...] [-h] [-h2] [-h3] [-p [PLOT]] [-o OUTPUT] [--chrome CHROME] [--android [ANDROID]]
# python3 quicbench.py chromedriver_mac64_v109 example.csv -p example.png -o example.csv
# python3 quicbench.py chromedriver_mac64_v109 https://www.google.com/ https://www.twitter.com/ example.csv -p --android

# PARSE ARGUMENTS
parser = argparse.ArgumentParser(description="quicbench")
parser.add_argument('chromedriver', type=str, help="path to chromedriver")
parser.add_argument('uris', nargs='+', type=str, help="uris to csv or web")
parser.add_argument('--disable-quic', action='store_true', help="http2 mode")
parser.add_argument('--origin-to-force-quic-on', type=str, help="enforce quic on url")
parser.add_argument('-p', '--plot', nargs='?', const='', help="plot")
parser.add_argument('-o', '--output', help="csv output")
parser.add_argument('--chrome', help="path to the chrome binary")
parser.add_argument('--android', nargs='?', const='com.android.chrome', help="android package")
args = parser.parse_args()

# READ INPUT
urls = []
for uri in args.uris:
    if validators.url(uri):  # url input
        urls.append(uri)
    elif os.path.isfile(uri):  # file input
        with open(uri) as file:
            for line in file.read().splitlines():
                if validators.url(line):
                    urls.append(line)
print("Read " + str(len(urls)) + " requests.")
# TODO close file?

if len(urls) == 0:
    print("No urls found.")
    exit(-1)

# CHROMEDRIVER DESIRED CAPABILITIES
# https://chromedriver.chromium.org/capabilities
# https://chromedriver.chromium.org/getting-started/getting-started---android
# https://chromedriver.chromium.org/mobile-emulation TODO
# https://chromedriver.chromium.org/logging TODO
# desired_capabilities has been removed from selenium 4.10.0
# https://stackoverflow.com/questions/76430192/getting-typeerror-webdriver-init-got-an-unexpected-keyword-argument-desi
# https://stackoverflow.com/questions/76550506/typeerror-webdriver-init-got-an-unexpected-keyword-argument-executable-p

# CHROME OPTIONS
options = webdriver.ChromeOptions()

# enable performance and network logging
# https://stackoverflow.com/questions/76792076/setting-logging-prefs-for-chrome-using-selenium-4-10
# https://www.selenium.dev/documentation/webdriver/troubleshooting/upgrade_to_selenium_4/
options.set_capability('goog:loggingPrefs', {'performance': "ALL"})

# https://www.browserstack.com/docs/automate/selenium/accept-insecure-certificates#Legacy_Integration
# options.accept_insecure_certs = True

# connect to android package
if args.android is not None:
    options.add_experimental_option('androidPackage', args.android)
else:
# headless mode if not android device
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    if args.chrome:
        options.binary_location = args.chrome

requests = list()

if args.disable_quic:
    options.add_argument("disable-quic")
else:
    if args.origin_to_force_quic_on is not None:
        options.add_argument('--origin-to-force-quic-on=' + args.origin_to_force_quic_on)

# CREATE WEBDRIVER
driver = webdriver.Chrome(service=service.Service(args.chromedriver), options=options)

# TODO disable favicon possible?

# delete cookies
# https://stackoverflow.com/questions/50456783/python-selenium-clear-the-cache-and-cookies-in-my-chrome-webdriver
driver.delete_all_cookies()
# disable cache
# https://stackoverflow.com/questions/66956625/disable-cache-on-network-tab-using-python-seleniumautomation
# https://chromedevtools.github.io/devtools-protocol/tot/Network/#method-setCacheDisabled
driver.execute_cdp_cmd('Network.setCacheDisabled', {'cacheDisabled': True})

# DO REQUESTS
for url in urls:
    retry = 0

    while True:
        driver.get(url)

        # https://developer.mozilla.org/en-US/docs/Web/API/PerformanceResourceTiming/responseStatus
        performanceTiming = driver.execute_script("return performance.getEntries()")

        # if
        request_id = ''

        # get protocol and status_code from cdp
        # status code should be available in chrome v109, but is 0 everytime
        # https://developer.mozilla.org/en-US/docs/Web/API/PerformanceResourceTiming/responseStatus#browser_compatibility
        for message in driver.get_log("performance"): # get all log entries since last request
            #entry = LogEntry.from_json(message) # TODO native load message?, message != text, level missing
            message = json.loads(message['message'])
            entry = parse_json_event(message['message'])
            # https://chromedevtools.github.io/devtools-protocol/tot/Network/#event-requestWillBeSent
            if type(entry) is RequestWillBeSent:
                if driver.current_url == entry.request.url:  # skip favicon.ico
                    request_id = entry.request_id
            # https://chromedevtools.github.io/devtools-protocol/tot/Network/#event-responseReceived
            if type(entry) is ResponseReceived:
                if request_id == entry.request_id:
                    protocol = entry.response.protocol
                    status_code = entry.response.status

        # quit with success
        if (protocol == 'h3' or args.disable_quic) and status_code == 200:
            requests.append(performanceTiming[0])
            print("[" + str(float(performanceTiming[0]['responseEnd']) - float(performanceTiming[0]['requestStart'])) + "] ",
                  "[" + performanceTiming[0]['nextHopProtocol'] + "] ",
                  performanceTiming[0])
            break

        retry += 1
        # quit without success
        if retry >= 3:
            print("[ERROR] ", performanceTiming[0])
            break
        print("[RETRY] ", performanceTiming[0])

# CLOSE DRIVER
driver.close()

# convert requests to pandas dataframe
rdf = pd.DataFrame(requests)
# calc durations
rdf['connectDuration'] = rdf['connectEnd'] - rdf['connectStart']
rdf['requestDuration'] = rdf['responseEnd'] - rdf['requestStart']
rdf['responseDuration'] = rdf['responseEnd'] - rdf['responseStart']
rdf['duration'] = (rdf['responseEnd'] - rdf['requestStart'])

# EXPORT
if args.output is not None:
    rdf.to_csv(args.output)

# PLOTTING
if args.plot is not None:
    plot(rdf, args.plot)
