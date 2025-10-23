# Troubleshooting Guide

## Common Issues & Solutions

### Web Interfaces Won't Load

**Issue**: Can't reach http://raspberrypi.local:6680 or :8080

**Checklist**:
- [ ] Pi is powered on (green LED should be lit)
- [ ] You've waited 2+ minutes after power-on (first boot is slow)
- [ ] Pi is on the same network as your computer
- [ ] Try IP address instead: `http://192.168.1.X:6680` (find X on your router)
- [ ] Try clearing browser cache (Ctrl+Shift+Delete)

**Solutions**:
```bash
# Find Pi's IP address
ping raspberrypi.local

# If that fails, check your router's connected devices
# Look for an entry named "DietPi" or with MAC starting with b8:27:eb:

# SSH in to check services are running
ssh root@raspberrypi.local
systemctl status mopidy
systemctl status cheeky-bluetooth-manager
```

---

### Bluetooth Speaker Won't Pair

**Issue**: Can't pair Bluetooth speaker via web interface

**Checklist**:
- [ ] Speaker is in pairing mode
- [ ] Speaker isn't already paired with another device
- [ ] Bluetooth adapter is enabled on Pi
- [ ] Speaker has sufficient battery

**Solutions**:
```bash
# SSH into Pi
ssh root@raspberrypi.local

# Check Bluetooth adapter
bluetoothctl
> show
> power on  # If powered off
> quit

# Manually pair and connect
bluetoothctl
> scan on
> # Wait for your speaker to appear
> pair <device-mac>
> connect <device-mac>
> quit
```

**Still won't pair?**
- Try unplugging speaker and plugging back in
- Try restarting Bluetooth daemon: `systemctl restart bluetooth`
- Check speaker is compatible (most modern speakers work)

---

### Bluetooth Speaker Auto-Disconnect

**Issue**: Speaker disconnects randomly or doesn't reconnect after reboot

**Solutions**:
```bash
# SSH in and check auto-reconnect script
ssh root@raspberrypi.local
systemctl status cheeky-bluetooth-reconnect

# View logs
journalctl -u cheeky-bluetooth-reconnect -n 50

# Manually reconnect
bluetoothctl
> connect <device-mac>
> quit
```

**Workaround**: Manually reconnect from web interface (port 8080)

---

### No Audio Output

**Issue**: Sound isn't coming from speaker

**Checklist**:
- [ ] Speaker is connected (shows in Bluetooth Manager)
- [ ] Volume is above 0% in web interface
- [ ] Speaker itself has volume turned up
- [ ] Check PulseAudio is running

**Solutions**:
```bash
# SSH in
ssh root@raspberrypi.local

# Check PulseAudio is running
systemctl status pulseaudio

# Check audio volume
pactl list sinks | grep "Name:\|Volume:"

# Set volume to 100%
pactl set-sink-volume 0 100%

# Check which sink is active
pactl get-default-sink
```

---

### WiFi Won't Connect

**Issue**: Pi won't connect to WiFi

**Checklist**:
- [ ] WiFi credentials are correct (case-sensitive!)
- [ ] Router is broadcasting WiFi (not hidden, or configured properly)
- [ ] Pi is in range of router
- [ ] Only tried one network
- [ ] Credentials don't have special characters causing issues

**Solutions**:
```bash
# SSH via Ethernet if you have it
ssh root@raspberrypi.local

# Check available networks
nmcli device wifi list

# Connect to WiFi manually
nmcli device wifi connect "NetworkName" password "Password"

# View connection status
nmcli connection show

# Check WiFi config file
cat /etc/wpa_supplicant/wpa_supplicant.conf
```

**Reconfigure WiFi**:
```bash
# Use DietPi config
dietpi-config
# Navigate: Network Options → WiFi → Select network → Enter password
```

---

### Pi Boot Takes Too Long

**Issue**: Takes more than 2-3 minutes to boot

**Checklist**:
- [ ] This is first boot (first boot expands filesystem, takes longer)
- [ ] SD card isn't corrupted
- [ ] Pi has sufficient power (check with PSU appropriate for your model)
- [ ] Not too many services configured to auto-start

**Solutions**:
```bash
# SSH in
ssh root@raspberrypi.local

# Check boot messages
dmesg | tail -50

# Check services that auto-start
systemctl list-unit-files | grep enabled

# Disable unnecessary services if needed
systemctl disable service-name
```

---

### "Connection Refused" on Port 6680 or 8080

**Issue**: Error when trying to access http://raspberrypi.local:6680

