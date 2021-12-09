#!/bin/sh

source backend-venv/bin/activate

# If we're testing only the modeling
#python data_processor.py dados.json

python server.py
