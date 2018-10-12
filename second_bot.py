# In order to execute the program, you need:
# 1) download and install Python from here https://www.python.org/
# 2) download and install chromedriver from here: http://chromedriver.chromium.org/downloads
# 3) run this command via terminal: python3 get-pip.py
# 4) run this command via terminal: pip3 install numpy
# 5) run this command via terminal: pip3 install selenium
# 6) run this command via terminal: python3 second_bot.py
# That's it, have fun! 🎉

import re
from time import sleep
from datetime import datetime, time

import numpy as np
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException, TimeoutException, UnexpectedAlertPresentException, ElementNotVisibleException

# This is the rates, that you probably want to change in case to get more
# clicks (or save money, otherwise).
MAX_RATE_CONTEXT = 129
MAX_RATE_SHOPS = 129
MAX_RATE_GOODS = 129

# Your credentials are required in order to give access for the bot.
MY_USERNAME = "username-example"
MY_PASSWORD = "put-your-password-here"

# # This variant is more suitable for debugging, in order to see the real process in browser.
# driver = webdriver.Chrome()

# This variant works in a shadow without need to launch the browser.
options = webdriver.ChromeOptions()
options.add_argument("headless")
driver = webdriver.Chrome(chrome_options=options)

main_competitors = (
    "микро-климат.бел",
    "1st-mebel.by",
    "9watt.by",
    "21vek.by",
    "24-market.by",
    "7745.by",
    "amd.by",
    "agrox.by",
    "asteroid.by",
    "delomastera.by",
    "domix.by",
    "domotehnika.by",
    "e-mag.by",
    "e-not.by",
    "e-l.shop.by",
    "home.agroup.by",
    "izliv.by",
    "kit.by",
    "lda-tehno.by",
    "lishop.by",
    "malutka.by",
    "maximal.by",
    "mirbt.by",
    "multicom.by",
    "pingvin.shop.by",
    "rubl.by",
    "sevan.by",
    "sheah.shop.by",
    "socket.by",
    "sportsity.by",
    "sportman.by",
    "sport-center.by",
    # "star-market.by",
    "stuloffice.shop.by",
    "sundays.by",
    "texpom.by",
    "ttn.by",
    "union.shop.by",
    "utr.by",
    "vdv.by",
    "vipbaby.by",
    "www.hobot.by",
    "ydachnik.by")


def log_in():
    driver.get("https://second-website.com/office/index.php?r=login")
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.NAME, "login")))
    username = driver.find_element(By.NAME, "login")
    username.send_keys(MY_USERNAME)
    password = driver.find_element(By.NAME, "passwd")
    password.send_keys(MY_PASSWORD)
    sleep(2)
    driver.find_element(By.CSS_SELECTOR,"table.input_table .input_btn, table.input_table .input_btn:hover").click()
    sleep(2)


def check_active_promo():
    while True:
        try:
            driver.get("https://second-website.com/office/index.php?menu_item_id=tariff_plan")
            WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "frmDPBlock4_block")))
            current_balance = driver.find_element(By.CLASS_NAME, "denied")
            if current_balance:
                print(f"The promo was inactive at {datetime.now().time()}")
                sleep(600)
        except TimeoutException:
            log_in()
            continue
        except NoSuchElementException:
            break


def update_rate_for_context():
    while True:
        try:
            num_of_attempts_if_timeout = 1
            driver.get("https://second-website.com/office/index.php?menu_item_id=advance_find")
            WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#cuselFrame-max_weight")))
            try:

                # Scrape rates.
                pairs = tuple(re.findall(r"(\d+) - (\w+.\w+.\w+.?\w+)", driver.page_source))
                competitors_rates = ({value: int(key)} for key, value in pairs)

                # Calculate new rate.
                lower_than_max_rate = ({key: value} for pair in competitors_rates for key, value in pair.items() if value <= MAX_RATE_CONTEXT)
                rates_of_main_competitors = ({key: value} for pair in lower_than_max_rate for key, value in pair.items() if key in main_competitors)
                new_rate = max((value for pair in rates_of_main_competitors for key, value in pair.items()), default=0) + 1

                # Set new rate.
                driver.find_element(By.ID, "cuselFrame-max_weight").click()
                possible_options = tuple(int(option.text) for option in tuple(driver.find_elements(By.CLASS_NAME, "cuselItem")[1:MAX_RATE_CONTEXT]))
                # Here numpy is used in order to find closest value among available.
                array = np.asarray(possible_options)
                index = np.argmin(abs(array - new_rate))
                driver.find_element(By.CSS_SELECTOR, f"#cusel-scroll-max_weight > span:nth-child({possible_options[index] + 1})").click()
                WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#frmCampaign > div.module-box-main > div > div.saveContent > button.btn.btn-success")))
                driver.find_element(By.CSS_SELECTOR, "#frmCampaign > div.module-box-main > div > div.saveContent > button.btn.btn-success").click()
                sleep(2)
                break

            except ValueError:
                print("ValueError occurred in context 🚨")
                continue
            except StaleElementReferenceException:
                print("StaleElementReferenceException occurred in context 🚨")
                continue
            except NoSuchElementException:
                print("NoSuchElementException occurred in context 🚨")
                continue
            except TimeoutException:
                print("TimeoutException occurred in context 🚨")
                if num_of_attempts_if_timeout <= 10:
                    num_of_attempts_if_timeout += 1
                    continue
                else:
                    break

        except UnexpectedAlertPresentException:
            print("UnexpectedAlertPresentException occurred in context 🚨")
            alert = driver.switch_to.alert
            alert.accept()
            continue


