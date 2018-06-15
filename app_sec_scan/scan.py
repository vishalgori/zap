#!/usr/bin/python2.7
import logging
import os
import sys
import time
import urllib
from urlparse import urlparse
from zapv2 import ZAPv2
import boto3
import yaml
import argparse
from enable_session_handling import Session_Handling
from create_scan_policy import CreateScanPolicy

def slack(message, slack_web_hook):
    slack_room = "#security-builds"
    user_name = "zap_auth_scan"

    data = 'payload={"channel":"' + slack_room + '", "username": "' + user_name + '", "text":"' + message + '"}'
    response = urllib.urlopen('https://hooks.slack.com/services/' + slack_web_hook, data)
    print response.read()

class Main:
    def __init__(self):
        pass

    if __name__ == "__main__":

        #Configuration Directory
        base_config_dir="/home/zap/security-configurations/"

        parser = argparse.ArgumentParser(description='Run Zap Scans')
        parser.add_argument('--yml', help="YML Configuration File", required=True)

        args = vars(parser.parse_args())
        yml = args["yml"]

        # Configure logging.
        log_file_name = "/home/zap/zap-scan-log" + str(time.time()) + ".txt"
        logging.basicConfig(filename=log_file_name, level=logging.DEBUG)

        # Configuration using YAML.
        config = None
        try:
            config = yaml.load(open(base_config_dir + "config/app/" + yml))
        except:
            logging.debug("Error while loading YAML file: " + str(sys.exc_info()[0]))
            raise

        #Check if zap is running. Then enable auto session handling.
        session_handler = Session_Handling()
        try:
            session_handler.enable_session_handling(log_file_name,config)
        except:
            logging.debug("Error while calling session handler: " + str(sys.exc_info()[0]))
            raise

        # Creating zap api version2 object
        zap = ZAPv2()

        #Defining variables from config parser.
        targetURL = config['URL'][0] # Target URL
        targetURL_regex = targetURL + ".*"  # For zap.
        contextname = str(urlparse(targetURL).netloc) + "-" + str(time.time())
        urls_in_context = config['AdditionalURLs'] #This is a list
        pscan = config['Scan'][0]['pscan'][0] #This is boolean
        ascan = config['Scan'][1]['ascan'][0] #This is boolean
        excludes = config['Excludes'] #This is a list
        '''excludes_regex = []
        for exc in excludes:
            excludes_regex.append(targetURL + exc + '.*')
        logging.debug("Excluded URLs: " + str(excludes_regex))'''
        bucket_name = config['Output'][0]['S3'][0]['bucket_name'][0]
        bucket_file_name = config['Output'][0]['S3'][1]['bucket_folder'][0] + contextname + '.html'
        selenium_script = config['LoginScript'][0]
        slack_web_hook = config['Reporting'][0]['slack_web_hook'][0]

        print ("Slack Notificaiton Starting:")
        slack("ZAP Scan Starting On: " + targetURL, slack_web_hook)

        # Selenium based authentication.
        logging.info("Calling selenium script: " + str(selenium_script))
        #suite = unittest.TestLoader().loadTestsFromName(str(selenium_script), selenium_scripts)
        #unittest.TextTestRunner(verbosity=2).run(suite)
        try:
            execfile(base_config_dir + "selenium/" + selenium_script)
        except SystemExit:
            logging.info("Caught system exit coming back from selenium script.")
            pass

        # ZAP configuration settings:
        # 1. Defining context name as hostname from targetURL and creating context using it.
        logging.debug("Context Name: " + contextname)

        # 2. Create context and set it in scope.
        contextid = zap.context.new_context(contextname)
        logging.debug("ContextID: " + contextid)
        result = zap.context.set_context_in_scope(contextname, True)
        logging.debug("Context - " + contextname + " set in scope: " + result)

        # 3. Include list of URLs necessary in the context.
        zap.context.include_in_context(contextname, targetURL_regex)
        if urls_in_context is not None:
            for url in urls_in_context:
                result = zap.urlopen(url)  # Accessing URLs in scope.
                url_regex = url + ".*"
                zap.context.include_in_context(contextname, url_regex)
        logging.debug("Context includes: " + str(zap.context.include_regexs(contextname)))

        # 4. Exclude from spider
        for exc in excludes:
            result = zap.spider.exclude_from_scan(exc)
        logging.debug("Excluded - " + str(excludes) + " from spider: " + result)

        # 5. Session Management - cookieBasedSessionManagement
        result = zap.sessionManagement.set_session_management_method(contextid, "cookieBasedSessionManagement", None)
        logging.debug("Session method defined: " + result)

        # 6. Set log in indicator
        loggedInIndicator = "\Qlogout\E"
        result = zap.authentication.set_logged_in_indicator(contextid, loggedInIndicator)
        logging.debug("Login Indicator - " + loggedInIndicator + "defined: " + result)

        # 7. Create custom scan policy
        policy_obj = CreateScanPolicy()
        ascan_policy = policy_obj.ascan_policy(config)
        logging.info("Active scan policy returned: "+ascan_policy)

        ## Attack:
        # 1. Spider everything included in context.
        spiderId = zap.spider.scan(targetURL, contextname=contextname)
        logging.debug("Crawling through. Spider ID: " + spiderId)
        time.sleep(15)

        # 2. Passive scanning.
        if pscan:
            # Do not Passive Scan if explicitly not requested. Default is requested.
            # Wait for spider to complete.
            logging.debug("Spider scan status: " + str(zap.spider.status(spiderId)))
            while int(zap.spider.status(spiderId)) < 100:
                logging.debug("Waiting 10 more seconds for spider to complete crawling through the website...")
                time.sleep(10)
                logging.debug("Spider status: " + str(zap.spider.status(spiderId)))
            logging.debug('List of URLs obtained by spider : ' + str(zap.spider.full_results(spiderId)))
            # Wait for passive scanning to complete
            while int(zap.pscan.records_to_scan) > 0:
                logging.debug('Records to passive scan : ' + zap.pscan.records_to_scan)
                time.sleep(2)
            logging.debug('Passive scanning complete')

            # 3. Active scanning.
            if ascan:
                # Do not Active Scan if explicitly not requested. Default is requested.
                logging.debug('Actively Scanning target ' + targetURL)
                result = zap.ascan.set_option_thread_per_host(10)
                logging.debug('Running 10 active scanning threads.')
                ascan_id = zap.ascan.scan(targetURL, scanpolicyname= ascan_policy, inscopeonly=True)
                logging.debug("Active scanID: "+ str(ascan_id))
                while int(zap.ascan.status(ascan_id)) < 100:
                    logging.debug('Scan progress %: ' + str(zap.ascan.status(ascan_id)))
                    logging.debug('Scan progress: ' + str(zap.ascan.scan_progress(ascan_id)))
                    time.sleep(30)
                logging.debug('Scan completed')

        # 8. Deleting custom scan policy.
        result = zap.ascan.remove_scan_policy(ascan_policy)

        # Reporting:
        # 1. Generate XML/HTML report. Pending: send report to dojo.
        f_html = open("/home/zap/app_sec_scan/report.html", 'wb')
        f_html.write(zap.core.htmlreport())

        f_xml = open("/home/zap/app_sec_scan/report.xml", 'wb')
        f_xml.write(zap.core.xmlreport())

        # 2. S3 bucket integration.
        print os.environ['AWS_ACCESS_KEY_ID']+' and '+os.environ['AWS_SECRET_ACCESS_KEY']
        s3 = boto3.resource(
            's3',
            aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
            aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY']

        )
        result = s3.Object(bucket_name, bucket_file_name).put(Body=open('/home/zap/app_sec_scan/report.html', 'rb'),
                                                              ServerSideEncryption='AES256')
        logging.debug("Scan report: " + bucket_file_name + " uploaded to S3-bucket: " + str(result))

        # 3. Slack Completion notification
        slack("ZAP scan completed for: " + targetURL + ". Report uploaded to: " + bucket_file_name, slack_web_hook)
