#!/data/data/com.termux/files/usr/bin/sh
USB_DEVICE="/dev/bus/usb/001/003"

termux-usb -r -e python app.py $USB_DEVICE
