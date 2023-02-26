#!/usr/bin/python
# выгрузка requirements.txt --> "pipreqs ."
# new

import os.path
import asyncio
import time
import random
import common
import json

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

        self.ferma_steps = 1000  # Количество действий, максимум 1000
        self.ferma_min_time = 20  # задержка - от 20 сек до 3 минут
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
            print(str(num + 1) + ".", name)

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

            worker = FermaWorker(self.server, browser, browser.get_driver(), tasks_for_farmer, robot_project_id,
                                 profile_id)
            await worker.to_work_from_server()

            time_sleep = random.randrange(self.ferma_min_time, self.ferma_max_time)
            time.sleep(time_sleep)

            print("ждем, сек", time_sleep)

        return True

    async def dev_download_script(self, fullpath, script_id):

        response = await self.server.download_script(script_id)
        data = (await response.json())["data"]

        if len(data) == 0:
            print("скрипт не найден!")
            return False

        if not os.path.exists(os.path.dirname(fullpath)):
            try:
                os.makedirs(os.path.dirname(fullpath))
            except OSError as exc:
                pass

        with open(fullpath, "w", encoding='utf-8') as f:
            f.write(data["source"])

        print("Исходный файл скачан и сохранен в", fullpath)
        return True

    def dev_path_script(self, script_id):
        path = os.path.dirname(os.path.realpath(__file__)) + "\scripts"
        name = script_id + ".py"
        fullpath = os.path.join(path, name)
        return fullpath

    async def dev_run_script(self, script_id):
        if script_id == "":
            print("Не удалось скачать скрипт - после «ID» пустое")
            return

        script_id = str(script_id)
        fullpath = self.dev_path_script(script_id)

        if not os.path.exists(fullpath):
            response = await self.dev_download_script(fullpath, script_id)
            if not response:
                print("ошибка при получении скрипта!")
                return

            config = common.load_config()
            config["developer_script_run"] = script_id
            common.save_config(config)

        profiles = await self.my_profiles()
        profile_id = int(input('\nНомер профиля для запуска\nВвод: ')) - 1

        response = await self.server.profileInfo(profiles[profile_id])
        profile = (await response.json())["data"]

        if len(profile) == 0:
            print("Аккаунт не найден!")
            return

        datas = json.loads(profile["datas"])
        source_code = ""

        # compile code
        for key, value in datas.items():
            source_code += f"{key}='{value}'\n"

        source_code += common.file_local_get_contents(fullpath)

        # running
        browser = self.parse_and_run_browser(profile)
        browser.connect()

        time.sleep(1)

        worker = FermaWorker(self.server, browser, browser.get_driver())
        status, message, num_line = (await worker.exec_scripts(source_code))

        browser.log()

        if status == "SUCCESS":
            browser.log(f"Скрипт отработан успешно!")
        else:
            browser.log(f"Возникла ошибка в строке: {num_line}")
            browser.log(f"{message}")

    async def dev_publish_script(self):

        config = common.load_config()
        script_id = str(config["developer_script_run"])
        fullpath = self.dev_path_script(script_id)

        source_code = common.file_local_get_contents(fullpath)
        source_code = source_code.split("\n")

        try:
            idx = source_code.index("# [end]") + 1
        except:
            idx = 0

        source_code = "\n".join(source_code[idx:])

        response = await self.server.publish_source_script(script_id, source_code)
        status = (await response.json())["status"]
        message = (await response.json())["message"]

        if status == "success":
            os.remove(fullpath)
            config["developer_script_run"] = ""
            common.save_config(config)

            print("скрипт успешно опубликован и удален:", fullpath)
        else:
            print("не удалось опубликовать", message)

    async def dev_search_error_scripts(self):

        response = await self.server.search_error_scripts()
        scripts = (await response.json())["data"]
        scripts_ids = []

        if len(scripts) == 0:
            print("Проблемных скриптов не найдено!")
            return []

        print("\nНайдено", len(scripts), "скриптов:")

        for num, script in enumerate(scripts):
            print(str(num + 1) + ".", script["name"] + " (" + str(script["cnt"]) + " ошибок)")
            scripts_ids.append(script["id"])

        return scripts_ids


def main():
    print("--------------------------------")
    print("-- ferma.zhernosek.xyz-beta03 --")
    print("--------------------------------")

    config = common.load_config()

    if "secret_key" not in config or "profiles_dir" not in config or "chrome_driver" not in config or "developer_mode" not in config:
        secret_key = input('Напиши свой API ключ, получить http://ferma.zhernosek.xyz/Profile.php\nВвод: ')
        profiles_dir = input('Путь где находятся твои профили\nВвод: ')
        chrome_driver = input('Путь к Selenium браузеру(chromedriver-windows-x64.exe)\nВвод: ')
        developer_mode = 0
        developer_script_run = ""
    else:
        secret_key = config["secret_key"]
        profiles_dir = config["profiles_dir"]
        chrome_driver = config["chrome_driver"]
        developer_mode = int(config["developer_mode"])
        developer_script_run = config["developer_script_run"]

    server = Server(secret_key)
    manager = Manager(server, profiles_dir, chrome_driver)

    assert asyncio.new_event_loop().run_until_complete(manager.check_key()) == True, \
        "Удали файл config.json и попробуй ещё раз, потому что ключ неверный"

    config["secret_key"] = secret_key
    config["profiles_dir"] = profiles_dir
    config["chrome_driver"] = chrome_driver
    config["developer_mode"] = developer_mode
    config["developer_script_run"] = developer_script_run

    common.save_config(config)

    if developer_mode == 0:
        question = int(input('1. Показать мои аккаунты\n'
                             '2. Запустить браузер\n'
                             '3. Запустить продвижение твиттера\n'
                             '4. Запустить ферму\n'
                             '5. Включить «Режим разработчика»\n'
                             '6. Выйти\n'
                             'Ввод: '))
    else:
        question = 5

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
        print("-- Режим разработчика --")

        config["developer_mode"] = 1
        common.save_config(config)

        question2 = int(input('1. Скачать и запустить выполнение скрипта\n'
                              '2. Опубликовать скрипт на ферме\n'
                              '3. Показать скрипты с ошибками\n'
                              '4. Выключить «Режим разработчика»\n'
                              'Ввод: '))

        if question2 == 1:
            question3 = input(f'ID запускаемого скрипта (#{developer_script_run})?\nВвод: ')
            if question3 == "":
                question3 = developer_script_run
            asyncio.new_event_loop().run_until_complete(manager.dev_run_script(question3))

        elif question2 == 2:
            question3 = input(f'Публикация скрипта (#{developer_script_run}) - напиши «Да» для подтверждения\nВвод: ')
            if question3.lower() == "да":
                asyncio.new_event_loop().run_until_complete(manager.dev_publish_script())

        elif question2 == 3:
            print("Поиск скриптов с ошибками...")
            scripts = asyncio.new_event_loop().run_until_complete(manager.dev_search_error_scripts())
            script_id = int(input('\nНомер скрипта для редактирования\nВвод: ')) - 1
            asyncio.new_event_loop().run_until_complete(manager.dev_run_script(scripts[script_id]))

        elif question2 == 4:
            config["developer_mode"] = 0
            common.save_config(config)
            print("Режим разработчика выключен.")

        else:
            print('Неверный ввод, попробуйте снова.')

    elif question == 6:
        raise 'Хорошо, покааа...'

    else:
        print('Неверный ввод, попробуйте снова.')

    input("\nНажмите на Enter для продолжения...")
    time.sleep(1)
    main()


if __name__ == '__main__':
    main()
