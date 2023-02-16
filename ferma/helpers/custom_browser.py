import time

from seleniumwire import webdriver
from selenium.webdriver.chrome.options import Options

# working plugin 3.0.6

class CustomBrowser:
    def __init__(self, exec_path, proxy, user_agent, user_data_dir, user_profile_id, extensions):
        self.exec_path = exec_path
        self.user_profile_id = user_profile_id
        self.proxy = proxy
        self.user_agent = user_agent
        self.user_data_dir = user_data_dir + "\\" + self.user_profile_id
        self.extensions = extensions
        self.driver = None

    def connect(self):
        options = Options()

        for ext in self.extensions:
            options.add_extension(ext)

        options.add_argument(f"user-agent={self.user_agent}")
        options.add_argument(f"user-data-dir={self.user_data_dir}")
        #options.add_argument("window-size=1440,768")

        options.add_argument('--no-sandbox')
        options.add_argument('--ignore-certificate-errors-spki-list')
        options.add_argument('--ignore-ssl-errors')
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--lang=en-US")

        # новые параметры, пока не знаю зачем, но типо чтобы нас меньше отслеживать
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument("--enable-aggressive-domstorage-flushing")
        options.add_argument("--profiling-flush=1")                             # кажду секунду сохраняем данные


        wire_options = {
            'proxy': {
                'http': self.proxy,
                'https': self.proxy,
                'no_proxy': 'localhost,127.0.0.1'
            }
        }

        self.driver = webdriver.Chrome(
            executable_path=self.exec_path,
            chrome_options=options,
            seleniumwire_options=wire_options
        )

        return self.driver

    def get_driver(self):
        return self.driver

    def start(self):
        while self.is_browser_alive():
            time.sleep(1)

    def stop(self):
        self.driver.quit()

    def is_browser_alive(self):
        try:
            var = self.driver.current_url
            # or driver.title
            return True
        except:
            return False

#dir = os.path.dirname(os.path.realpath(__file__))

#chromedriver_path = dir + r"\Exec\chromedriver-windows-x64.exe"
#user_data_dir = dir + r"\Browser"
#extensions = ["Canvas-Fingerprint-Defender.crx"]

#assert os.path.exists(chromedriver_path), "chromedriver-windows-x64.exe not found"

#for file in extensions:
#    assert os.path.exists(dir + "\\" + file), file + " not found"

#proxy = "socks5://8ByYP4Hx:qKxvHiMf@45.138.4.158:62943"
#user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36"
#user_profile_id = "prof2"


#customBrowser = CustomBrowser(exec_path, proxy, user_agent, user_data_dir, user_profile_id, extensions)
#driver = customBrowser.driver()

#driver.get("https://amiunique.org/fp")
