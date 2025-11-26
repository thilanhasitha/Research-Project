#!/bin/bash
set -e

DB_PATH=/data/db
LOG_PATH=$DB_PATH/mongo.log
KEYFILE_PATH=$DB_PATH/mongo-keyfile

# -------------------------------
# Step 0: Generate keyfile (optional)
# -------------------------------
if [ ! -f "$KEYFILE_PATH" ]; then
  echo "Generating keyfile..."
  openssl rand -base64 756 > "$KEYFILE_PATH"
  chmod 600 "$KEYFILE_PATH"
fi

# -------------------------------
# Step 1: Start MongoDB without auth
# -------------------------------
echo "Starting MongoDB (no auth) for initialization..."
mongod --replSet rs0 --bind_ip_all --dbpath "$DB_PATH" --logpath "$LOG_PATH" &
MONGO_PID=$!

# Wait until MongoDB is ready
echo "Waiting for MongoDB to be ready..."
until mongosh --quiet --eval "db.adminCommand('ping')" >/dev/null 2>&1; do
  sleep 2
done

# -------------------------------
# Step 2: Initialize replica set
# -------------------------------
echo "Initializing replica set..."
mongosh --quiet --eval '
try { rs.status() } 
catch(e) { rs.initiate({_id:"rs0", members:[{_id:0, host:"localhost:27017"}]}) }
'

until mongosh --quiet --eval 'rs.isMaster().ismaster' | grep -q "true"; do
  sleep 2
done

# -------------------------------
# Step 3: Create user for research_db
# -------------------------------
echo "Creating user for research_db..."
mongosh --quiet <<EOF
use research_db
if (!db.getUser("research")) {
  db.createUser({
    user: "research",
    pwd: "user",
    roles: [{ role: "readWrite", db: "research_db" }]
  })
  print("User 'research' created successfully")
} else {
  print("User 'research' already exists")
}
EOF

# -------------------------------
# Step 4: Stop init mongod
# -------------------------------
echo "Stopping initial MongoDB..."
kill $MONGO_PID
wait $MONGO_PID 2>/dev/null || true

# -------------------------------
# Step 5: Start MongoDB with keyfile authentication
# -------------------------------
echo "Starting MongoDB with keyfile authentication..."
exec mongod --replSet rs0 --bind_ip_all --dbpath "$DB_PATH" --logpath "$LOG_PATH" --keyFile "$KEYFILE_PATH" --auth
