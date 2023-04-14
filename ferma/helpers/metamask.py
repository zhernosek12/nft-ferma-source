import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

# исходный код, где можно брать за основу
#
# https://github.com/javerianadeem/selenium_metamask_automation/blob/master/selenium_metamask_automation/__init__.py

class MetamaskSelenium:
    def __init__(self, driver, password):
        self.driver = driver
        self.password = password
        self.page = "_"
        self.error = ""

    def set_active_window(self):
        for handle in self.driver.window_handles:
            self.driver.switch_to_window(handle)
            if self.driver.title == "MetaMask Notification":
                break

    def reset_active_window(self):
        for handle in self.driver.window_handles:
            self.driver.switch_to_window(handle)
            break

    def get_type_page(self):
        self.set_active_window()
        try:
            page = self.driver.find_element_by_xpath('//*[@id="app-content"]/div/div[2]/div/div')
            attr = page.get_attribute("class")

            if attr == "unlock-page":
                self.page = "UNLOCK"
            elif attr == "permissions-connect__top-bar":
                self.page = "PREMISSIONS_CONNECT"
            elif attr == "request-signature__header":
                self.page = "REQUEST_SIGNATURE"
            else:
                print("page", attr, "not found!!!")

        except Exception as ex:
            raise RuntimeError("Error get page!")
            pass

    def get_page(self):
        return self.page

    def unlock(self):
        self.set_active_window()

        inputs = self.driver.find_elements_by_xpath('//*[@id="password"]')
        inputs[0].clear()
        inputs[0].send_keys(self.password)

        self.driver.find_element_by_xpath("//button[contains(@class,'button')]").click()

        time.sleep(2)

        try:
            self.error = self.driver.find_element_by_css_selector("p.MuiFormHelperText-root.Mui-error.MuiFormHelperText-filled").text
        except Exception as ex:
            pass

        time.sleep(2)

        self.reset_active_window()

        if self.error != "":
            raise RuntimeError(self.error)

        print('Site metamask unlock.')
        time.sleep(1)

    """
    когда нажали подключить кошелек
    и у нас всплывающее окошко, где нам нужно дать доступ 
    к нашему кошельку!
    """
    def connect_to_website(self):
        try:
            self.get_type_page()
            time.sleep(1)
            current_page = self.get_page()

            if current_page == "UNLOCK":
                self.unlock()

            if current_page == "PREMISSIONS_CONNECT":
                self.driver.execute_script("window.scrollBy(0, document.body.scrollHeight)")
                time.sleep(3)
                self.driver.find_element_by_xpath('//*[@id="app-content"]/div/div[2]/div/div[3]/div[2]/button[2]').click()
                time.sleep(1)
                self.driver.find_element_by_xpath('//*[@id="app-content"]/div/div[2]/div/div[2]/div[2]/div[2]/footer/button[2]').click()
                time.sleep(3)
                print('Site connected to metamask')
                self.driver.switch_to.window(self.driver.window_handles[0])
                time.sleep(3)
        except Exception as ex:
            print(ex)

    def sign_confirm(self):
        try:
            self.get_type_page()
            time.sleep(1)
            current_page = self.get_page()

            if current_page == "UNLOCK":
                self.unlock()

            if current_page == "REQUEST_SIGNATURE":
                self.driver.execute_script("window.scrollBy(0, document.body.scrollHeight)")
                time.sleep(3)
                self.driver.find_element_by_xpath('//*[@id="app-content"]/div/div[2]/div/div[3]/button[2]').click()
                time.sleep(1)
                print('Sign confirmed')
                self.reset_active_window()
                time.sleep(3)
        except Exception as ex:
            print(ex)

    def accept_switch_network(self):
        self.set_active_window()
        time.sleep(0.5)
        self.driver.find_element_by_xpath('//*[@id="app-content"]/div/div[2]/div/div[2]/div/button[2]').click()
        time.sleep(1)
        self.reset_active_window()

    def confirm_txs(self):
        self.set_active_window()
        time.sleep(0.5)
        self.driver.find_element_by_xpath('//*[@id="app-content"]/div/div[2]/div/div[2]/div/button[2]').click()
        time.sleep(1)
        self.reset_active_window()

#metamaskSelenium = MetamaskSelenium(driver, "CookFabulous5824")

# 1 этап это этап авторизации.
#metamaskSelenium.connect_to_website()
#metamaskSelenium.get_type_page()
#print(metamaskSelenium.get_page())

# подождем на всякий
#time.sleep(3)

#metamaskSelenium.sign_confirm()

# Авторизовались, теперь подключимся
#metamaskSelenium.connect_to_website()
