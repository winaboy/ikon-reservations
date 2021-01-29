from msedge.selenium_tools import Edge, EdgeOptions
from datetime import datetime
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import calendar

class ReservationEngine:
    def __init__ (self, email, password, headless=True):
        self.email = email
        self.password = password
        self.available = False
        self.booked = False
        self.reservations_left = False
        options = EdgeOptions()
        options.add_argument("--log-level=3")
        options.use_chromium = True
        if headless:
            options.add_argument("headless")
        self.driver = Edge(options=options)
        print("Starting web driver...")
    
    def remove_overlay(self):
        #get rid of cc overlay
        buttons = self.driver.find_elements_by_css_selector("a.cc-btn")
        while any(map(lambda x: x.size["height"] != 0, buttons)):
            for button in buttons:
                try:
                    button.click()
                except:
                    pass
            buttons = self.driver.find_elements_by_css_selector("a.cc-btn")

    def login(self):
        #login
        self.driver.get("https://account.ikonpass.com/en/login?redirect_uri=/en/myaccount/add-reservations/")
        self.remove_overlay()
        email_box = self.driver.find_element_by_css_selector("input#email")
        email_box.send_keys(self.email)
        password_box = self.driver.find_element_by_css_selector("input#sign-in-password")
        password_box.send_keys(self.password)
        submit = self.driver.find_element_by_css_selector("button.submit")
        submit.click()
        print("Logged in")

    def refresh(self):
        self.driver.refresh()
        
    def find_date(self, date, resort):
        WebDriverWait(self.driver,10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input.react-autosuggest__input')))   
        self.remove_overlay()
        #select resort
        search = self.driver.find_element_by_css_selector("input.react-autosuggest__input")
        search.send_keys(resort)
        button = self.driver.find_element_by_css_selector("li#react-autowhatever-resort-picker-section-1-item-0")     
        button.click()            
        button = self.driver.find_element_by_xpath("//span[contains(text(), 'Continue')]")
        button.click()

        WebDriverWait(self.driver,10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.DayPicker-wrapper')))
        self.remove_overlay()

        #select date
        datepicker = self.driver.find_element_by_css_selector("div.DayPicker-wrapper") 
        month_selected = False
        while not month_selected:
            month_text = calendar.month_name[date.month]
            month = datepicker.find_elements_by_xpath("//span[contains(text(), " + "'" + month_text + "')]")
            if len(month) > 0:
                month_selected = True
            else:
                button = datepicker.find_element_by_class_name("icon-chevron-right")
                button.click()

        day = datepicker.find_element_by_xpath("//div[@aria-label='" + date.strftime("%a %b %d %Y") + "']")
        day.click()
        day_classes = day.get_attribute(name="class")

        self.available = "past" not in day_classes and "unavailable" not in day_classes
        self.booked = "confirmed" in day_classes
        div = self.driver.find_elements_by_xpath("//div[contains(text(), 'Reservation Limit Reached')]")
        self.reservations_left = len(div) == 0
        print("Date Selected: "+ date.strftime("%m/%d/%Y"))

    def reserve(self):
        #confirm reservation if available
        if self.available and not self.booked and self.reservations_left:
            self.remove_overlay()
            button = self.driver.find_element_by_xpath("//span[contains(text(), 'Save')]")
            button.click()
            button = self.driver.find_element_by_xpath("//span[contains(text(), 'Continue to Confirm')]")
            button.click()

            WebDriverWait(self.driver,10).until(EC.presence_of_element_located((By.XPATH, "//input[@type='checkbox']")))   
            button = self.driver.find_element_by_xpath("//input[@type='checkbox']")
            button.click()
            WebDriverWait(self.driver,10).until(EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'Confirm Reservations')]")))   
            button = self.driver.find_element_by_xpath("//span[contains(text(), 'Confirm Reservations')]")
            button.click()
            self.booked = True
            print("Booked")
        return self.booked

    def log_results(self, log_file_name):
        #log
        with open(log_file_name, "a") as f:
            f.write(datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))
            f.write(": Available - %r, Booked - %r, Reservations Left- %r" % (self.available, self.booked, self.reservations_left))
            f.write("\n")    
    
    def close_driver(self):
        self.driver.close()