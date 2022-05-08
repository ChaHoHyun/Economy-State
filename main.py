# import requests
import schedule
import time
import datetime
import sys
# import pandas as pd
from alarm import test_alarm

test_alarm()

# 매초마다 test_alarm 실행
schedule.every(1).seconds.do(test_alarm)

# 무한 루프를 돌면서 스케쥴을 유지한다.
while True:
    try:
        schedule.run_pending()
        time.sleep(1)
    except Exception as e:
        print(e)
        # post_message(myToken, "#stock", e)
        time.sleep(1)