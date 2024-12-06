#!/bin/bash

while true; do
    ssh led-controller && break
    echo "Retrying in 5 seconds..."
    sleep 5
done