def update_rate_for_shops():
    while True:
        try:
            driver.get("https://second-website.com/office/index.php?menu_item_id=advance_shop")
            sleep(2)

            # Scrape rates.
            num_of_attempts_if_timeout = 1
            # This action hides contact panel in order to prevent misclick.
            driver.execute_script("""
                var element = document.querySelector(".contacts");
                if (element)
                    element.parentNode.removeChild(element);
                """)
            # WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, "WeightsBlock")))
            WebDriverWait(driver, 30).until(EC.visibility_of_all_elements_located((By.CLASS_NAME, "WeightsBlock")))
            categories = len(tuple(driver.find_elements(By.CLASS_NAME, "WeightsBlock"))) + 1
            for category in range(1, categories):
                try:
                    WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,f"#index > table > tbody > tr:nth-child({category}) > td:nth-child(11) > span > div:nth-child(3) > div.WeightsBlock > i")))
                    driver.find_element(By.CSS_SELECTOR, f"#index > table > tbody > tr:nth-child({category}) > td:nth-child(11) > span > div:nth-child(3) > div.WeightsBlock > i").click()
                    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#gradient > div.tooltipster-base.tooltipster-default.tooltipster-fade.tooltipster-fade-show")))
                    sleep(1)
                    pairs = tuple(re.findall(r"(\d+) - (\w+.\w+.\w+.?\w+)", driver.page_source))
                    competitors_rates = ({value: int(key)} for key, value in pairs)

                    # Calculate new rate.
                    lower_than_max_rate = ({key: value} for pair in competitors_rates for key, value in pair.items() if value <= MAX_RATE_SHOPS)
                    rates_of_main_competitors = ({key: value} for pair in lower_than_max_rate for key, value in pair.items() if key != "kingmarket.by")
                    all_values = tuple(value for pair in rates_of_main_competitors for key, value in pair.items())
                    # If there are not enough competitors, then use rates value = 0 by default.
                    try:
                        ultimate_position = all_values[0]
                        try:
                            penultimate_position = all_values[1]
                        except IndexError:
                            penultimate_position = 0
                            pass
                    except IndexError:
                        ultimate_position = 0
                        penultimate_position = 0
                        pass

                    # Set new rate.
                    select = Select(driver.find_element(By.CSS_SELECTOR, f"#index > table > tbody > tr:nth-child({category}) > td:nth-child(11) > span > div.WeightInfoBlock.CurrentWeightBlock > select"))
                    possible_options = tuple(int(option.text) for option in tuple(select.options[1:MAX_RATE_SHOPS]))
                    array = np.asarray(possible_options)
                    rates_difference = ultimate_position - penultimate_position
                    if rates_difference >= 50:
                        index = np.argmin(abs(array - (penultimate_position + 1)))
                        select.select_by_visible_text(str(possible_options[index]))
                    else:
                        index = np.argmin(abs(array - (ultimate_position + 1)))
                        select.select_by_visible_text(str(possible_options[index]))

                except ValueError:
                    print(f"ValueError occurred in shops with position: {category} 🚨")
                    continue
                except StaleElementReferenceException:
                    print(f"StaleElementReferenceException occurred in shops with position: {category} 🚨")
                    continue
                except NoSuchElementException:
                    print(f"NoSuchElementException occurred in shops with position: {category} 🚨")
                    continue
                except ElementNotVisibleException:
                    print(f"ElementNotVisibleException occurred in shops with position: {category} 🚨")
                    sleep(5)
                    continue
                except TimeoutException:
                    print(f"TimeoutException occurred in shops with position: {category} 🚨")
                    if num_of_attempts_if_timeout <= 10:
                        num_of_attempts_if_timeout += 1
                        continue
                    else:
                        break

            # Finish update shop's rates.
            sleep(2)
            break

        except UnexpectedAlertPresentException:
            print(f"UnexpectedAlertPresentException occurred in main shops 🚨")
            alert = driver.switch_to.alert
            alert.accept()
            continue


