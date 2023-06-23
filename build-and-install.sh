rm -rf ./dist
python3 setup.py bdist_wheel
scp ./dist/*.whl pi@192.168.1.118:/tmp/gshocktimeserver.zip
ssh pi@192.168.1.118 /home/pi/update.sh


