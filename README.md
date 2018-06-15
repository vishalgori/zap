# DYNAMIC AUTHENTICATED SCAN USING DOCKER AND ZAP
This project aims at automating the process of authenticated dynamic application scanning and making it platform independent by the use of docker.

## Getting started
This project uses the latest OWASP ZAP docker available on docker hub called owasp/zap2docker-weekly.

#### Pre-requisites

* Create selenium scripts using selenium web driver for your application's authentication inside "selenium_scripts" folder.  
Example:  
``
selenium_scripts/BodgeitTestUser_v1.py
``
* Install Docker engine.  
Refer:  
``
https://docs.docker.com/engine/getstarted/
``
* Needs defectdojo running. Specify required details for reporting on dojo in `/zap/app_sec_scan/run.sh`. More details about defectdojo and defectdojo-API here: [https://github.com/OWASP/django-DefectDojo, https://github.com/aaronweaver/defectdojo_api]
* AWS access keys to be passed as parameters before running `re-build.sh` or `docker run`. If running in AWS environment you can use IAM roles instead so you dont need to specify keys.
* config.yml needs to be updated for specific configuration settings. Also, change the yml filename in `config_parser.py` specific to the app.
* Define scan policy file from security-configuration (http://stash.corp.web:7990/projects/SEC/repos/security-configurations/browse/config/zap) needs to be updated to select specific scan plugins to be used for active scanning. You can specify the intensity as well.

#### Run
```
./re-build_docker.sh
```
OR
```
docker run -p 8080:8080 -it -e AWS_ACCESS_KEY_ID=$ID -e AWS_SECRET_ACCESS_KEY=$KEY --name zapauth zapauth /bin/bash -c '/home/zap/app_sec_scan/run.sh'
```

#### Features
* Select specific ZAP plugin for active scanning. [Use _Application__config.yml_ to specify which plugin to use. Manage plugin configurations in **security-configurations** directory.]
* Slack app integration.
* Upload report to dojo. [Specify dojo details by passing them as parameters in run.sh against dojo_ci_cd.py]
* Provide option to select only passive OR active scanning. [Use config.yml]

## Future scope
* Slack outgoing webhook / slackbot / ecs-watchbot.
* Send link to dojo and s3 report via slack. 
* Check if authentication was successful at various levels. Including spider and active scan.
* Spider for login URL. Once found use it as loginURL parameter for authentication.
* Set or select new api key everytime (replacing current static key) using -config api.key=change-me-9203935709 using random() function.
* Password vault for ID:KEY environment variables.

## Contributing
* Vishal Gori <vishal.gori@cengage.com>
* Aaron Weaver <aaron.weaver@cengage.com>

## Authors
* **Vishal Gori** <vishal.gori@cengage.com>
* **Aaron Weaver** <aaron.weaver@cengage.com>

## License
This project is licensed under the Apache2.0 License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgements
