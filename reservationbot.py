import time
from datetime import datetime
from reservation import ReservationEngine

date_str = "2021-2-4"
date = datetime.strptime(date_str, "%Y-%m-%d")    
email = ""
password = ""
resort = "Crystal Mountain Resort"
run_frequency_in_min = 1
log_file = "log.txt"


engine = ReservationEngine(email, password)
reserved = False
try:
    engine.login()
except:
    engine.close_driver()
    print("Invalid Login")
    exit()

while not reserved:
    engine.find_date(date, resort)
    try:
        reserved = engine.reserve()
    except:
        pass
    engine.log_results(log_file)
    engine.refresh()
    time.sleep(run_frequency_in_min * 60)

engine.close_driver()


