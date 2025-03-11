#! /usr/bin/bash
celery -A myproject worker -l info
celery -A myproject beat -l info
