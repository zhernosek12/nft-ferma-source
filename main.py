#!/usr/bin/python
# выгрузка requirements.txt --> "pipreqs ."

import asyncio
import time
import random
import common

from ferma.helpers.custom_browser import CustomBrowser
from ferma.ferma_worker import FermaWorker
from server import Server

from ferma.modules.twitter_promontion import TwitterPromontion

class Manager:
    def __init__(self, server, profiles_dir, chrome_driver):
        self.server = server
        self.profiles_dir = profiles_dir
        self.chrome_driver = chrome_driver

        self.extensions = []

        self.ferma_steps = 1000             # Количество действий, максимум 1000
        self.ferma_min_time = 20            # задержка - от 20 сек до 3 минут
        self.ferma_max_time = 3 * 60

    def parse_and_run_browser(self, data):
        _chrome_driver = self.chrome_driver
        _proxy = data["proxy"]
        _user_agent = data["user_agent"]
        _user_data_dir = self.profiles_dir
        _user_profile_id = "user" + data["id"]
        _extensions = self.extensions

        return CustomBrowser(_chrome_driver, _proxy, _user_agent,
                             _user_data_dir, _user_profile_id, _extensions)

    async def check_key(self):
        try:
            await (await self.server.checkKey()).json()
            return True
        except:
            return False

    async def my_profiles(self):
        response = await self.server.myProfiles()
        profiles = (await response.json())["data"]

        assert len(profiles) != 0, "Профилей не найдено на ферме!"

        print("\nПрофили:")

        for num, name in enumerate(profiles):
            print(str(num+1) + ".", name)

        return profiles

    async def browser_run(self, username):
        response = await self.server.profileInfo(username)
        profile = (await response.json())["data"]

        browser = self.parse_and_run_browser(profile)
        browser.connect()
        browser.start()

        return True

    async def twitter_promotion(self):
        await (TwitterPromontion(self)).start()
        return True

    async def ferma_run(self):
        for _ in range(self.ferma_steps):
            response = await self.server.robotProject()
            data = (await response.json())["data"]

            assert (data) != 0, "Задач пока нет :) запусти алгоритм позже"

            profile = data["profile"]
            tasks_for_farmer = data["tasks_for_farmer"]
            robot_project_id = data["robot_project_id"]
            profile_id = profile["id"]

            browser = self.parse_and_run_browser(profile)
            browser.connect()

            time.sleep(1)

            worker = FermaWorker(self.server, browser.get_driver(), tasks_for_farmer, robot_project_id, profile_id)
            await worker.to_work()

            time_sleep = random.randrange(self.ferma_min_time, self.ferma_max_time)
            time.sleep(time_sleep)

            print("ждем, сек", time_sleep)

        return True

def main():

    print("--------------------------------")
    print("-- ferma.zhernosek.xyz-beta03 --")
    print("--------------------------------")

    config = common.load_config()

    if "secret_key" not in config or "profiles_dir" not in config or "chrome_driver" not in config:
        secret_key = input('Напиши свой API ключ, получить http://ferma.zhernosek.xyz/Profile.php\nВвод: ')
        profiles_dir = input('Путь где находятся твои профили\nВвод: ')
        chrome_driver = input('Путь к Selenium браузеру(chromedriver-windows-x64.exe)\nВвод: ')
    else:
        secret_key = config["secret_key"]
        profiles_dir = config["profiles_dir"]
        chrome_driver = config["chrome_driver"]

    server = Server(secret_key)
    manager = Manager(server, profiles_dir, chrome_driver)

    assert asyncio.new_event_loop().run_until_complete(manager.check_key()) == True, \
        "Удали файл config.json и попробуй ещё раз, потому что ключ неверный"

    config["secret_key"] = secret_key
    config["profiles_dir"] = profiles_dir
    config["chrome_driver"] = chrome_driver

    common.save_config(config)

    question = int(input('1. Показать мои аккаунты\n'
                         '2. Запустить браузер\n'
                         '3. Запустить продвижение твиттера\n'
                         '4. Запустить ферму\n'
                         '5. Выйти\n'
                         'Ввод: '))

    if question == 1:
        asyncio.new_event_loop().run_until_complete(manager.my_profiles())

    elif question == 2:
        profiles = asyncio.new_event_loop().run_until_complete(manager.my_profiles())
        profile_id = int(input('\nНомер профиля для запуска\nВвод: ')) - 1
        asyncio.new_event_loop().run_until_complete(manager.browser_run(profiles[profile_id]))

    elif question == 3:
        print("Запуск продвижения твиттера...")
        asyncio.new_event_loop().run_until_complete(manager.twitter_promotion())

    elif question == 4:
        print("Запуск фермы...")
        asyncio.new_event_loop().run_until_complete(manager.ferma_run())

    elif question == 5:
        raise 'Хорошо, покааа...'

    else:
        print('Неверный ввод. Попробуйте снова.')

    input("\nНажмите на Enter для продолжения...")
    time.sleep(1)
    main()

if __name__ == '__main__':
    main()