import os
import json
import urllib.request as urllib2

from models.database import get_robot_project_error
from models.profile import Profile
from models.helpers import get_local_script

from ferma_worker import CallbackFerma


def push_script(name):
    print("push script.", name)

def download_task_error(directory_save_scripts):

    response = get_robot_project_error()

    for task in response["tasks"]:

        task_id = task["id"]
        task_name = task["name"]
        task_code_url = task["code_url"]

        task_file_name = task_id + ".py"
        uri = directory_save_scripts + task_file_name

        print("Create dirs:", directory_save_scripts)

        if not os.path.exists(str(directory_save_scripts)):
            os.makedirs(str(directory_save_scripts))

        print("Download file from:", task_code_url)

        urllib2.urlretrieve(task_code_url, uri)

        print("Download files success!")
        print()

        task["local_py"] = uri

    print("Save source file:", directory_save_scripts)

    settings = directory_save_scripts + "settings.json"

    json_object = json.dumps(response, indent=4)

    with open(settings, "w") as outfile:
        outfile.write(json_object)


# файл который имитурет выполнение задачи
# здесь можно как выполнять, а также корректировать работу с выполнния определенной строки.

directory_save = os.getcwd() + "\\zhernosek_scripts\\"
directory_save_scripts = directory_save + "3_7\\"

#download_task_error(directory_save_scripts)

#account = get_test_account()




# Активируем нашего робота-убийцу NFT
project = get_local_script(directory_save_scripts)

account = project["profile"]
robot_project_id = project["robot_project_id"]
tasks = project["tasks"]

account_id = account["id"]
account_name = account["name"]
account_dolphin_id = account["dolphin_id"]

parent_uid = account["id"]

callbacks = CallbackFerma()
callbacks.tasks = tasks
callbacks.robot_project_id = robot_project_id
callbacks.parent_uid = parent_uid
callbacks.test = True

# в случае если часть кода выполнена, и нам нужно продолжить выполнение.
# для этого в файл нужно поместить коментарий #restume
# и с этого момента начнется выполнятся код.
callbacks.set_restume()

# запускаем браузер

profile = Profile(account_id, account_name, account_dolphin_id, callbacks)
profile.browser_run()

#profile.set_browser_server_info("127.0.0.1:52306/devtools/browser/774c8416-704c-464b-ac4d-8dd7cb3b0ff5")
profile.connect()
