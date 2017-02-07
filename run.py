#!/usr/local/bin/python

import os
import sched
import subprocess
import tempfile
import time

from google.cloud import storage

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
            print("ERROR: bucket does not exist [%s]" % bucket)
            exit(1)
        else:
            self.bucket = self.storage.get_bucket(bucket)

    def upload(self, f, upload_name):
        blob = storage.Blob(upload_name, self.bucket)
        print("Uploading backup to %s%s" % (self.bucket, upload_name))
        blob.upload_from_file(f, rewind=True)

    def cleanup(self, prefix = ""):
        backups = list(self.bucket.list_blobs(prefix = prefix))
        to_delete = backups[:max(0, len(backups) - self.keep)]
        for backup in to_delete:
            backup.delete()

# How often to run backup
scheduler = sched.scheduler(time.time, time.sleep)
DELAY     = int(os.environ.get('EVERY', 60 * 60 * 12)) # default to once a day

# DB configuration options
HOST      = os.environ.get('MYSQL_HOST', 'localhost')
PORT      = os.environ.get('MYSQL_PORT', '3306')
USERNAME  = os.environ.get('MYSQL_USER')
PASSWORD  = os.environ.get('MYSQL_PASSWORD')
DB        = os.environ.get('MYSQL_DATABASE')

cloud = GCS(BUCKET)

def backup():
    backup_name = "%s/%s-%s.sql" % (DB, DB, time.strftime("%Y-%m-%d-%H%M%S"))
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

while True:
    print("running every %s(s)" % DELAY)
    scheduler.enter(DELAY, 1, backup, ())
    scheduler.run()
