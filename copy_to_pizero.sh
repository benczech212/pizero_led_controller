HOSTNAME=led-controller
USERNAME=ben
FILENAME=code.py
REMOTE_PATH=/home/ben/dev/pizero_led_controller/code.py

scp $FILENAME $USERNAME@$HOSTNAME:$REMOTE_PATH
ssh $USERNAME@$HOSTNAME "sudo systemctl restart led_controller.service"