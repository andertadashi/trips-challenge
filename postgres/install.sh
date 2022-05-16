#!/bin/bash

python3 -m venv env

source env/bin/activate

which python
which pip 

pip install --upgrade pip

pip install Pyrseas pgxnclient psycopg2-binary

pgxn install pyrseas

pgxn install h3
# pgxn load h3