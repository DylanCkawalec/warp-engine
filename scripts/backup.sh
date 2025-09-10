#!/usr/bin/env bash
# Backup script for Warp Engine data

set -e

BACKUP_DIR="${1:-backup_$(date +%Y%m%d_%H%M%S)}"

echo "📦 Creating backup: $BACKUP_DIR"
mkdir -p "$BACKUP_DIR"

# Backup data directory
if [ -d "data" ]; then
    echo "  - Backing up data directory..."
    cp -r data "$BACKUP_DIR/"
fi

# Backup agent binaries
if [ -d "bin" ]; then
    echo "  - Backing up agent binaries..."
    cp -r bin "$BACKUP_DIR/"
fi

# Backup registry
if [ -f "data/registry.json" ]; then
    echo "  - Backing up agent registry..."
    cp data/registry.json "$BACKUP_DIR/registry_backup.json"
fi

# Create backup manifest
cat > "$BACKUP_DIR/manifest.txt" << EOF
Warp Engine Backup
Created: $(date)
Version: 2.0.0
Contents:
- Agent registry
- Job history
- Generated agents
- Agent binaries
- Log files

To restore:
1. Stop the service: ./warp-engine-service stop
2. Copy data/ back: cp -r $BACKUP_DIR/data ./
3. Copy bin/ back: cp -r $BACKUP_DIR/bin ./
4. Start the service: ./warp-engine-service start
EOF

echo "✅ Backup complete: $BACKUP_DIR"
echo "📋 Manifest created with restore instructions"
