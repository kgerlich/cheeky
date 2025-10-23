# WiFi Configuration Guide

This guide covers the different methods to configure WiFi on your Cheeky Raspberry Pi.

## Quick Method: Before First Boot (Recommended)

This is the easiest and most reliable method.

### Steps

1. **Flash the image** to your SD card using Raspberry Pi Imager or `dd`
2. **Keep the SD card** in your computer (don't eject it)
3. **Find the boot partition** and open it
4. **Locate and edit** `dietpi-wifi.txt`
5. **Add your WiFi credentials**:
   ```
   aWIFI_SSID[0]='YourNetworkName'
   aWIFI_KEY[0]='YourPassword'
   ```
6. **Eject the SD card** safely
7. **Insert into Pi** and power on
8. Pi will auto-connect on first boot

### Encoding Credentials

If you have special characters in your WiFi name or password, they may need to be encoded:

- Replace spaces with underscores or escape them
- Example: Network name "My WiFi 5G" becomes `My_WiFi_5G` or `My\\ WiFi\\ 5G`

### Multiple Networks

You can add multiple WiFi networks:

```
aWIFI_SSID[0]='HomeNetwork'
aWIFI_KEY[0]='HomePassword'

aWIFI_SSID[1]='GuestNetwork'
aWIFI_KEY[1]='GuestPassword'

aWIFI_SSID[2]='WorkNetwork'
aWIFI_KEY[2]='WorkPassword'
```

The Pi will try each network in order until it successfully connects.

## Method 2: Raspberry Pi Imager (Modern Way)

If you're using a recent version of Raspberry Pi Imager, you can configure WiFi during flashing:

1. **Open Raspberry Pi Imager**
2. **Select your image** (the Cheeky `.img.xz` file)
3. **Select your SD card**
4. **Click the gear icon** for Advanced Options
5. **Enable WiFi** and enter:
   - SSID (network name)
   - Password
   - WiFi country (your region)
6. **Click Write**
7. Imager will embed your WiFi credentials in the image

This is the most user-friendly method if your Imager version supports it.

## Method 3: After First Boot (With Ethernet)

If you want to configure WiFi after the Pi is running:

### Requirements
- Ethernet cable connected to Pi
- Computer on same network

### Steps

1. **Boot the Pi** with Ethernet connected
2. **Wait 2 minutes** for services to start
3. **SSH into the Pi**:
   ```bash
   ssh root@raspberrypi.local
   # or: ssh root@192.168.1.X (your Pi's IP)
   # Password: raspberry
   ```

4. **Run DietPi Config**:
   ```bash
   dietpi-config
   ```

5. **Navigate to**: Network Options → WiFi
6. **Enter your credentials**
7. **Reboot**:
   ```bash
   reboot
   ```

## Method 4: Using dietpi-wifi.txt After Flashing

If your SD card was already in the Pi and you need to add WiFi:

1. **Power off the Pi** and remove SD card
2. **Insert SD card** into computer
3. **Edit `/boot/dietpi-wifi.txt`** as described in Method 1
4. **Eject and reinserert** the SD card into the Pi
5. **Power on** the Pi

The next time it boots, it will try to connect with the new credentials.

## Troubleshooting WiFi Issues

### Pi won't connect after boot

- **Double-check credentials**: Ensure SSID and password are exactly correct (case-sensitive)
- **Check syntax**: Make sure the `aWIFI_SSID[0]='...'` format is correct
- **Try Ethernet first**: Connect via Ethernet to verify the Pi works, then configure WiFi via SSH
- **Check WiFi strength**: Some weak signals can cause connection failures

### Can't find dietpi-wifi.txt

The file is in the boot partition:
- **Linux**: Mount the boot partition manually
- **Windows**: May appear as a separate drive when SD card is inserted
- **macOS**: Use Finder to navigate to the boot partition

### WiFi connects but no internet

- Check your router's internet connection
- Ensure the Pi's IP address is in the correct range (192.168.1.X for most home networks)
- Try restarting both the Pi and your WiFi router

### Need to change WiFi network later

You can always SSH into your Pi and use `dietpi-config` to change networks:

```bash
ssh root@raspberrypi.local
dietpi-config
# Navigate: Network Options → WiFi
```

## Hidden Networks (SSID Not Broadcast)

If your WiFi network is hidden, you can still connect:

```
aWIFI_SSID[0]='YourHiddenNetworkName'
aWIFI_KEY[0]='YourPassword'
aWIFI_HIDDEN[0]=1
```

The `aWIFI_HIDDEN[0]=1` line tells DietPi that this network doesn't broadcast its SSID.

## Staying Connected

Once configured, Cheeky will:
- ✅ Auto-connect on boot
- ✅ Auto-reconnect if connection drops
- ✅ Prioritize networks by order in dietpi-wifi.txt
- ✅ Remember settings across reboots

## Security Recommendations

- 🔒 Change the default SSH password on first login: `passwd`
- 🔒 Use WPA2 or WPA3 encryption for your WiFi (don't use WEP)
- 🔒 Keep your Cheeky Pi on a private/trusted network

## Advanced: Using Ethernet Only

If you prefer not to use WiFi:

1. **Skip WiFi configuration** in all methods above
2. **Connect Ethernet cable** to your Pi and router
3. **Boot normally** - Ethernet will be auto-configured by DHCP
4. **Access web interfaces** normally via `raspberrypi.local`

This is actually more reliable than WiFi if you can run a cable.

---

🍑 Once WiFi is working, enjoy your Cheeky radio!

For issues, see [Troubleshooting Guide](TROUBLESHOOTING.md) or [open an issue on GitHub](https://github.com/cheeky-radio/cheeky/issues).