**Solutions**:
```bash
# SSH in
ssh root@raspberrypi.local

# Check if Mopidy is running
systemctl status mopidy
# If not running: systemctl start mopidy

# Check if FastAPI is running
systemctl status cheeky-bluetooth-manager
# If not running: systemctl start cheeky-bluetooth-manager

# Check if ports are listening
netstat -tlnp | grep :6680
netstat -tlnp | grep :8080

# Check logs
journalctl -u mopidy -n 100
journalctl -u cheeky-bluetooth-manager -n 100
```

---

### Radio Stations Won't Play

**Issue**: Can browse stations but playback doesn't work

**Solutions**:
```bash
# SSH in
ssh root@raspberrypi.local

# Check Mopidy logs
journalctl -u mopidy -n 100 | grep -i error

# Verify TuneIn extension is loaded
systemctl status mopidy  # Should mention TuneIn

# Restart Mopidy
systemctl restart mopidy
```

---

### Very Slow Web Interface

**Issue**: Web pages take a long time to load

**Checklist**:
- [ ] Network connection is stable (not too far from router)
- [ ] No other heavy network traffic
- [ ] Browser has JavaScript enabled
- [ ] Pi isn't overheating (check temperature: `vcgencmd measure_temp`)

**Solutions**:
```bash
# Check if Pi is resource-constrained
ssh root@raspberrypi.local
top -b -n 1 | head -20

# Check disk space
df -h

# Check RAM usage
free -h

# Monitor temperatures
vcgencmd measure_temp  # Should be <80°C

# Restart services if stuck
systemctl restart mopidy
systemctl restart cheeky-bluetooth-manager
```

---

### SSH Connection Refused

**Issue**: `ssh root@raspberrypi.local` fails

**Checklist**:
- [ ] Pi is powered on and booted
- [ ] You're on the same network
- [ ] SSH is enabled (should be by default)

**Solutions**:
```bash
# Try using IP address instead
ssh root@192.168.1.X  # Find X on your router

# Check if SSH daemon is running
ssh -v root@raspberrypi.local  # Shows verbose output

# If Pi is unreachable, reboot it:
# 1. Power off and on
# 2. Wait 2 minutes
# 3. Try again
```

---

### Default Password Doesn't Work

**Issue**: "root/raspberry" password fails to SSH

**Checklist**:
- [ ] You're using username `root` (not `pi` or `dietpi`)
- [ ] Default password is `raspberry` (case-sensitive)
- [ ] You've changed the password and forgot it

**If you forgot the password**:
- Reflash the SD card (erases everything)
- Or restore from backup if you have one
- No way to recover lost root password without reflashing

---

### QEMU-Specific Issues

### QEMU Won't Start

**Error**: "qemu-system-aarch64: command not found"

**Solution**: Install QEMU for your OS (see [QEMU Guide](QEMU.md))

### QEMU is Very Slow

**Normal**: Emulation is inherently slower than real hardware

**Tips**:
- Allocate more RAM: Edit `start-qemu.sh`, change `-m 2048` to `-m 4096`
- Close other applications
- Use Linux host (faster than macOS/Windows for ARM emulation)

### Can't Download Image in QEMU

**Issue**: `start-qemu.sh` fails to download image

**Solutions**:
```bash
# Check internet connection
ping github.com

# Manually download
wget https://github.com/cheeky-radio/cheeky/releases/download/v1.0.0/cheeky-armv8-v1.0.0.img.xz

# Extract
xz -d cheeky-armv8-v1.0.0.img.xz

# Run QEMU script again (it will find the image)
./start-qemu.sh
```

---

## Getting Help

If your issue isn't listed above:

1. **Check logs**: SSH in and run relevant systemctl commands above
2. **Search issues**: [GitHub Issues](https://github.com/cheeky-radio/cheeky/issues)
3. **Ask the community**: [GitHub Discussions](https://github.com/cheeky-radio/cheeky/discussions)
4. **Report a bug**: [Open a new issue](https://github.com/cheeky-radio/cheeky/issues/new)

When reporting issues, include:
- Your Pi model and OS
- Steps to reproduce
- Error messages (copy from logs or web interface)
- What you've already tried

---

## Common Commands Reference

```bash
# Check service status
systemctl status mopidy
systemctl status cheeky-bluetooth-manager
systemctl status bluetooth

# View logs
journalctl -u mopidy -n 50
journalctl -u cheeky-bluetooth-manager -n 50

# Restart services
systemctl restart mopidy
systemctl restart cheeky-bluetooth-manager

# Network info
ip addr show
nmcli connection show
nmcli device wifi list

# System info
uname -a
vcgencmd measure_temp
df -h
free -h

# Bluetooth
bluetoothctl
> show
> list
> devices
> connect <mac>
```

---

🍑 Having trouble? Be cheeky about it—ask for help!

[Report issue →](https://github.com/cheeky-radio/cheeky/issues)
