#!/usr/local/bin/python

import logging
import os
import schedule
import subprocess
import tempfile
import time

from google.cloud import storage

# Set up logging
logging.basicConfig(format = '%(asctime)s %(message)s', level = logging.INFO)

# Upload file to google cloud storage

# Authentication is done via a service account keyfiles. Default location is
# /etc/creds.json. Customise via GOOGLE_APPLICATION_CREDENTIALS environment variable
# Set the bucket to store backups in via BUCKET

BUCKET = os.environ.get('BUCKET')

class GCS:
    def __init__(self, bucket, keep = 5):
        self.keep = keep
        self.storage = storage.Client()

        if not self.storage.lookup_bucket(bucket):
            logging.critical("ERROR: bucket does not exist [%s]" % bucket)
            exit(1)
        else:
            self.bucket = self.storage.get_bucket(bucket)

    def upload(self, f, upload_name):
        blob = storage.Blob(upload_name, self.bucket)
        logging.info("Uploading backup to %s%s" % (self.bucket, upload_name))
        blob.upload_from_file(f, rewind=True)

    def cleanup(self, prefix = ""):
        backups = list(self.bucket.list_blobs(prefix = prefix))
        to_delete = backups[:max(0, len(backups) - self.keep)]
        for backup in to_delete:
            backup.delete()

# How often to run backup
EVERY_N_DAYS  = int(os.environ.get('EVERY_N_DAYS', 1)) # default to once a day
AT_TIME       = os.environ.get('AT_TIME', "00:00") # at midnight

# DB configuration options
HOST      = os.environ.get('MYSQL_HOST', 'localhost')
PORT      = os.environ.get('MYSQL_PORT', '3306')
USERNAME  = os.environ.get('MYSQL_USER')
PASSWORD  = os.environ.get('MYSQL_PASSWORD')
DB        = os.environ.get('MYSQL_DATABASE')

cloud = GCS(BUCKET)

def backup():
    backup_name = "%s/%s-%s.sql" % (DB, DB, time.strftime("%Y-%m-%d-%H%M%S"))
    logging.info("Running backup %s" % backup_name)
    with tempfile.NamedTemporaryFile() as f:
        subprocess.run([
            "mysqldump",
            "--host=%s" % HOST,
            "--port=%s" % PORT,
            "--user=%s" % USERNAME,
            "--password=%s" % PASSWORD,
            DB], stdout = f)

        cloud.upload(f, backup_name)

    cloud.cleanup()

schedule.every(EVERY_N_DAYS).days.at(AT_TIME).do(backup)
while True:
    schedule.run_pending()
    time.sleep(30)
