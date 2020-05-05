#!/bin/sh
ln -s ../info .
ln -s ../graph .
ln -s ../chart .
python -m http.server 8000
#google-chrome http://localhost:8000/
