
import requests
import schedule
import time
import datetime
import sys
import pandas as pd
import FinanceDataReader as fdr

myToken = "myToken"


def post_message(token, channel, text):
    """슬랙 메시지 전송"""
    response = requests.post("https://slack.com/api/chat.postMessage",
                             headers={"Authorization": "Bearer "+token},
                             data={"channel": channel, "text": text}
                             )

# 스케쥴 모듈이 동작시킬 함수


def test_function():
    data = fdr.DataReader(['T10Y2Y', 'T10Y3M'],
                          data_source="fred", start='2022').reset_index()
    t10y2y = data.iloc[-1]["T10Y2Y"]
    t10y3m = data.iloc[-1]["T10Y3M"]
    date = data.iloc[-1]["DATE"].strftime('%y.%m/%d')
    if (t10y2y < 0) and (t10y3m < 0):
        post_message(myToken, "#stock", "!!!!!!WARNING!!!!!!")
    else:
        pass
    # Slack에 보낼 메세지
    post_message(myToken, "#practice", "Date : " + date + "\n" +
                 " - T10Y2Y : "+str(t10y2y)+"\n"+" - T10Y3M : "+str(t10y3m))


def test_alarm():
    print("Good!")
    post_message(myToken, "#flex", "GOOD!")

