#!/bin/bash
sudo curl -s http://localhost:80 >> /keep_alive.sh
echo "Pinged localhost:80 at $(date)"
