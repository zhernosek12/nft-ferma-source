import json
import urllib.request as urllib2

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC


def find_element_by_xpath_v2(driver, dom, sec=15):
    wait = WebDriverWait(driver, sec)
    return wait.until(EC.element_to_be_clickable((By.XPATH, dom)))

"""
def get_local_script(uri):
    with open(uri + "settings.json") as fp:
        return json.load(fp)
"""