# Cheeky 🍑

```
 ██████╗██╗  ██╗███████╗███████╗██╗  ██╗██╗   ██╗
██╔════╝██║  ██║██╔════╝██╔════╝██║ ██╔╝╚██╗ ██╔╝
██║     ███████║█████╗  █████╗  █████╔╝  ╚████╔╝ 
██║     ██╔══██║██╔══╝  ██╔══╝  ██╔═██╗   ╚██╔╝  
╚██████╗██║  ██║███████╗███████╗██║  ██╗   ██║   
 ╚═════╝╚═╝  ╚═╝╚══════╝╚══════╝╚═╝  ╚═╝   ╚═╝   
```

**A cheeky little internet radio for your Raspberry Pi**

[![Build Status](https://github.com/cheeky-radio/cheeky/workflows/Build%20and%20Release/badge.svg)](https://github.com/cheeky-radio/cheeky/actions)
[![Latest Release](https://img.shields.io/github/v/release/cheeky-radio/cheeky)](https://github.com/cheeky-radio/cheeky/releases/latest)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://img.shields.io/github/downloads/cheeky-radio/cheeky/total)](https://github.com/cheeky-radio/cheeky/releases)

---

## What's Cheeky?

Look, we know the name is a bit silly. But hear us out - **Cheeky** makes setting up a Raspberry Pi internet radio as easy as... well, pie.

Flash an SD card, boot your Pi, and you're listening to **100,000+ radio stations** via TuneIn within 2 minutes. Control everything from a slick web interface, pair your Bluetooth speaker without touching SSH, and never take radio too seriously again.

### Features

- 🎵 **100,000+ Stations** - Full TuneIn integration
- 🌐 **Web Control** - Modern interface on port 6680
- 🔊 **Bluetooth Audio** - Manage speakers via web UI (port 8080)
- 🖥️ **QEMU Testing** - Test without hardware
- 🎯 **Universal** - Works on any Raspberry Pi model
- ⚡ **Fast Boot** - Ready in under 2 minutes
- 💾 **Tiny** - Only ~180MB compressed
- 🆓 **Free & Open** - MIT licensed

---

## Quick Start

### For Physical Raspberry Pi

**1. Download**

Choose the right image for your Pi model:

| Your Pi | Download |
|---------|----------|
| Pi Zero 2 W, Pi 3, Pi 4, Pi 5 | [cheeky-armv8-v1.0.0.img.xz](releases) |
| Pi 2 | [cheeky-armv7-v1.0.0.img.xz](releases) |
| Pi Zero W, Pi 1 | [cheeky-armv6-v1.0.0.img.xz](releases) |

**2. Flash**

Use [Raspberry Pi Imager](https://www.raspberrypi.com/software/) or:

```bash
xz -d cheeky-*.img.xz
sudo dd if=cheeky-*.img of=/dev/sdX bs=4M status=progress
```

**3. Boot & Access**

- Insert SD card and power on
- Wait ~2 minutes for first boot setup
- Visit **http://raspberrypi.local:6680** - Radio interface
- Visit **http://raspberrypi.local:8080** - Bluetooth manager

**4. Pair Bluetooth Speaker**

- Open http://raspberrypi.local:8080
- Click "Scan for Devices"
- Click "Pair" on your speaker
- Done! Auto-reconnects on reboot

---

### For QEMU (No Pi Needed!)

Don't have a Raspberry Pi yet? Test Cheeky in QEMU first!

**Linux/macOS:**
```bash
# Download and extract
wget https://github.com/cheeky-radio/cheeky/releases/download/v1.0.0/cheeky-qemu-linux-v1.0.0.tar.gz
tar xzf cheeky-qemu-linux-v1.0.0.tar.gz
cd linux

# Run (downloads image on first start)
./start-qemu.sh

# Access in browser
# Radio: http://localhost:6680
# Bluetooth: http://localhost:8080
# SSH: ssh -p 2222 root@localhost (password: raspberry)
```

**Windows:**
```
1. Download cheeky-qemu-windows-v1.0.0.zip
2. Extract ZIP file
3. Double-click start-qemu.bat
4. Access http://localhost:6680
```

⚠️ **Note:** Bluetooth audio won't work in QEMU (no real hardware), but you can test the web interfaces!

---

## Screenshots

### Radio Interface (Mopidy Iris)
![Radio Interface](docs/images/radio-ui.png)
*Browse and play from 100,000+ TuneIn stations*

### Bluetooth Manager
![Bluetooth Manager](docs/images/bluetooth-ui.png)
*Manage Bluetooth speakers via web - no SSH needed*

---

## Documentation

- [📘 Installation Guide](docs/INSTALLATION.md) - Detailed setup instructions
- [🖥️ QEMU Testing](docs/QEMU.md) - Test without hardware
- [🔧 Troubleshooting](docs/TROUBLESHOOTING.md) - Common issues & fixes
- [🔌 API Documentation](docs/API.md) - REST API reference
- [🎨 Customization](docs/CUSTOMIZATION.md) - Make it yours
- [🤝 Contributing](CONTRIBUTING.md) - Join the cheeky community

---

## Architecture

```
┌─────────────────────────────────────┐
│         Your Browser/Phone          │
│  ┌──────────┐      ┌─────────────┐ │
│  │ Radio UI │      │ BT Manager  │ │
│  │ :6680    │      │ :8080       │ │
│  └──────────┘      └─────────────┘ │
└─────────────────────────────────────┘
         │                  │
         ↓                  ↓
    ┌─────────┐      ┌─────────────┐
    │ Mopidy  │      │  FastAPI    │
    │ + Iris  │      │  + Uvicorn  │
    └─────────┘      └─────────────┘
         │                  │
         ↓                  ↓
    ┌─────────────────────────────────┐
    │      PulseAudio + BlueZ         │
    └─────────────────────────────────┘
         │
         ↓
    ┌─────────────────────────────────┐
    │         DietPi Linux            │
    └─────────────────────────────────┘
```

**Tech Stack:**
- **Base OS:** DietPi (optimized Debian)
- **Radio:** Mopidy + TuneIn + Iris
- **Bluetooth UI:** FastAPI + Alpine.js + Tailwind CSS
- **Audio:** PulseAudio + BlueZ
- **Build:** GitHub Actions (automated)

---

## Requirements

### For Raspberry Pi
- Any Raspberry Pi model (Zero W, Zero 2 W, 1, 2, 3, 4, 5)
- MicroSD card (8GB minimum, 16GB recommended)
- 5V power supply (appropriate for your model)
- Bluetooth speaker
- Internet connection (WiFi or Ethernet)

### For QEMU Testing
- Host machine with 4GB+ RAM
- 10GB free disk space
- QEMU installed
- Internet connection

---

## FAQ

**Q: Why is it called Cheeky?**  
A: It's British slang for "playful" or "impudent." We wanted a memorable name that signals this project doesn't take itself too seriously. Radio should be fun! Also, yes, the double meaning is intentional. We're self-aware. 🍑

**Q: Can I use this commercially?**  
A: Yes! MIT licensed. Use it however you like.

**Q: Does it work with Spotify?**  
A: Not in v1.0 (TuneIn only). Spotify integration is planned for v1.1.

**Q: Can I add my own radio stations?**  
A: Yes! See [docs/CUSTOMIZATION.md](docs/CUSTOMIZATION.md)

**Q: Does Bluetooth work in QEMU?**  
A: No, but you can test the web interfaces and see how everything works.

**Q: Why DietPi instead of Raspberry Pi OS?**  
A: DietPi is optimized for single-purpose devices. It's 60% smaller and boots faster while maintaining full compatibility.

**Q: Can I SSH into it?**  
A: Yes! `ssh root@raspberrypi.local` (default password: `raspberry` - please change it!)

**Q: Will this work on my Pi Zero W (original)?**  
A: Yes! Use the armv6 image. It'll work but be a bit slower than newer models.

---

## Troubleshooting

### Radio won't load
- Check Pi has internet connection
- Try accessing via IP address instead of hostname
- Clear browser cache

### Bluetooth speaker won't pair
- Ensure speaker is in pairing mode
- Make sure it's not connected to another device
- Try scanning again
- Check Bluetooth is enabled: `systemctl status bluetooth`

### Can't access web interface
- Confirm Pi has booted (wait 2 minutes on first boot)
- Try IP address: `http://192.168.1.X:6680`
- Check Pi is on same network as your device

More help: [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)

---

## Contributing

We love cheeky contributions! 🍑

- 🐛 [Report bugs](https://github.com/cheeky-radio/cheeky/issues)
- 💡 [Suggest features](https://github.com/cheeky-radio/cheeky/discussions)
- 📝 [Improve docs](https://github.com/cheeky-radio/cheeky/tree/main/docs)
- 💻 [Submit PRs](https://github.com/cheeky-radio/cheeky/pulls)

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## Roadmap

### v1.0 (Current) ✅
- TuneIn integration
- Bluetooth web management  
- Multi-architecture support
- QEMU testing
- Automated builds

### v1.1 (Planned)
- [ ] Spotify Connect integration
- [ ] Custom station presets
- [ ] Sleep timer
- [ ] Alarm clock
- [ ] WiFi web configuration

### v2.0 (Future)
- [ ] Multi-room audio sync
- [ ] Voice control (Alexa/Google)
- [ ] Mobile app
- [ ] Advanced audio processing

---

## Community

- 💬 [GitHub Discussions](https://github.com/cheeky-radio/cheeky/discussions) - Q&A and chat
- 🐛 [Issues](https://github.com/cheeky-radio/cheeky/issues) - Bug reports
- 📢 [Twitter](https://twitter.com/CheekyRadio) - Updates and news
- 📧 Email: hello@cheeky-radio.io

---

## Credits

Built with:
- [DietPi](https://dietpi.com/) - Lightweight OS
- [Mopidy](https://mopidy.com/) - Music server
- [Mopidy-TuneIn](https://github.com/kingosticks/mopidy-tunein) - TuneIn integration
- [Iris](https://github.com/jaedb/Iris) - Web interface
- [FastAPI](https://fastapi.tiangolo.com/) - Bluetooth manager backend
- [Tailwind CSS](https://tailwindcss.com/) - UI styling

Special thanks to the Raspberry Pi and open source communities!

---

## License

MIT License - see [LICENSE](LICENSE) for details.

```
Copyright (c) 2025 Cheeky Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```

---

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=cheeky-radio/cheeky&type=Date)](https://star-history.com/#cheeky-radio/cheeky&Date)

---

<p align="center">
  Made with 🍑 by the Cheeky community<br>
  <i>Don't take radio too seriously. Be cheeky.</i>
</p>
