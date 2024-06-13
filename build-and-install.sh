rm -rf ./dist
python3 setup.py bdist_wheel
scp ./dist/*.whl pi@pizero:/tmp/gshocktimeserver.zip
ssh pi@pizero /home/pi/update.sh


