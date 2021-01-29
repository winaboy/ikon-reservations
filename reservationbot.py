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
    try:
        engine.find_date(date, resort)
    except:
        print("Unable to select date:" + date_str)

    try:
        reserved = engine.reserve()
        if reserved:
            print("Reservation Successful")
        else:
            print("No available reservations")
    except:
        print("Error making reservation - retrying")
        pass
    engine.log_results(log_file)
    print("Refreshing")
    engine.refresh()
    print("Waiting for %i minutes" % run_frequency_in_min)
    time.sleep(run_frequency_in_min * 60)

engine.close_driver()


