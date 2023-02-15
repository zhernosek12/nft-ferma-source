import aiohttp

class Server:
    def __init__(self, secret_key):
        self.secret_key = secret_key
        self.url_api = 'http://ferma.zhernosek.xyz/Api.php'
        #self.url = "http://ferma.zhernosek.xyz/Api.php?method=setScriptStatus"

    async def checkKey(self):
        async with aiohttp.ClientSession() as session:
            response = await session.get(
                url=self.url_api + "?method=checkKey&secret_key=" + self.secret_key,
            )
        return response

    async def myProfiles(self):
        async with aiohttp.ClientSession() as session:
            response = await session.get(
                url=self.url_api + "?method=myProfiles&secret_key=" + self.secret_key,
            )
        return response

    async def profileInfo(self, username):
        async with aiohttp.ClientSession() as session:
            response = await session.get(
                url=self.url_api + "?method=profileInfo&username=" + username + "&secret_key=" + self.secret_key,
            )
        return response

    async def robotProject(self):
        async with aiohttp.ClientSession() as session:
            response = await session.get(
                url=self.url_api + "?method=getRobotProject&secret_key=" + self.secret_key,
            )
        return response

    async def script_error(self, profile_id, robot_script_id, robot_project_id, message):
        async with aiohttp.ClientSession() as session:
            response = await session.post(
                url=self.url_api + "?method=setScriptStatus&secret_key=" + self.secret_key,
                data={'profile_id': profile_id,
                      'robot_project_id': robot_project_id,
                      'robot_script_id': robot_script_id,
                      'type': 'fail',
                      'message': message}
            )
        print(await response.text())

    async def script_success(self, profile_id, robot_script_id, robot_project_id):
        async with aiohttp.ClientSession() as session:
            response = await session.post(
                url=self.url_api + "?method=setScriptStatus&secret_key=" + self.secret_key,
                data={'profile_id': profile_id,
                      'robot_project_id': robot_project_id,
                      'robot_script_id': robot_script_id,
                      'type': 'success',
                      'message': ''}
            )
        print(await response.text())

    async def request_script_finish(self, profile_id, robot_project_id, type):
        async with aiohttp.ClientSession() as session:
            response = await session.post(
                url=self.url_api + "?method=setScriptStatus&secret_key=" + self.secret_key,
                data={'profile_id': profile_id,
                      'robot_project_id': robot_project_id,
                      'type': type}
            )

        print(await response.text())

"""
def get_test_account():

    url = "http://ferma.zhernosek.xyz/Api.php?method=getTestAccount"

    payload = {}
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5)'}

    response = requests.request("GET", url, headers=headers, data=payload)

    return response.json()



def get_robot_project_error():

    url = "http://ferma.zhernosek.xyz/Api.php?method=getRobotProject&robot_project_id=3&profile_id=7"

    payload = {}
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5)'}

    response = requests.request("GET", url, headers=headers, data=payload)

    return response.json()

"""