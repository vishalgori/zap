#!/usr/bin/env bash
echo "********************************************************************"
echo "Creating Directory for logs and output";
echo "********************************************************************"
mkdir output
echo "================================================================================"
echo "Starting ZAP on this container on port 8080."
echo "================================================================================"
echo ""
echo ""
zap.sh -daemon -host 0.0.0.0 -port 8080 -config api.disablekey=true &
echo "================================================================================"
echo "Waiting for 30 seconds for zap to spawn."
echo "================================================================================"
echo ""
echo ""
sleep 30
echo "================================================================================"
echo "Clone the configuration repo"
echo "================================================================================"
echo ""
echo ""
git clone $CONFIG_REPO /home/zap/security-configurations
sleep 15
echo "================================================================================"
echo "Clone the Dojo-CI-CD repo"
echo "================================================================================"
echo ""
echo ""
git clone https://github.com/aaronweaver/defectdojo_api /home/zap/defectdojo
sleep 15
echo "================================================================================"
echo "Initiating scan."
echo "================================================================================"
echo ""
echo ""
export $TARGET_URL=`python /home/zap/app_sec_scan/scan.py --yml $YAML_CONFIG | tail -1`
echo "================================================================================"
echo "Pushing results to defectdojo."
echo "================================================================================"
echo ""
echo ""
set +e
bash -e <<TRY
  echo "Uploading scan report to defect dojo."
  python /home/zap/defectdojo/examples/dojo_ci_cd.py --product=$PRODUCT_ID --file "/home/zap/app_sec_scan/report.xml" --build=$build --scanner="ZAP Scan" --high=0 --host=$DOJO_HOST --api_key=$DOJO_API_KEY --user=$DOJO_USER
TRY
if [ $? -ne 0 ]; then
  echo "Scan report upload to defect dojo failed"
fi
#python /home/zap/defectdojo/examples/dojo_ci_cd.py --product=$PRODUCT_ID --file "/home/zap/app_sec_scan/output/report.xml" --build=$build --scanner="ZAP Scan" --high=0 --host=$DOJO_HOST --api_key=$DOJO_API_KEY --user=$DOJO_USER
echo "================================================================================"
echo ""
echo ""
echo "********************************************************************"
echo "Copying report and log files to S3"
echo "********************************************************************"
echo ""
echo ""
s3cmd --access_key=$AWS_ACCESS_KEY_ID --secret_key=$AWS_SECRET_ACCESS_KEY put output/*  s3://security-tool-reports/scans/dynamic/zap/$output_dir/ 2>&1 | tee -a $logfile
echo "Complete!"
