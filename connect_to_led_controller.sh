#!/bin/bash
hostname="led-controller"


while true; do
    ssh $hostname && break
    echo "Retrying in 5 seconds..."
    sleep 5
done