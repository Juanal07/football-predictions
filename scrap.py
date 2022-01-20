from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC, wait
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import *
import requests
import re
from webdriver_manager.chrome import ChromeDriverManager

driver = webdriver.Chrome(ChromeDriverManager().install())



jugador = "Wayne Rooney"
print(jugador)
# https://www.transfermarkt.co.uk/schnellsuche/ergebnis/schnellsuche?query=Wayne%20Rooney
jugador = re.sub(' ','%20', jugador)
URL = 'https://www.transfermarkt.co.uk/schnellsuche/ergebnis/schnellsuche?query='+jugador
print(URL)
driver.get(URL)
# aceptamos cookies
# comaut = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#notice > div.message-component.message-row.mobile-reverse > div:nth-child(2) > button")))
# comaut.click()