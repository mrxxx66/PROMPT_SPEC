#!/system/bin/sh
# Create whitelist directory and file
mkdir -p /data/adb/modules/hyperos_sf_bypass
touch /data/adb/modules/hyperos_sf_bypass/whitelist.txt

# Set proper permissions
chmod 666 /data/adb/modules/hyperos_sf_bypass/whitelist.txt
chmod 755 /data/adb/modules/hyperos_sf_bypass