from zapv2 import ZAPv2
import yaml
import time
import logging

class CreateScanPolicy:
    def ascan_policy(self,config):
        zap=ZAPv2()
        ascan_policy = "Custom"+str(time.time())
        zap.ascan.add_scan_policy(ascan_policy)
        zap.ascan.disable_all_scanners(ascan_policy)
        select_plugin = config['Scan_Policy'][0]['option_scan_policy_file'][0]

        profile = yaml.load(
            open("/home/zap/security-configurations/config/zap/"+select_plugin))
        logging.info("Scan profile: "+str(profile))

        for i in range(0,len(profile['scanners'])):
            if profile['scanners'][i]['enabled'] == 'true':
                zap.ascan.enable_scanners(profile['scanners'][i]['id'],
                                          ascan_policy)
                zap.ascan.set_scanner_alert_threshold(profile['scanners'][i]['id'],
                                                          profile['scanners'][i]['alertThreshold'],
                                                          ascan_policy)
                zap.ascan.set_scanner_attack_strength(profile['scanners'][i]['id'],
                                              profile['scanners'][i]['attackStrength'],
                                              ascan_policy)
        logging.debug("Active scan policy: "+ascan_policy)
        return ascan_policy

if __name__ == '__main__':
    policy_obj = CreateScanPolicy()
    config = yaml.load(open("")) ##Is this necessary?
    log_file_name = "/home/zap/zap" + str(time.time()) + ".txt"
    logging.basicConfig(filename=log_file_name, level=logging.DEBUG)
    ascan_policy = policy_obj.ascan_policy(config,log_file_name)
    logging.info("Active scan policy: "+str(ascan_policy))
    #pscan_policy = policy_obj.pscan_policy()
