import base64
import random
import urllib
from time import sleep

from selenium.webdriver import Proxy
from selenium.webdriver.common.action_chains import ActionChains
from selenium import webdriver
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.proxy import ProxyType
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from solver import PuzleSolver
import configparser
from pyvirtualdisplay import Display

"""
external programs
sudo apt-get install python-setuptools
sudo apt-get install xvfb
sudo apt-get install xserver-xephyr
sudo easy_install PyVirtualDisplay
"""


def config_display():
    config = configparser.RawConfigParser()
    config.read('config.file')
    dsp = config.getint('display', 'visible')
    # display size has no specific significance as long as its reasonable
    # changing sizes makes the script harder to detect
    display = Display(visible=dsp, size=(random.randint(640, 1024), random.randint(640, 1024)))
    display.start()
    return display

def get_proxy():
    #proxy source: http://free-proxy.cz/es/
    config = configparser.RawConfigParser()
    config.read('config.file')
    proxies = config.get('proxy', 'proxies')
    proxy = random.choice(proxies.split(','))
    return proxy

def setup_driver():
    myProxy = get_proxy()

    proxy = Proxy({
        'proxyType': ProxyType.MANUAL,
        'httpProxy': myProxy,
        'ftpProxy': myProxy,
        'sslProxy': myProxy,
        'noProxy': ''})
    profile = webdriver.FirefoxProfile()
    options = Options()
    # options.preferences.update({"javascript.enabled": True})
    options.preferences.update({"general.useragent.override": "Mozilla/5.0 Gecko/20100101 Firefox/66"})
    options.preferences.update({"extensions.lastPlatformVersion": "66"})
    options.preferences.update({"distribution.abut": "Mozilla Firefox"})
    options.preferences.update({"intl.accept_languages": "en,en_US"})
    driver = webdriver.Firefox(firefox_profile=profile, options=options,proxy=proxy)
    return driver


def go_to_captcha(driver):
    element = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, "//*[text()='Click to verify']"))
    )
    element.click()
    action = webdriver.common.action_chains.ActionChains(driver)
    action.move_to_element_with_offset(element, 40, 40)
    action.click()
    action.perform()


def get_puzzle_images(driver):
    sleep(4)
    canvasbg = driver.find_element_by_xpath(
        '/html/body/div[6]/div[2]/div[1]/div/div[1]/div[1]/div/a/div[1]/div/canvas[1]')
    canvasfg = driver.find_element_by_xpath(
        '/html/body/div[6]/div[2]/div[1]/div/div[1]/div[1]/div/a/div[1]/div/canvas[2]')
    # get the canvas as a PNG base64 string
    canvasbg_base64 = driver.execute_script("return arguments[0].toDataURL('image/png').substring(21);", canvasbg)
    canvasfg_base64 = driver.execute_script("return arguments[0].toDataURL('image/png').substring(21);", canvasfg)
    # decode
    canvasbg_png = base64.b64decode(canvasbg_base64)
    canvasfg_png = base64.b64decode(canvasfg_base64)
    # save to a file
    with open(r"background.png", 'wb') as f:
        f.write(canvasbg_png)
    with open(r"piece.png", 'wb') as f:
        f.write(canvasfg_png)
    return 0


def drag_and_drop(driver, offst):
    sleep(2.12)
    element = driver.find_element_by_xpath('/html/body/div[6]/div[2]/div[1]/div/div[1]/div[2]/div[2]')
    action = webdriver.common.action_chains.ActionChains(driver)
    #action.click_and_hold(element).perform()
    try:
        action.drag_and_drop_by_offset(element, offst+random.randint(1,4), offst/3)\
            .click_and_hold(element)\
            .pause(1).release(element).perform()
    except:
        pass


def log_in(driver, username, password):
    try:
        sleep(2)
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "userid"))
        ).send_keys(username)
        sleep(2)
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "signin-continue-btn"))
        ).click()
        sleep(3)
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "pass"))
        ).send_keys(password)
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "sgnBt"))
        ).click()
    except:
        raise Exception("failed")


def go_to_site(driver):
    driver.get("https://signin.ebay.com/ws/eBayISAPI.dll?SignIn&ru=https%3A%2F%2Fwww.ebay.com%2F")


def crack_captcha(driver):
    get_puzzle_images(driver)
    res = PuzleSolver('piece.png', 'background.png')
    pos = res.get_position()
    drag_and_drop(driver, pos)
    net_fail(driver)


def net_fail(driver):
    # Retry
    sleep(4)
    accept_alert(driver)
    try:
        el = driver.find_element_by_xpath("//*[text()='Retry']")
    except:
        try:
            drag_and_drop(driver)
        except:
            pass
    else:

        el.click()
        sleep(3)
        crack_captcha(driver)


def where_am_i(driver):
    el = None
    try:
        el = driver.find_element_by_id('userid')
    except:
        pass
    if el:
        return 'login'
    try:
        el = driver.find_element_by_xpath("//*[text()='Click to verify']")
    except:
        pass
    if el:
        return 'captcha'
    try:
        #id = gh-ug
        el = driver.find_element_by_id('gh-ug')
    except:
        pass
    if el:
        return 'success'


def accept_alert(driver):
    try:
        WebDriverWait(driver, 1).until(EC.alert_is_present())
        sleep(1)
        Alert(driver).accept()
    except:
        pass
    else:
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "gh-ug"))
        )

def get_credentials():
    config = configparser.RawConfigParser()
    config.read('config.file')
    user = config.get('credentials', 'user')
    password = config.get('credentials','password')
    return {'user': user, 'password':password}
    
    
if __name__ == '__main__':
    cred = get_credentials()
    display = config_display()
    driver = setup_driver()
    go_to_site(driver)
    exit = False
    while not exit:
        wai = where_am_i(driver)
        if wai == 'captcha':
            go_to_captcha(driver)
            crack_captcha(driver)
            accept_alert(driver)
        elif wai == 'login':
            log_in(driver, cred['user'],cred['password'])
            accept_alert(driver)
        elif wai == 'success':
            exit = True
            print('success')
            pass
