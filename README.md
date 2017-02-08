# Docker Cloud Bacukp

This container is meant to run as a sidecar to a database container which periodically
takes a mysqldump and pushes it to google cloud storage.

It can be configured using the environment variables:
  - `MYSQL_HOST` - defaults to `localhost`
  - `MYSQL_PORT` - defaults to `3306`
  - `MYSQL_DATABASE`
  - `MYSQL_USER`
  - `MYSQL_PASSWORD`
  - `BUCKET` - Bucket to save dumps to. Must be writable with given credentials
  - `EVERY_N_DAYS` - defaults to 1 (i.e., every day)
  - `AT_TIME` - defaults to 00:00 (midnight)
  - `KEEP` - Number of backups to keep. Defaults to 5

## Google cloud storage authentication

The Google cloud storage api expects a service account credentials file to exist at
`/etc/creds.json`. This can be customised by setting the
`GOOGLE_APPLICATION_CREDENTIALS` enviroment variable to point to wherever the creds file
is.

## Example kubernetes yaml

```json
# ===========================================
# Database deployment, service, and storage
# ===========================================
apiVersion: extensions/v1beta1
kind: Deployment
metadata:
  name: db
spec:
  replicas: 1
  template:
    metadata:
      labels:
        name: db
    spec:
      containers:
        - name: db
          image: mysql:5.7
          env:
            - name: MYSQL_RANDOM_ROOT_PASSWORD
              value: "yes"
            - name: MYSQL_DATABASE
              value: test
            - name: MYSQL_USER
              value: test
            - name: MYSQL_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: secrets
                  key: mysql-password
        - name: backup
          image: cloud-backup:0.1.0
          volumeMounts:
            - name: sa-keys
              mountPath: /etc/sa-keys
          env:
            - name: MYSQL_DATABASE
              value: test
            - name: MYSQL_USER
              value: test
            - name: MYSQL_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: secrets
                  key: mysql-password
            - name: BUCKET
              value: db-backups
            - name: GOOGLE_APPLICATION_CREDENTIALS
              value: /etc/sa-keys/backup-creds.json
        volumes:
          - name: sa-keys
            secret:
              secretName: sa-keys
```
