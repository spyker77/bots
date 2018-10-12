# In order to execute the program, you need:
# 1) download and install Python from here https://www.python.org/
# 2) download and install chromedriver from here: http://chromedriver.chromium.org/downloads
# 3) run this command via terminal: python3 get-pip.py
# 4) run this command via terminal: pip3 install selenium
# 5) run this command via terminal: python3 first_bot.py
# That's it, have fun! 🎉

import re
from time import sleep, time as currenttime
from random import randrange
from datetime import datetime, time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

# This is the rate, that you probably want to change in case to get more
# clicks (or save money, otherwise).
MAX_RATE = 1.29

# Your credentials are required in order to give access for the bot.
MY_EMAIL = "example-email@gmail.com"
MY_PASSWORD = "put-your-password-here"

# # This variant is more suitable for debugging, in order to see the real process in browser.
# driver = webdriver.Chrome()

# This variant works in a shadow without need to launch the browser.
options = webdriver.ChromeOptions()
options.add_argument("headless")
driver = webdriver.Chrome(chrome_options=options)

main_competitors = (
    "антамедиа",
    "будалекс",
    "велодом",
    "гравитех",
    "дело мастера",
    "компания вк.бел",
    "микро-климат.бел",
    "мультиком",
    "салон сантехники фонтанн",
    "торгсин",
    "удачник",
    "швейный советник",
    "швеймаг",
    "2kita.by",
    "21vek.by",
    "310.by",
    "9watt.by",
    "9999.by",
    "amd.by",
    # "bazarchik",
    "ctk.by",
    "dcd.by",
    "dom-sad.by",
    "domotehnika.by",
    "e-mag.by",
    "enter-market.by",
    "fit-sport.by",
    "galore.by",
    "hobot.by",
    "home.agroup.by",
    # "ipvan.by",
    "izliv.by",
    "kranik.by",
    "lishop.by",
    "lulu.shop.by",
    "maximal.by",
    "m-velo.by",
    "newton.by",
    "novyj.by",
    # "nvd.by",
    "pingvin.shop.by",
    "rapid.by",
    "ram.by",
    # "realshop.by",
    "sevan.by",
    "star-market.by",
    "supervelo",
    # "stuloffice.shop.by",
    "te.by",
    "tehnobum.by",
    "technostatus",
    "union.shop.by",
    "vaverki.by",
    "velogo.by",
    "yutno.by")


def log_in():
    driver.get("https://first-website.com/cabinet")
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.NAME, "email")))
    username = driver.find_element(By.NAME, "email")
    username.send_keys(MY_EMAIL)
    password = driver.find_element(By.NAME, "password")
    password.send_keys(MY_PASSWORD)
    sleep(2)
    driver.find_element(By.CSS_SELECTOR, ".popup .form-action .form-button").click()
    sleep(2)


def scrape_all_ids():
    while True:
        try:
            driver.get("https://first-website.com/catalog/rates.html")
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, "tr")))
            all_ids = tuple(re.findall(r"position(\d+)", driver.page_source))
            break
        except TimeoutException:
            print(f"Seem's like the promo was inactive at {datetime.now().time()}")
            sleep(600)
            log_in()
            continue
    return all_ids


def calculate_new_rate():
    all_ids = scrape_all_ids()
    new_rates = {}
    
    # Look for a page of the category rates.
    for single_id in all_ids:
        start_time = currenttime()
        driver.get(f"https://first-website.com/catalog/shops.html?idpat={single_id}")
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, "tr")))
        all_competitors = tuple(driver.find_elements(By.TAG_NAME, "tr")[1:])

        # Scrape rates of the category.
        child_number = 2
        competitors_rates = {}
        for competitor in all_competitors:
            seller = driver.find_element(By.CSS_SELECTOR, f"body > table > tbody > tr:nth-child({child_number}) > td:nth-child(2) > a").text
            seller_rate = driver.find_element(By.CSS_SELECTOR, f"body > table > tbody > tr:nth-child({child_number}) > td:nth-child(4)").text
            competitors_rates.update({seller.lower(): float(f"+{seller_rate}")})
            child_number += 1

        # Calculate new rate and put it into the overall dictionary.
        rates_after_cut = {key: value for key, value in competitors_rates.items() if value < MAX_RATE}
        rates_of_main_competitors = {key: value for key, value in rates_after_cut.items() if key in main_competitors}
        new_rate = round((max(rates_of_main_competitors.values(), default=0) + 0.01), 2)
        new_rates.update({f"rate{single_id}": new_rate})
        end_time = currenttime()

        # Reduce the CPU load by limiting the speed.
        time_difference = end_time - start_time
        if time_difference < 2:
            wait = 2 - time_difference
            sleep(wait)
        else:
            pass

    return new_rates


def set_new_rate():
    new_rates = calculate_new_rate()
    driver.get("https://first-website.com/catalog/rates.html")
    for key, value in new_rates.items():
        try:
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, f"{key}")))
            rate = driver.find_element(By.ID, f"{key}")
            actions = ActionChains(driver)
            actions.move_to_element(rate).double_click(rate).send_keys(f"{value}").send_keys("\ue007").perform()
        except NoSuchElementException:
            print(f"Some id wasn't found on the main page with all rates 🚨")
            continue


def check_current_page():
    try:
        driver.refresh()
        current_page = driver.find_element(By.LINK_TEXT, "Аукцион")
        if current_page:
            pass
    except NoSuchElementException:
        log_in()


log_in()
while True:
    try:
        while time(6, 0) < datetime.now().time() < time(23, 59, 59, 999999):
            print(f"The fly was started at {datetime.now().time()} 🚀")
            set_new_rate()
            print(f"All rates successfully updated at {datetime.now().time()}, so take a little break for ☕")
            sleep(randrange(180, 300, 6))
            check_current_page()
        else:
            print("We're sleeping now... 😴")
            sleep(600)
    except ConnectionRefusedError:
        print(f"We've got a ConnectionRefusedError at {datetime.now().time()}")
        sleep(60)
        continue
    except TimeoutException:
        print(f"We've got a TimeoutException at {datetime.now().time()}")
        sleep(60)
        continue
