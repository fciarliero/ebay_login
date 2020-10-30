import base64
import json
import random
from time import sleep

import requests

from selenium.webdriver.common.action_chains import ActionChains
from selenium import webdriver
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.proxy import ProxyType, Proxy
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import geckodriver_autoinstaller
import configparser
from solver2cap import TwoCaptcha

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
    options.preferences.update({"javascript.enabled": True})
    options.preferences.update({"general.useragent.override": "Mozilla/5.0 Gecko/20100101 Firefox/66"})
    options.preferences.update({"extensions.lastPlatformVersion": "66"})
    options.preferences.update({"distribution.abut": "Mozilla Firefox"})
    options.preferences.update({'intl.accept_languages': 'en,en_US'})
    driver = webdriver.Firefox(firefox_profile=profile, options=options, proxy=proxy)
    return driver


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
    #driver.get("https://signin.ebay.com/distil_identify_cookie.html?httpReferrer=%2Fws%2FeBayISAPI.dll%3FSignIn%26ru%3Dhttps%253A%252F%252Fwww.ebay.com%252F&uid=4DBF6146-EBA4-3C4B-AB39-E0A8BABEEB95&distil_rA=2")
    #sleep(4)
    driver.get("https://signin.ebay.com/")

def api_key():
    config = configparser.RawConfigParser()
    config.read('config.file')
    apiKey = config.get('api', 'key')
    return apiKey


def get_params():
    gt = 'f2ae6cadcf7886856696502e1d55e00c'
    url = 'https://www.ebay.com/distil_r_captcha_challenge'
    api_server = 'api-na.geetest.com'
    resp = requests.get(url)
    challenge = resp.content.decode('utf-8').split(';')[0]
    return {'gt': gt, 'challenge': challenge, 'url': url, 'api_server': api_server}


def crack_captcha(params, solver):
    try:
        result = solver.geetest(gt=params['gt'],
                                challenge=params['challenge'],
                                url=params['url'],
                                api_server=params['api_server'])
    except Exception as e:
        sleep(5)
        print('couldnt solve captcha. '+str(e))
        if str(e) in ['ERROR_CAPTCHA_UNSOLVABLE','CAPCHA_NOT_READY']:
            return (crack_captcha(get_params,solver))
        else:
            return(crack_captcha(get_params(),solver))
    else:
        return result

def input_captcha_solution(result):
    dic = json.loads(result['code'])
    #inserting seccode
    driver.execute_script(
        "document.getElementsByName('geetest_seccode')[0].type = 'text'")
    driver.execute_script(
        "document.getElementsByName('geetest_seccode')[0].value='{}'".format(dic['geetest_seccode']))
    driver.execute_script(
        "document.getElementsByName('geetest_seccode')[0].type = 'hidden'")
    #inserting challenge
    driver.execute_script(
        "document.getElementsByName('geetest_challenge')[0].type = 'text'")
    driver.execute_script(
        "document.getElementsByName('geetest_seccode')[0].value='{}'".format(dic['geetest_challenge']))
    driver.execute_script(
        "document.getElementsByName('geetest_challenge')[0].type = 'hidden'")
    #inserting validate
    driver.execute_script(
        "document.getElementsByName('geetest_validate')[0].type = 'text'")
    driver.execute_script(
        "document.getElementsByName('geetest_validate')[0].value='{}'".format(dic['geetest_challenge']))
    driver.execute_script(
        "document.getElementsByName('geetest_validate')[0].type = 'hidden'")
    driver.find_element_by_id('distilCaptchaForm').submit()
    return 0

def solve_captcha():
    params = get_params()
    solver = TwoCaptcha(api_key())
    result = crack_captcha(params,solver)
    input_captcha_solution(result)

def go_to_captcha(driver):
    element = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, "//*[text()='Click to verify']"))
    )
    element.click()
    action = webdriver.common.action_chains.ActionChains(driver)
    action.move_to_element_with_offset(element, 40, 40)
    action.click()
    action.perform()


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
        # id = gh-ug
        el = driver.find_element_by_id('gh-ug')
    except:
        pass
    if el:
        return 'success'


def accept_alert(driver):
    try:
        WebDriverWait(driver, 5).until(EC.alert_is_present())
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
    password = config.get('credentials', 'password')
    return {'user': user, 'password': password}


if __name__ == '__main__':
    cred = get_credentials()
    driver = setup_driver()
    go_to_site(driver)
    exit = False
    while not exit:
        wai = where_am_i(driver)
        if wai == 'captcha':
            solve_captcha()
            accept_alert(driver)
        elif wai == 'login':
            log_in(driver, cred['user'], cred['password'])
            accept_alert(driver)
        elif wai == 'success':
            exit = True
            #uncomment to quit at the end
            #driver.close()
            print('success')
            pass
