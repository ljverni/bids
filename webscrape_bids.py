from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
import requests
import re
import unittest
import time


link = "https://comprar.gob.ar/PLIEGO/VistaPreviaPliegoCiudadano.aspx?qs=BQoBkoMoEhzx8zvkTDdwTXg17CFDfb9gjz|hkhikVuyhUW1N8Tfv5zjexUkKfyHHxcg3AZulJorys/QkdmWV5fw7Z5QjQLd2M0P5kfWqNWehoUyNMe16yC4Pdh8gFi94uVNDZzV4kXjLgb2wbcE23HGRBQNBx|acgVvZv5d3Ya6JgsxUdFvBNQ=="


driver = webdriver.Chrome("\webdrivers\chromedriver.exe")
delay = 3
driver.get(link)
source = driver.page_source
html = BeautifulSoup(source, "lxml")

bid_code = driver.find_element_by_css_selector('span[id*="NumeroProceso"]').text
name = driver.find_element_by_css_selector('span[id*="NombreProceso"]').text
process = driver.find_element_by_css_selector('span[id*="ProcedimientoSeleccion"]').text
stage = driver.find_element_by_css_selector('span[id*="Etapa"]').text
validity = driver.find_element_by_css_selector('span[id*="MantenimientoOferta"]').text
duration = driver.find_element_by_css_selector('span[id*="DuracionContrato"]').text
opening = driver.find_element_by_css_selector('table[id*="ActasApertura"] p').text
contract_info = driver.find_elements_by_css_selector('table[id*="DetalleImputacionAdjudicacion"] td')
awarded_bidder = contract_info[1].text
awarder_bidder_id = contract_info[2].text
amount = contract_info[6].text
currency = contract_info[7].text

products = [product.text for product in driver.find_elements_by_css_selector('span[id*="lblDescripcion"]')]
products_qty = [qty.text for qty in driver.find_elements_by_css_selector('span[id*="lblCantidad"]')]

driver.quit()