from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import random
TOKEN = ''

class scraper:
    def __init__(self):
        PROXY_DATA = random.choice(get_proxies())
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
        # Now extract the name
        name = self.driver.find_element(By.XPATH, "/html/body/div[3]/main/div/div[2]/div/div/article/div/div/div/table[1]/tbody/tr[1]/td[2]/strong").text
        status = self.driver.find_element(By.XPATH, "/html/body/div[3]/main/div/div[2]/div/div/article/div/div/div/table[1]/tbody/tr[3]/td[2]").text
        registered = self.driver.find_element(By.XPATH, "/html/body/div[3]/main/div/div[2]/div/div/article/div/div/div/table[1]/tbody/tr[4]/td[2]").text
        entity_type = self.driver.find_element(By.XPATH, "/html/body/div[3]/main/div/div[2]/div/div/article/div/div/div/table[2]/tbody/tr[3]/td[2]").text
        profile = self.driver.find_element(By.ID, 'goalsremit')
        description_table = profile.find_element(By.XPATH, "following-sibling::*")
        description = description_table.find_elements(By.CSS_SELECTOR, '.ecl-table__body > tr')[0].find_elements(By.CSS_SELECTOR,'.ecl-table__cell')[1].text
        funding = self.driver.find_element(By.ID, 'financial-data')
        table = funding.find_element(By.XPATH, 'following-sibling::*')
        table2 = table.find_elements(By.CSS_SELECTOR, '.ecl-table__body > tr')[3]
        table_content = table2.find_elements(By.CSS_SELECTOR, 'td')[1]
        funding_list = []
        for el in table_content.find_elements(By.CSS_SELECTOR, '.ecl-table__cell > div > ul > li'):
            funding_list.append(el.text)
        financial_data = self.driver.find_elements(By.CLASS_NAME, "ecl-table--zebra")[14]
        try:
            total_budget_row = financial_data.find_element(By.XPATH, ".//tbody/tr[contains(.,'Total budget:')]")
            total_budget_cells = total_budget_row.find_elements(By.XPATH, "./td")
            total_budget = total_budget_cells[1].text if len(total_budget_cells) > 1 else "Not found"
            funders = financial_data.find_element(By.XPATH, ".//tbody/tr[contains(.,'Contributions in the closed financial year')]")
            funders_names_cells = funders.find_elements(By.XPATH, "./td")[1].find_elements(By.CSS_SELECTOR, '.ecl-table__cell > table tbody tr')
            funding = []
            for element in funders_names_cells:
                row = element.find_elements(By.CSS_SELECTOR, 'td')
                dict_fund = {'funder' : row[0].text,
                            'amount' : row[1].text}
                funding.append(dict_fund)
            #total_budget = funders_names_celles[1].text if len(total_budget_cells) > 1 else "Not found"
        except Exception as e:
            total_budget = "Not found"
            print(f"Error finding total budget: {e}")

        involved = self.driver.find_element(By.ID, 'number-of-persons-involved-in-the-activities')
        table = involved.find_element(By.XPATH, 'following-sibling::*')
        table2 = table.find_elements(By.CSS_SELECTOR, '.ecl-table__body > tr')[1]
        pp_involved = table2.find_elements(By.CSS_SELECTOR, 'td')[1].text
        table2 = table.find_elements(By.CSS_SELECTOR, '.ecl-table__body > tr')[2]
        fte_involed = table2.find_elements(By.CSS_SELECTOR, 'td')[1].text
        country_table = self.driver.find_elements(By.CLASS_NAME, "ecl-table--zebra")[2]
        country = country_table.find_element(By.XPATH, ".//tbody/tr[2]/td[2]/span[6]").text
        comm_meetings_pdf = f"https://ec.europa.eu/transparencyregister/public/meetings/{id}/pdf"
        parl_meeting = f"https://www.europarl.europa.eu/meps/en/search-meetings?transparencyRegisterIds={id}&exportFormat=CSV"
        website = self.driver.find_element(By.XPATH, "/html/body/div[3]/main/div/div[2]/div/div/article/div/div/div/table[2]/tbody/tr[4]/td[2]").text
        legal_responsible = 'Not found'
        EU_responsible = 'Not found'
        try:
            responsible = self.driver.find_element(By.ID, 'person-with-legal-responsibility')
            responsible_table = responsible.find_element(By.XPATH, 'following-sibling::*')
            table2 = responsible_table.find_elements(By.CSS_SELECTOR, '.ecl-table--zebra')
            legal_responsible_table = responsible_table.find_element(By.XPATH, ".//tbody/tr[contains(.,'Person with legal responsibility for the organisation:')]")
            legal_responsible = legal_responsible_table.find_elements(By.XPATH, "./td")[1].text

            responsible = self.driver.find_element(By.ID, 'person-in-charge-of-eu-relations')
            responsible_table = responsible.find_element(By.XPATH, 'following-sibling::*')
            table2 = responsible_table.find_elements(By.CSS_SELECTOR, '.ecl-table--zebra')
            EU_responsible_table = responsible_table.find_element(By.XPATH, ".//tbody/tr[contains(.,'Person in charge of EU relations:')]")
            EU_responsible = EU_responsible_table.find_elements(By.XPATH, "./td")[1].text
            EU_responsible = legal_responsible if EU_responsible == 'Same as above' else EU_responsible
        except Exception as e:
            print(f"Error finding legal responsible: {e}")
            legal_responsible = 'Not found'

        data = {
            'name' : name,
            'status' : status,
            'registered' : registered,
            'website' : website,
            'entity_type' : entity_type,
            'total_budget' : total_budget,
            'pp_involved' : pp_involved,
            'fte_involed' : fte_involed,
            'funding_source' : funding_list,
            'funding' : funding,
            'legal_responsible' : legal_responsible,
            'EU_responsible' : EU_responsible,
            'comm_meeting' : comm_meetings_pdf,
            'parl_meeting' : parl_meeting,
            'country' : country,
            'description' : description
        }        
        return data
    

    def kill(self):
        self.driver.quit()
        return None
    

def get_proxies():
    try:
        response = requests.get(
            "https://proxy.webshare.io/api/v2/proxy/list/?mode=direct&page=1&page_size=100",
            headers={"Authorization": f"Token {TOKEN}"}
        )
        response.raise_for_status()  # Raise an HTTPError for bad responses
    except requests.RequestException as e:
        print(f"Failed to get proxy: {e}")
        return
    PROXIES = []
    for res in response.json()['results']:
        PROXIES.append({
                'ip' : res['proxy_address'],
                'port' : res['port'],
                'username' : res['username'],
                'password' : res['password']
            })
    return PROXIES




