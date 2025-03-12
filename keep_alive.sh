#!/bin/bash
curl -s http://localhost:80 > /dev/null
echo "Pinged localhost:80 at $(date)"
