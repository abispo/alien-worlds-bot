from utils import get_used_percentage_cpu

from datetime import datetime
from time import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from time import sleep
import pathlib
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from random import randint

from selenium.common.exceptions import NoSuchElementException

import settings

MAX_CPU_USAGE_PERCENTAGE = 90


class AlienWorldsBot:

    def __init__(self, *args, **kwargs):

        self._game_url = "https://play.alienworlds.io/"

        self._options = Options()
        self._options.add_argument('--disable-blink-features=AutomationControlled')
        self._options.add_argument(f"user-data-dir={pathlib.Path().resolve()}/chrome_profile")
        self._options.add_argument('--ignore-certificate-errors-spki-list')
        self._options.add_argument('--ignore-ssl-errors')

        self._driver = webdriver.Chrome(options=self._options)
        self._last_mine_attempt_timestamp = datetime.utcfromtimestamp(time())

    def _is_waiting_timeout(self):
        date_now = datetime.utcfromtimestamp(time())
        print((date_now - self._last_mine_attempt_timestamp).total_seconds())
        return (date_now - self._last_mine_attempt_timestamp).total_seconds() > settings.WAITING_TIMEOUT

    def _access_website_and_do_login(self):
        self._driver.get(self._game_url)
        start_now_button = WebDriverWait(self._driver, 100).until(
            EC.presence_of_element_located((By.XPATH, "//*[text()='Start Now']")))

        start_now_button.click()
        WebDriverWait(self._driver, 100).until(
            EC.presence_of_element_located((By.XPATH, "//*[text()='Trilium Balance']")))

    def _is_claim_button_active(self):
        try:
            self._driver.find_element_by_xpath("//*[text()='Claim Mine']")
        except NoSuchElementException as e:
            return False

        return True

    def _mine_button_click(self):
        mine_button = WebDriverWait(self._driver, 600).until(
            EC.presence_of_element_located((By.XPATH, "//*[text()='Mine']")))
        sleep(randint(1, 3))
        mine_button.click()

    def _claim_button_click(self):
        claim_mine_button = WebDriverWait(self._driver, 300).until(
            EC.presence_of_element_located((By.XPATH, "//*[text()='Claim Mine']")))
        sleep(randint(1, 3))
        claim_mine_button.click()

    def _change_window_focus(self):
        WebDriverWait(self._driver, 300).until(EC.number_of_windows_to_be(2))
        another_window = list(set(self._driver.window_handles) - {self._driver.current_window_handle})[0]
        self._driver.switch_to.window(another_window)

    def _approve_button_click(self):
        approve_button = WebDriverWait(self._driver, 300).until(
            EC.presence_of_element_located((By.XPATH, "//*[text()='Approve']")))
        sleep(1, 5)
        approve_button.click()

    def _set_focus_to_main_window(self):
        WebDriverWait(self._driver, 300).until(EC.number_of_windows_to_be(1))
        self._driver.switch_to.window(self._driver.window_handles[0])

    def run(self):
        self._access_website_and_do_login()

        while True:
            used_cpu_percentage = get_used_percentage_cpu()

            while self._is_waiting_timeout() or used_cpu_percentage <= MAX_CPU_USAGE_PERCENTAGE:
                print(f'USED CPU PERCENTAGE: {used_cpu_percentage}')
                print(f'WAITING FOR 60s...')
                sleep(settings.WAITING_TIMEOUT)
                used_cpu_percentage = get_used_percentage_cpu()

            if not self._is_claim_button_active():
                self._mine_button_click()

            self._claim_button_click()
            self._change_window_focus()
            self._approve_button_click()
            self._set_focus_to_main_window()


if __name__ == '__main__':
    alien_worlds_bot = AlienWorldsBot()
    alien_worlds_bot.run()