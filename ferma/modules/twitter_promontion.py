import requests
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from ferma.helpers.custom_browser import CustomBrowser

class TwitterPromontion:
    def __init__(self, manager):
        self.browser = None
        self.manager = manager
        self.server = manager.server
        self.driver = None
        self.driver_wait = None
        self.step = 0
        self.max_steps = 100

    async def start(self, profile_id=""):

        while True:

            response = await self.server.twitterGetLastTask()

            assert await response.text() != "secret key not found!", "неверный секретный ключ!"
            assert await response.text() != "no secret key.", "не найдено ключа!"

            elements = await response.json()

            assert len(elements) != 0, "нет задач."

            for elem in elements:
                type = elem["type"]
                profile = elem["profile"]
                data = elem["data"]

                if self.browser is None:
                    self.browser = self.manager.parse_and_run_browser(profile)
                    self.browser.connect()
                    self.driver = self.browser.get_driver()
                    self.driver_wait = WebDriverWait(self.driver, 15)

                time.sleep(3)

                self.tw_page_check_auth()

                # получим наших подписчиков
                if type == "GET_FOLLOWERS":
                    self.tw_get_followers(data["login"], profile["id"])

                # проверяем пользователя, и если что подписываемся
                if type == "FOLLOW_AND_SCAN_COUNT":
                    result = self.tw_follow_and_scan_count(data["login"], profile["id"])
                    # если мы в бане при подписке, значит отменим процесс.
                    if result == True:
                        print("ACCOUNT IS BAN!")
                        break

                # получаем моих подписчиков
                if type == "SCAN_MY_FOLLOW":
                    self.tw_scan_my_followers(profile["id"])

                # отписываемся
                if type == "UNFOLLOW":
                    self.tw_unfollow(data["login"], profile["id"])

                # узнаем наших подписчиков
                if type == "GET_MY_FOLLOWERS":
                    self.tw_get_my_followers(data["login"], profile["id"])


            # остановим задачу
            if self.browser is not None:
                self.browser.stop()
                self.browser = None
                time.sleep(4)

            print("ждем следующего действия :)", self.step)

            self.step = self.step + 1
            if self.step > self.max_steps:
                break

    def tw_page_check_auth(self):

        if "twitter.com" not in self.driver.current_url:
            self.driver.get("https://twitter.com/")
            time.sleep(2)
        try:
            self.driver.find_element(By.XPATH, "//a[@href='/compose/tweet']").text
        except:
            input("авторизуйте в твиттере, и нажми на Enter...")

    def tw_follow(self, url):
        print("подписываемся на", url)
        try:
            if url is not None:
                self.driver.get(url)

            time.sleep(1.5)

            follow = self.driver_wait.until(EC.element_to_be_clickable((By.XPATH, '//span[text()="Follow"]')))
            self.driver.execute_script("arguments[0].click();", follow)

            # проверим, лимит не превышен?
            time.sleep(1.5)

            try:
                # найти все span элементы, и проверить текст
                spans = self.driver.find_elements(By.TAG_NAME, "span")
                if spans:
                    for s in spans:
                        if s and s.text:
                            if "You are unable to follow more people at this time." in str(s.text):
                                return "UNABLE_FOOLOW"
            except:
                pass

            return "OK"

        except Exception as ex:
            print("ошибка при фоловинге:", ex)
            time.sleep(2)

            return "FAIL"

    #
    def tw_parse_follow_text(self, text):

        text = text.replace(",", "")
        text = text.replace(" ", "")
        #text = text.replace(".", "")
        count = -1

        if text[-1:] == "K":
            count = text[:-1]
            count = float(count)
            count = count * 1000
        elif text[-1:] == "M":
            count = text[:-1]
            count = float(count)
            count = count * 1000000
        else:
            count = float(text)

        return count


    def tw_get_followers(self, profile, user_id):

        print("Узнаем подписчиков для @", profile)

        follower_list = []
        step = 0
        max_steps = 15

        # открываем всех подписчиков
        self.driver.get("https://twitter.com/"+profile+"/followers")
        time.sleep(2)

        # Code to goto End of the Page
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        while True:
            # Scroll down to bottom
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            # Wait to load page
            time.sleep(2)
            # Calculate new scroll height and compare with last scroll height
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

            usernames = self.driver.find_elements(By.CLASS_NAME, "css-901oao.css-16my406.r-poiln3.r-bcqeeo.r-qvutc0")
            for a in usernames:
                try:
                    text = a.text
                    if text and text[:1] == "@":
                        username = text[1:]
                        if username not in follower_list:
                            print(username, "add.")
                            follower_list.append(username)
                except:
                    pass

            step = step + 1
            if step >= max_steps:
                break

        time.sleep(1)
        self.result_server("result_followers", {'user_id': str(user_id), 'result': ",".join(follower_list)})


    def tw_follow_and_scan_count(self, profile, user_id):

        print("смотрим на подписчика, и подписываемся если нам такое подходит @", profile)

        # открываем всех подписчиков
        self.driver.get("https://twitter.com/"+profile)
        time.sleep(2)

        followers = -2
        following = -2
        follow = False
        ban = False

        # parse
        try:
            followers_datas = self.driver.find_elements(By.CSS_SELECTOR, ".css-901oao.css-16my406.r-18jsvk2.r-poiln3.r-1b43r93.r-b88u0q.r-1cwl3u0.r-bcqeeo.r-qvutc0 .css-901oao.css-16my406.r-poiln3.r-bcqeeo.r-qvutc0")

            following = self.tw_parse_follow_text(followers_datas[0].text)
            followers = self.tw_parse_follow_text(followers_datas[1].text)

            if following == 0:
                following = 1

            if followers == 0:
                followers = 1

            print("following", following, "followers", followers)

        except Exception as e:
            time.sleep(1)
            print("err", e)
            pass

        time.sleep(1)

        # условия подписываемся или нет?
        if following > 0 and following > 0:
            calc = following / followers

            # если не менее 20% он сам подписан, то скорее всего это бот
            if calc > 0.8 and calc < 2.2:
                # None --> мы находимся на этой странаице
                status_follow = self.tw_follow(None)

                if status_follow == "OK" or status_follow == "FAIL":
                    follow = True
                else:
                    ban = True

        time.sleep(1)
        self.result_server("result_follow_and_scan_count", {'user_id': user_id,
                   'login': profile,
                   'followers': followers,
                   'following': following,
                   'follow': follow,
                   'ban': ban})

        return ban



    #
    def tw_scan_my_followers(self, user_id):

        follower_list = []
        step = 0
        max_steps = 100

        self.driver.get("https://twitter.com/followers")
        time.sleep(2)

        last_height = self.driver.execute_script("return document.body.scrollHeight")
        while True:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

            usernames = self.driver.find_elements(By.CLASS_NAME, "css-901oao.css-16my406.r-poiln3.r-bcqeeo.r-qvutc0")

            for a in usernames:
                try:
                    text = a.text
                    if text and text[:1] == "@":
                        username = text[1:]
                        if username not in follower_list:
                            print(username, "+")
                            follower_list.append(username)
                except:
                    pass

            step = step + 1
            if step >= max_steps:
                break

        time.sleep(1)
        self.result_server("result_scan_my_followers", {'user_id': str(user_id), 'result': ",".join(follower_list)})

    def tw_unfollow(self, profile, user_id):

        print("отписываемся от @", profile)

        try:
            self.driver.get("https://twitter.com/" + profile)

            time.sleep(1)

            unfollow = self.driver_wait.until(EC.element_to_be_clickable((By.XPATH, '//span[text()="Following"]')))
            self.driver.execute_script("arguments[0].click();", unfollow)

            time.sleep(1)

            unfollow2 = self.driver_wait.until(EC.element_to_be_clickable((By.XPATH, '//span[text()="Unfollow"]')))
            self.driver.execute_script("arguments[0].click();", unfollow2)

            time.sleep(1)

        except Exception as ex:
            print("отписаться не получилось от @", profile, ", по причине", ex)
            time.sleep(1)

        time.sleep(1)
        self.result_server("result_unfollow", {'user_id': str(user_id), 'login': profile})

    def tw_get_my_followers(self, profile, user_id):

        print("смотрим подписчиков @", profile)

        # открываем всех подписчиков
        self.driver.get("https://twitter.com/"+profile)
        time.sleep(2)

        followers = -2
        following = -2

        # parse
        try:
            followers_datas = self.driver.find_elements(By.CLASS_NAME, "css-901oao.css-16my406.r-18jsvk2.r-poiln3.r-1b43r93.r-b88u0q.r-1cwl3u0.r-bcqeeo.r-qvutc0 .css-901oao.css-16my406.r-poiln3.r-bcqeeo.r-qvutc0")

            following = self.tw_parse_follow_text(followers_datas[0].text)
            followers = self.tw_parse_follow_text(followers_datas[1].text)

            if following == 0:
                following = 1

            if followers == 0:
                followers = 1

            print("following", following, "followers", followers)

        except Exception as e:
            time.sleep(1)
            print("err", e)
            pass

        time.sleep(1)
        self.result_server("result_my_followers", {'user_id': str(user_id), 'login': str(profile), 'followers': str(followers), 'following': str(following)})


    def result_server(self, method, datas):

        url = "http://checks.wordok.by/twitter/api.php?method=" + method + "&secret_key=" + str(self.server.secret_key)
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5)'}

        response = requests.request("POST", url, headers=headers, data=datas)

        if (response.json())["status"] == "success":
            print("--> успешно!")
        else:
            print("--> ошибка:", response.text)
