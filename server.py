import aiohttp

class Server:
    def __init__(self, secret_key):
        self.secret_key = secret_key
        self.url_api = 'http://ferma.zhernosek.xyz/Api.php'
        self.url_api_twitter = 'http://checks.wordok.by/twitter/router.php'
        self.headers = {"Content-Type": "application/json"}
        self.timeout = aiohttp.ClientTimeout(total=10)

    async def checkKey(self):
        async with aiohttp.ClientSession() as session:
            response = await session.get(
                url=self.url_api + "?method=checkKey&secret_key=" + self.secret_key,
            )
            await response.text()
        return response

    async def myProfiles(self):
        async with aiohttp.ClientSession() as session:
            response = await session.get(
                url=self.url_api + "?method=myProfiles&secret_key=" + self.secret_key,
            )
            await response.text()
        return response

    async def profileInfo(self, username):
        async with aiohttp.ClientSession() as session:
            response = await session.get(
                url=self.url_api + "?method=profileInfo&username=" + username + "&secret_key=" + self.secret_key,
            )
            await response.text()
        return response

    async def robotProject(self):
        async with aiohttp.ClientSession() as session:
            response = await session.get(
                url=self.url_api + "?method=getRobotProject&secret_key=" + self.secret_key,
            )
            await response.text()
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
            await response.text()
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
            await response.text()
        print(await response.text())

    async def request_script_finish(self, profile_id, robot_project_id, type):
        async with aiohttp.ClientSession() as session:
            response = await session.post(
                url=self.url_api + "?method=setScriptStatus&secret_key=" + self.secret_key,
                data={'profile_id': profile_id,
                      'robot_project_id': robot_project_id,
                      'type': type}
            )
            await response.text()
        print(await response.text())

    """
        твиттер
    """
    async def twitterGetLastTask(self):
        async with aiohttp.ClientSession(headers=self.headers, timeout=self.timeout) as session:
            response = await session.get(
                url=self.url_api_twitter + "?secret_key=" + self.secret_key,
            )
            await response.text()

        return response

    async def search_error_scripts(self):
        async with aiohttp.ClientSession(headers=self.headers, timeout=self.timeout) as session:
            response = await session.get(
                url=self.url_api + "?method=searchErrorScripts&secret_key=" + self.secret_key,
            )
            await response.text()

        return response

    async def download_script(self, script_id):
        async with aiohttp.ClientSession(headers=self.headers, timeout=self.timeout) as session:
            response = await session.get(
                url=self.url_api + "?method=getSourceScript&secret_key=" + self.secret_key + "&script_id=" + str(script_id),
            )
            await response.text()

        return response

    async def publish_source_script(self, script_id, source_code):
        # source_code
        async with aiohttp.ClientSession() as session:
            response = await session.post(
                url=self.url_api + "?method=publishSourceScript&secret_key=" + self.secret_key + "&script_id=" + str(script_id),
                data={'source_code': source_code}
            )
            await response.text()
        return response

    async def dev_get_all_scripts(self):
        async with aiohttp.ClientSession(headers=self.headers, timeout=self.timeout) as session:
            response = await session.get(
                url=self.url_api + "?method=getAllScripts&secret_key=" + self.secret_key,
            )
            await response.text()
        return response