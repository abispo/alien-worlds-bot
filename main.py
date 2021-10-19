from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from time import sleep
import pathlib
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from random import randint
import requests

from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

caps = DesiredCapabilities.CHROME

# TODO: Get response from network in browser
caps['goog:loggingPrefs'] = {'performance': 'ALL'}


def get_used_percentage_cpu():
    URL = 'https://wax.greymass.com/v1/chain/get_account'
    response = requests.post(URL, json={'account_name': 'azyse.wam'}).json()
    cpu_limit = response.get('cpu_limit')
    used_cpu = cpu_limit.get('used')
    max_cpu = cpu_limit.get('max')

    percentage_used = round((used_cpu*100)/max_cpu)

    return percentage_used


if __name__ == '__main__':
    options = Options()
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument(f"user-data-dir={pathlib.Path().resolve()}/chrome_profile")
    options.add_argument('--ignore-certificate-errors-spki-list')
    options.add_argument('--ignore-ssl-errors')
    driver = webdriver.Chrome(options=options, desired_capabilities=caps)

    driver.get('https://play.alienworlds.io/')
    start_now_button = WebDriverWait(driver, 100).until(EC.presence_of_element_located((By.XPATH, "//*[text()='Start Now']")))
    start_now_button.click()
    WebDriverWait(driver, 100).until(EC.presence_of_element_located((By.XPATH, "//*[text()='Trilium Balance']")))

    while True:
        used_cpu_percentage = get_used_percentage_cpu()

        while used_cpu_percentage >= 90:
            print(f'USED CPU PERCENTAGE: {used_cpu_percentage}')
            print(f'WAITING FOR 600s...')
            for i in range(600, 0, -1):
                print(f"{i}s LEFT...", end='\r')
                sleep(1)
            used_cpu_percentage = get_used_percentage_cpu()

        mine_button = WebDriverWait(driver, 600).until(EC.presence_of_element_located((By.XPATH, "//*[text()='Mine']")))
        if mine_button:
            sleep(randint(1, 3))
            mine_button.click()
            # Esperar aparecer o texto Claim Mine
            claim_mine_button = WebDriverWait(driver, 300).until(EC.presence_of_element_located((By.XPATH, "//*[text()='Claim Mine']")))
            # Clicar no botão para o Claim
            claim_mine_button.click()
            # Alterar o foco da Janela
            WebDriverWait(driver, 300).until(EC.number_of_windows_to_be(2))
            another_window = list(set(driver.window_handles) - {driver.current_window_handle})[0]
            driver.switch_to.window(another_window)
            # Clicar no botão aprove
            approve_button = WebDriverWait(driver, 300).until(EC.presence_of_element_located((By.XPATH, "//*[text()='Approve']")))
            approve_button.click()
            WebDriverWait(driver, 300).until(EC.number_of_windows_to_be(1))
            driver.switch_to.window(driver.window_handles[0])
            # Verificar se deu boa ou ruim
            # https://aw-guard.yeomen.ai/v1/chain/push_transaction HTTP 202

    driver.close()
