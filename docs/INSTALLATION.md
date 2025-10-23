# Installation Guide for Cheeky

This guide covers how to install and set up Cheeky on your Raspberry Pi.

## For Physical Raspberry Pi

### Step 1: Download the Image

Choose the image for your Pi model from the [GitHub Releases page](https://github.com/cheeky-radio/cheeky/releases):

| Your Pi | Download |
|---------|----------|
| Pi Zero 2 W, Pi 3, Pi 4, Pi 5 | `cheeky-armv8-v*.img.xz` |
| Pi 2 | `cheeky-armv7-v*.img.xz` |
| Pi Zero W, Pi 1 | `cheeky-armv6-v*.img.xz` |

### Step 2: Flash to SD Card

**Option A: Using Raspberry Pi Imager (Recommended)**

1. Download [Raspberry Pi Imager](https://www.raspberrypi.com/software/)
2. Open Raspberry Pi Imager
3. Choose "Custom Image"
4. Select the downloaded `cheeky-*.img.xz` file
5. Select your SD card
6. Click "Write"
7. (Optional) In Advanced Options, configure WiFi before flashing

**Option B: Command Line**

```bash
# Extract the image
xz -d cheeky-armv8-v1.0.0.img.xz

# Flash to SD card (replace sdX with your card)
sudo dd if=cheeky-armv8-v1.0.0.img of=/dev/sdX bs=4M status=progress
sync
```

### Step 3: Configure WiFi (Optional)

If you didn't configure WiFi with Raspberry Pi Imager, you can add it before first boot:

1. Keep the SD card in your computer after flashing
2. Open the `boot` partition
3. Edit `dietpi-wifi.txt`
4. Add your WiFi credentials:
   ```
   aWIFI_SSID[0]='YourNetworkName'
   aWIFI_KEY[0]='YourPassword'
   ```
5. Eject the SD card

See [WiFi Setup Guide](WIFI-SETUP.md) for more options.

### Step 4: Boot Your Pi

1. Insert the SD card into your Pi
2. Power on your Pi
3. Wait approximately 2 minutes for first boot
4. The system will automatically:
   - Expand the filesystem
   - Configure services
   - Start Mopidy (radio server)
   - Start Bluetooth manager

### Step 5: Access the Web Interfaces

Once your Pi is on the network, access:

- **Radio Interface**: http://raspberrypi.local:6680
- **Bluetooth Manager**: http://raspberrypi.local:8080

(Replace `raspberrypi` with your Pi's hostname if you changed it)

## For QEMU (Testing Without Hardware)

See [QEMU Testing Guide](QEMU.md)

## Troubleshooting

### Can't find the Pi on network

- Check your Pi is powered on (green LED should be lit)
- Ensure your computer is on the same network
- Try accessing by IP address instead:
  - On your router, find the Pi's IP (usually looks like 192.168.1.X)
  - Visit `http://192.168.1.X:6680`

### Web interfaces won't load

- Wait a full 2 minutes after power-on (first boot is slower)
- Try clearing browser cache (Ctrl+Shift+Delete)
- Try a different browser
- Check if services are running (see SSH access below)

### Bluetooth speaker won't pair

- Ensure speaker is in pairing mode
- Check it's not already paired with another device
- Try scanning again
- See [Troubleshooting Guide](TROUBLESHOOTING.md)

### SSH Access (For Advanced Users)

You can SSH into your Pi if needed:

```bash
ssh root@raspberrypi.local
# Default password: raspberry
# Change it on first login!
```

## Next Steps

1. **Pair a Bluetooth speaker** via the web interface at port 8080
2. **Browse radio stations** at port 6680
3. **Configure settings** via SSH if you need advanced customization

## Support

- 🐛 [Report issues](https://github.com/cheeky-radio/cheeky/issues)
- 💬 [Ask questions](https://github.com/cheeky-radio/cheeky/discussions)
- 📖 [Read troubleshooting guide](TROUBLESHOOTING.md)

---

🍑 Don't take radio too seriously. Be cheeky.
