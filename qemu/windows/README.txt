CHEEKY QEMU BUNDLE FOR WINDOWS
==============================

Test Cheeky without a Raspberry Pi!

REQUIREMENTS
============
- QEMU for Windows: https://qemu.weilnetz.de/
- Disk space: 10GB free
- RAM: 4GB available
- 7-Zip: https://www.7-zip.org/ (for extracting .xz files)

SETUP
=====

1. Download QEMU for Windows from https://qemu.weilnetz.de/
2. Extract the QEMU binaries to a 'qemu' folder in this directory
3. Install 7-Zip (or use built-in Windows extraction if supported)
4. You're ready!

QUICK START
===========

1. Double-click start-qemu.bat
2. The script will:
   - Download the Pi image (~180MB) on first run
   - Extract it
   - Launch QEMU
3. Wait 30-60 seconds for first boot
4. Open in browser:
   - Radio: http://localhost:6680
   - Bluetooth Manager: http://localhost:8080
   - SSH: ssh -p 2222 root@localhost (password: raspberry)

EXITING QEMU
============
- Close the QEMU window
- Or press Ctrl+Alt+Delete to exit

TROUBLESHOOTING
===============

Q: "QEMU not found"
A: Download QEMU from https://qemu.weilnetz.de/ and extract to 'qemu' folder

Q: "Port already in use"
A: Close applications using ports 6680, 8080, or 2222

Q: "Not enough disk space"
A: Free up at least 10GB disk space

Q: Download fails
A: Check internet connection, try downloading manually:
   https://github.com/cheeky-radio/cheeky/releases

WHAT WORKS
==========
✓ Web interfaces (radio + Bluetooth manager)
✓ Radio station browsing and playback
✓ Network access
✓ SSH to the emulated Pi

WHAT DOESN'T WORK
=================
✗ Real Bluetooth audio (no hardware)
✗ GPIO access
✗ Hardware-specific features

For full Bluetooth testing, use a real Raspberry Pi!

HELP
====
For more information, see the documentation:
- Docs: https://github.com/cheeky-radio/cheeky/docs
- Issues: https://github.com/cheeky-radio/cheeky/issues

VERSION_PLACEHOLDER

🍑 Be cheeky with your testing!
