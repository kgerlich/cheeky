#!/bin/bash
# Cheeky Image Build Script
# Customizes DietPi base image with Cheeky-specific software
# Usage: sudo ./build.sh --arch armv8 --base-image base.img --output output.img --version v1.0.0

set -e

# Default values
ARCH="armv8"
BASE_IMAGE=""
OUTPUT_IMAGE=""
VERSION="dev"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --arch)
            ARCH="$2"
            shift 2
            ;;
        --base-image)
            BASE_IMAGE="$2"
            shift 2
            ;;
        --output)
            OUTPUT_IMAGE="$2"
            shift 2
            ;;
        --version)
            VERSION="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Validate arguments
if [ -z "$BASE_IMAGE" ] || [ -z "$OUTPUT_IMAGE" ]; then
    echo "Usage: $0 --arch armv8 --base-image base.img --output output.img --version v1.0.0"
    exit 1
fi

echo "================================"
echo "🍑 Building Cheeky Image"
echo "================================"
echo "Architecture: $ARCH"
echo "Base Image: $BASE_IMAGE"
echo "Output: $OUTPUT_IMAGE"
echo "Version: $VERSION"
echo ""

# Copy base image
echo "[Build] Copying base image..."
cp "$BASE_IMAGE" "$OUTPUT_IMAGE"

# Mount the image
echo "[Build] Setting up mount points..."
LOOP_DEVICE=$(losetup -f)
losetup "$LOOP_DEVICE" "$OUTPUT_IMAGE"

# Find partitions
LOOP_PARTITIONS=$(lsblk -ln "$LOOP_DEVICE" | grep part | awk '{print $1}')
ROOT_PARTITION="/dev/$(echo "$LOOP_PARTITIONS" | tail -1)"

# Create mount directory
MOUNT_POINT=$(mktemp -d)
echo "[Build] Mount point: $MOUNT_POINT"

# Mount root filesystem
echo "[Build] Mounting filesystem..."
mount "$ROOT_PARTITION" "$MOUNT_POINT"

# Setup chroot
echo "[Build] Setting up chroot environment..."
mount --bind /dev "$MOUNT_POINT/dev"
mount --bind /sys "$MOUNT_POINT/sys"
mount --bind /proc "$MOUNT_POINT/proc"

# Copy our scripts and config into the image
echo "[Build] Copying Cheeky files..."
mkdir -p "$MOUNT_POINT/opt/cheeky"
cp -r "$PROJECT_DIR/config" "$MOUNT_POINT/opt/cheeky/"
cp -r "$PROJECT_DIR/docs" "$MOUNT_POINT/opt/cheeky/"

# Run automation script inside chroot
echo "[Build] Running first-boot automation script..."
cat > "$MOUNT_POINT/tmp/run-cheeky-setup.sh" << 'EOF'
#!/bin/bash
set -e
cd /opt/cheeky/config
chmod +x Automation_Custom_Script.sh
./Automation_Custom_Script.sh
EOF

chmod +x "$MOUNT_POINT/tmp/run-cheeky-setup.sh"

# Execute inside chroot
chroot "$MOUNT_POINT" /tmp/run-cheeky-setup.sh || {
    echo "[Build] Warning: Some setup commands failed (may be normal in chroot)"
}

# Customize DietPi config
echo "[Build] Customizing DietPi configuration..."
cat > "$MOUNT_POINT/boot/dietpi.txt" << EOFCONFIG
ROOT_USER_PASSWORD=raspberry
AUTO_SETUP_LOCALE=en_US.UTF-8
AUTO_SETUP_TIMEZONE=UTC
DIETPI_SURVEY_OPTED_OUT=1
AUTO_UNMASK_LOGIND=1
AUTO_SETUP_RUN=1
BOOT_WAIT_FOR_NETWORK=1
CHEEKY_VERSION=$VERSION
EOFCONFIG

# Add WiFi template
cat > "$MOUNT_POINT/boot/dietpi-wifi.txt" << 'EOFWIFI'
# Cheeky WiFi Configuration
# Edit this file BEFORE first boot to auto-configure WiFi
# Uncomment and customize with your network details:

# aWIFI_SSID[0]='YourNetworkName'
# aWIFI_KEY[0]='YourPassword'

# For multiple networks:
# aWIFI_SSID[1]='SecondNetwork'
# aWIFI_KEY[1]='SecondPassword'
EOFWIFI

# Create hostname file
echo "raspberrypi" > "$MOUNT_POINT/etc/hostname"

# Cleanup
echo "[Build] Cleaning up chroot..."
rm -f "$MOUNT_POINT/tmp/run-cheeky-setup.sh"

# Unmount
echo "[Build] Unmounting filesystem..."
umount "$MOUNT_POINT/proc" 2>/dev/null || true
umount "$MOUNT_POINT/sys" 2>/dev/null || true
umount "$MOUNT_POINT/dev" 2>/dev/null || true
umount "$MOUNT_POINT" 2>/dev/null || true
rmdir "$MOUNT_POINT"

# Detach loop device
losetup -d "$LOOP_DEVICE"

echo ""
echo "================================"
echo "✓ Image build complete!"
echo "================================"
echo "Output: $OUTPUT_IMAGE"
echo ""
echo "Next steps:"
echo "  1. Compress: xz -9 $OUTPUT_IMAGE"
echo "  2. Flash to SD: dd if=$OUTPUT_IMAGE of=/dev/sdX bs=4M"
echo "  3. Boot and enjoy!"
echo ""
