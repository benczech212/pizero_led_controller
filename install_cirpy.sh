sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip
sudo pip3 install --upgrade adafruit-blinka
python3 -m adafruit_blinka.agnostic
sudo raspi-config
# Interface Options -> Enable SPI

sudo reboot


source ~/circuitpython_env/bin/activate
pip install adafruit-circuitpython-neopixel

sudo ~/circuitpython_env/bin/python ~/dev/pizero_led_controller/rings.py
