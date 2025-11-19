#!/bin/bash
set -e

DB_PATH=/data/db
KEYFILE_PATH=$DB_PATH/mongo-keyfile
LOG_PATH=$DB_PATH/mongo.log
SOCIAL_DATA_FILE=/scripts/social_media_data.json
POLICY_FILE=/scripts/policies.json
DB_NAME="research_db"

# -------------------------------
# Generate keyfile if missing
# -------------------------------
if [ ! -f "$KEYFILE_PATH" ]; then
  echo "Generating keyfile..."
  openssl rand -base64 756 > "$KEYFILE_PATH"
  chmod 600 "$KEYFILE_PATH"
fi

# -------------------------------
# Start MongoDB without auth
# -------------------------------
echo "Starting MongoDB without auth..."
mongod --replSet rs0 --bind_ip_all --dbpath "$DB_PATH" --logpath "$LOG_PATH" &
MONGO_PID=$!

# Wait until Mongo is ready
until mongosh --quiet --eval "db.adminCommand('ping')" >/dev/null 2>&1; do sleep 2; done

# -------------------------------
# Initialize replica set
# -------------------------------
echo "Initializing replica set..."
mongosh --quiet --eval 'try { rs.status() } catch(e) { rs.initiate({_id:"rs0", members:[{_id:0, host:"mongo:27017"}]}) }'

# Wait until PRIMARY
until mongosh --quiet --eval 'rs.isMaster().ismaster' | grep -q "true"; do sleep 2; done

# -------------------------------
# Create admin user
# -------------------------------
echo "Creating admin user..."
mongosh --quiet <<EOF
use admin
try { db.createUser({user: "admin", pwd: "secret", roles: ["root"]}); } catch(e) { }
EOF

# -------------------------------
# Create application user
# -------------------------------
echo "Creating research project user..."
mongosh --quiet <<EOF
use admin
try { db.createUser({user: "research_user", pwd: "research_pass", roles: [{ role: "readWrite", db: "$DB_NAME" }]}); } catch(e) { }
EOF

# -------------------------------
# Import Social Media Data
# -------------------------------
if [ -f "$SOCIAL_DATA_FILE" ]; then
  echo "Importing social media data..."
  mongosh --quiet <<EOF
use $DB_NAME
try {
  const fs = require('fs');
  const data = JSON.parse(fs.readFileSync('$SOCIAL_DATA_FILE', 'utf8'));
  if (db.social_media_data.countDocuments() === 0) {
    db.social_media_data.insertMany(data);
  }
} catch(e) { print(e); }
EOF
fi

# -------------------------------
# Import Stock Market Interactions Data (Policies)
# -------------------------------
if [ -f "$POLICY_FILE" ]; then
  echo "Importing stock market interactions..."
  mongosh --quiet <<EOF
use $DB_NAME
try {
  const fs = require('fs');
  const data = JSON.parse(fs.readFileSync('$POLICY_FILE', 'utf8'));
  if (db.stock_interactions.countDocuments() === 0) {
    db.stock_interactions.insertMany(data);
  }
} catch(e) { print(e); }
EOF
fi

# -------------------------------
# Create indexes
# -------------------------------
echo "Creating indexes..."
mongosh --quiet <<EOF
use $DB_NAME
db.social_media_data.createIndex({ timestamp: 1 });
db.social_media_data.createIndex({ source: 1 });
db.stock_interactions.createIndex({ timestamp: 1 });
db.stock_interactions.createIndex({ source: 1 });
EOF

# -------------------------------
# Stop temporary mongod
# -------------------------------
kill $MONGO_PID
wait $MONGO_PID 2>/dev/null || true

# -------------------------------
# Start MongoDB with auth
# -------------------------------
exec mongod --replSet rs0 --bind_ip_all --dbpath "$DB_PATH" --logpath "$LOG_PATH" --keyFile "$KEYFILE_PATH" --auth
