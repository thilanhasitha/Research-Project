#!/bin/bash

# Generate keyfile for replica set
openssl rand -base64 756 > /data/keyfile
chmod 400 /data/keyfile
chown mongodb:mongodb /data/keyfile

# Start MongoDB in background
mongod --bind_ip_all --replSet rs0 --keyFile /data/keyfile &

# Wait for MongoDB to start
sleep 5

# Initialize replica set
mongosh -u research -p user --authenticationDatabase admin <<EOF
rs.initiate({
  _id: "rs0",
  members: [{ _id: 0, host: "mongo:27017" }]
})
EOF

# Keep container running
wait
