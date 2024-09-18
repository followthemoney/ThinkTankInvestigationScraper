from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import random
TOKEN = 'KEY'

class scraper:
    def __init__(self):
        PROXY_DATA = get_proxy()
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # Optional: Run in headless mode
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        PROXY = f"{PROXY_DATA['ip']}:{PROXY_DATA['port']}"# IP:PORT or HOST:PORT        
        chrome_options.add_argument('--proxy-server=socks5://' + PROXY)
        chrome_options.add_argument("--proxy-auth=" + PROXY_DATA['username'] + ":" + PROXY_DATA['password'])
        # Connect to the Selenium server in Docker
        driver = webdriver.Remote(
            command_executor='http://localhost:4444',
            options=chrome_options
        )
        self.driver = driver
        print('driver setup')
        return None

    def get_infos(self, id):
        self.driver.get(f"https://transparency-register.europa.eu/search-details_en?id={id}")
        # Wait for the page to load by waiting for a specific element to be present

        try:
            WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.XPATH, "/html/body/div[3]/main/div/div[2]/div/div/article/div/div/div/table[1]/tbody/tr[1]/td[2]/strong")))
        except:
            return []
        # Now extract the name
        name = self.driver.find_element(By.XPATH, "/html/body/div[3]/main/div/div[2]/div/div/article/div/div/div/table[1]/tbody/tr[1]/td[2]/strong").text
        status = self.driver.find_element(By.XPATH, "/html/body/div[3]/main/div/div[2]/div/div/article/div/div/div/table[1]/tbody/tr[3]/td[2]").text
        registered = self.driver.find_element(By.XPATH, "/html/body/div[3]/main/div/div[2]/div/div/article/div/div/div/table[1]/tbody/tr[4]/td[2]").text
        entity_type = self.driver.find_element(By.XPATH, "/html/body/div[3]/main/div/div[2]/div/div/article/div/div/div/table[2]/tbody/tr[3]/td[2]").text
        total_budget = self.driver.find_element(By.XPATH, "/html/body/div[3]/main/div/div[2]/div/div/article/div/div/div/table[15]/tbody/tr[7]/td[2]").text #
        website = self.driver.find_element(By.XPATH, "/html/body/div[3]/main/div/div[2]/div/div/article/div/div/div/table[2]/tbody/tr[4]/td[2]").text

        comm_meetings_pdf = f"https://ec.europa.eu/transparencyregister/public/meetings/{id}/pdf"
        parl_meeting = f"https://www.europarl.europa.eu/meps/en/search-meetings?transparencyRegisterIds={id}&exportFormat=CSV"

        data = {
            'name' : name,
            'status' : status,
            'registered' : registered,
            'website' : website,
            'entity_type' : entity_type,
            'total_budget' : total_budget,
            'comm_meeting' : comm_meetings_pdf,
            'parl_meeting' : parl_meeting
        }
        return data
    

    def kill(self):
        self.driver.quit()
        return None
    
    
def get_proxy():
    try:
        response = requests.get(
            "https://proxy.webshare.io/api/v2/proxy/list/?mode=direct&page=1&page_size=25",
            headers={"Authorization": f"Token {TOKEN}"}
        )
        response.raise_for_status()  # Raise an HTTPError for bad responses
    except requests.RequestException as e:
        print(f"Failed to get proxy: {e}")
        return
    random_index = random.randint(1, 24)
    PROXY = {
        'ip' : response.json()['results'][random_index]['proxy_address'],
        'port' : response.json()['results'][random_index]['port'],
        'username' : response.json()['results'][random_index]['username'],
        'password' : response.json()['results'][random_index]['password']
    }
    return PROXY

def get_proxies():
    try:
        response = requests.get(
            "https://proxy.webshare.io/api/v2/proxy/list/?mode=direct&page=1&page_size=25",
            headers={"Authorization": f"Token {TOKEN}"}
        )
        response.raise_for_status()  # Raise an HTTPError for bad responses
    except requests.RequestException as e:
        print(f"Failed to get proxy: {e}")
        return
    #random_index = random.randint(1, 24)
    PROXIES = []
    for res in response.json()['results']:
        PROXIES.append({
                'ip' : res['proxy_address'],
                'port' : res['port'],
                'username' : res['username'],
                'password' : res['password']
            })
    return PROXIES




