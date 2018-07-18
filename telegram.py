import logging

import config

import urllib.request
import urllib.error
import urllib.parse
import json
import time


repeat_count = 0
prev_message = ''

def send_message(message):

    max_retry = 10
    retry = 0
    while retry < max_retry:
        try:
            _send_message(message)
            print('retry times',retry)
        except Exception as e:
            print('send_message occur exception!')
            time.sleep(20)
            retry = retry+1
            continue
        break


def _send_message(message):
    global prev_message,repeat_count
    if message == prev_message:
        repeat_count += 1
        if repeat_count >= config.telegram_rmsc:
            return
    else:
        repeat_count = 0

    url = ("https://api.telegram.org/bot%s/sendMessage?chat_id=%s&text=%s" 
            % (config.telegram_token, config.telegram_chatid, urllib.parse.quote_plus(message)))

    req = urllib.request.Request(url, None, headers={
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "*/*",
        "User-Agent": "curl/7.24.0 (x86_64-apple-darwin12.0)"})
    res = urllib.request.urlopen(req)
    #retrun_data = json.loads(res.read().decode('utf8'))

    prev_message = message

