@echo off
cd ../../
python setup.py bdist_egg --exclude-source-files
cd src/bin