import time
import asyncio
import aiohttp
import common

from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC

from ferma.helpers.metamask import MetamaskSelenium
from ferma.helpers.functions_browser import find_element_by_xpath_v2

"""
модуль, исполнитель, фермер.
"""


class FermaWorker:
    def __init__(self, server, browser, driver, tasks_for_farmer=None, robot_project_id=None, profile_id=None):
        self.server = server
        self.browser = browser
        self.driver = driver
        self.tasks_for_farmer = tasks_for_farmer
        self.robot_project_id = robot_project_id  # проект который берем в работу
        self.profile_id = profile_id  # исполнитель сам фермер.

        self.test = False
        self.test_local = False
        self.test_local_init = ""
        self.test_local_file = ""
        self.restume = False
        # можно ли выполнять код?
        # используется с выполнения кода.
        self.run_code = True

    """
    def set_local_file(self, path):
        self.test_local = True
        self.test_local_file = path
    """

    def add_test_init_param(self, key, value):
        self.test_local_init = self.test_local_init + key + "='" + value + "'" + "\n"

    def end_init_params(self):
        self.test_local_init = self.test_local_init + "#end_init" + "\n"

    def set_restume(self):
        self.restume = True
        self.run_code = False

    async def exec_scripts(self, code):

        # параметры которые необходимы при написании скрипта
        driver = self.driver

        # выполняем скрипт
        status = "SUCCESS"
        message = ""
        num_line = 1
        init_lines = True
        try:
            self.browser.log("--------")
            num_line = 1
            for line in code.split("\n"):
                if line == "#end_init":
                    num_line = 0
                    init_lines = False
                if line == "#restume" and self.restume == True:
                    self.run_code = True

                # если у нас разрешено выполнять код
                if self.run_code == True or init_lines == True:
                    self.browser.log(str(num_line) + " --> " + str(line))
                    exec(line)
                    num_line = num_line + 1

            self.browser.log("--------")
        except Exception as ex:
            status = "FAIL"
            message = str(ex)
            message = message + "\n"
            message = message + "line error: " + str(num_line)

        return status, message, num_line

    """
    с помощью этого модуля мы создаем скрипт для автоматизации.
    
    def testing(self, profile):

        start_time = datetime.now()
        driver = profile.driver
        wait = WebDriverWait(driver, 5)

        r = modules.file_local_get_contents(self.test_local_file)
        d = self.test_local_init + r

        status, message = self.exec_scripts(driver, wait, d)

        print("Результат выполнения:", status)
        print("Сообщение:", message)
        print("Выполнено за:", datetime.now() - start_time)
    """

    async def to_work_from_server(self):

        scripts_finish_status = "script_finish_success"

        for task in self.tasks_for_farmer:
            task_id = task["id"]
            robot_script_id = task["id"]
            task_name = task["name"]
            task_init = task["init"]
            task_code_url = task["code_url"]

            r = common.file_get_contents(task_code_url)
            d = task_init + r.decode()

            # выполняем скрипт
            status, message, _ = self.exec_scripts(d)

            if self.test == False:
                if status == "FAIL":
                    scripts_finish_status = "script_finish_error"
                    await self.server.script_error(self.profile_id, robot_script_id, self.robot_project_id, message)
                    time.sleep(1)
                    self.driver.quit()
                    time.sleep(2)
                    break
                else:
                    await self.server.script_success(self.profile_id, robot_script_id, self.robot_project_id)
                    time.sleep(1)

        await self.server.request_script_finish(self.profile_id, self.robot_project_id, scripts_finish_status)
        time.sleep(1)
        self.driver.quit()

    # def connected(self, profile):
    #
    #    # если мы создаем локальную задачу
    #    if self.test_local == True:
    #        self.testing(profile)
    #    else:
    #        self.run_tasks(profile)