def update_rate_for_goods():
    while True:
        try:
            driver.get("https://second-website.com/office/index.php?menu_item_id=advance_goods")
            sleep(2)
            while True:

                # Scrape rates.
                num_of_attempts_if_timeout = 1
                # This action hides contact panel in order to prevent misclick.
                driver.execute_script("""
                    var element = document.querySelector(".contacts");
                    if (element)
                        element.parentNode.removeChild(element);
                    """)
                # WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, "WeightsBlock")))
                WebDriverWait(driver, 30).until(EC.visibility_of_all_elements_located((By.CLASS_NAME, "WeightsBlock")))
                categories = len(tuple(driver.find_elements(By.CLASS_NAME, "WeightsBlock"))) + 1
                for category in range(1, categories):
                    try:
                        WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.CSS_SELECTOR, f"#index > table > tbody > tr:nth-child({category}) > td:nth-child(9) > span > div:nth-child(3) > div.WeightsBlock > i")))
                        driver.find_element(By.CSS_SELECTOR, f"#index > table > tbody > tr:nth-child({category}) > td:nth-child(9) > span > div:nth-child(3) > div.WeightsBlock > i").click()
                        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#gradient > div.tooltipster-base.tooltipster-default.tooltipster-fade.tooltipster-fade-show")))
                        sleep(1)
                        pairs = tuple(re.findall(r"(\d+) - (\w+.\w+.\w+.?\w+)", driver.page_source))
                        competitors_rates = ({value: int(key)} for key, value in pairs)

                        # Calculate new rate.
                        lower_than_max_rate = ({key: value} for pair in competitors_rates for key, value in pair.items() if value <= MAX_RATE_GOODS)
                        rates_of_main_competitors = ({key: value} for pair in lower_than_max_rate for key, value in pair.items() if key in main_competitors)
                        all_values = tuple(value for pair in rates_of_main_competitors for key, value in pair.items())
                        # If there are not enough competitors, then use rates value = 0 by default.
                        try:
                            ultimate_position = all_values[0]
                            try:
                                penultimate_position = all_values[1]
                                try:
                                    next_to_penultimate_position = all_values[2]
                                except IndexError:
                                    next_to_penultimate_position = 0
                                    pass
                            except IndexError:
                                penultimate_position = 0
                                pass
                        except IndexError:
                            ultimate_position = 0
                            penultimate_position = 0
                            next_to_penultimate_position = 0
                            pass
                        first_second_difference = ultimate_position - penultimate_position
                        second_third_difference = penultimate_position - next_to_penultimate_position
                        
                        # Set new rate.
                        select = Select(driver.find_element(By.CSS_SELECTOR, f"#index > table > tbody > tr:nth-child({category}) > td:nth-child(9) > span > div.WeightInfoBlock.CurrentWeightBlock > select"))
                        possible_options = tuple(int(option.text) for option in tuple(select.options[1:MAX_RATE_GOODS]))
                        array = np.asarray(possible_options)
                        # A money saving strategy, if possible within a certain range.
                        if second_third_difference >= 30:
                            index = np.argmin(abs(array - (next_to_penultimate_position + 1)))
                            select.select_by_visible_text(str(possible_options[index]))
                        elif first_second_difference >= 20:
                            index = np.argmin(abs(array - (penultimate_position + 1)))
                            select.select_by_visible_text(str(possible_options[index]))
                        else:
                            index = np.argmin(abs(array - (ultimate_position + 1)))
                            select.select_by_visible_text(str(possible_options[index]))

                    except ValueError:
                        print(f"ValueError occurred in goods with position: {category} 🚨")
                        continue
                    except StaleElementReferenceException:
                        print(f"StaleElementReferenceException occurred in goods with position: {category} 🚨")
                        continue
                    except NoSuchElementException:
                        print(f"NoSuchElementException occurred in goods with position: {category} 🚨")
                        continue
                    except ElementNotVisibleException:
                        print(f"ElementNotVisibleException occurred in goods with position: {category} 🚨")
                        sleep(2)
                        continue
                    except TimeoutException:
                        print(f"TimeoutException occurred in goods with position: {category} 🚨")
                        if num_of_attempts_if_timeout <= 10:
                            num_of_attempts_if_timeout += 1
                            continue
                        else:
                            break

                # Move to the next page and repeat rates update.
                next_page = driver.find_element(By.CLASS_NAME, "next")
                if next_page:
                    try:
                        next_page.click()
                        sleep(2)
                    except ElementNotVisibleException:
                        break
                else:
                    break

            # Return to the first page of rates for goods.
            driver.find_element(By.CLASS_NAME, "first").click()
            sleep(2)
            break

        except UnexpectedAlertPresentException:
            print(f"UnexpectedAlertPresentException occurred in main goods 🚨")
            alert = driver.switch_to.alert
            alert.accept()
            continue


def check_current_page():
    try:
        driver.refresh()
        sleep(2)
        current_page = driver.find_element(By.ID, "summa")
        if current_page:
            pass
    except NoSuchElementException:
        log_in()


log_in()
while True:
    try:
        while time(6, 0) < datetime.now().time() < time(23, 59, 59, 9):
            print(f"The fly was started at {datetime.now().time()} 🚀")
            check_active_promo()
            update_rate_for_context()
            update_rate_for_shops()
            update_rate_for_goods()
            print(f"All rates successfully updated at {datetime.now().time()} 👏")
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
