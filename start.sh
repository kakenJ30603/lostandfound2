#!/bin/bash

cd /home/system/lostandfound2

# Flask起動
python3 app.py > flask.log 2>&1 &

# Flaskが起動するまで待つ
for i in {1..30}
do
    if /usr/bin/curl -s http://127.0.0.1:5000 > /dev/null
    then
        break
    fi
    sleep 1
done

# ngrok起動
/snap/bin/ngrok http 5000 > ngrok.log 2>&1 &

# ngrokが起動するまで待つ
sleep 5

# Chromeを開く
google-chrome "https://confusing-veneering-radish.ngrok-free.dev"