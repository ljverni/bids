from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
import requests
import re
import time


link = "https://comprar.gob.ar/PLIEGO/VistaPreviaPliegoCiudadano.aspx?qs=BQoBkoMoEhzx8zvkTDdwTXg17CFDfb9gjz|hkhikVuyhUW1N8Tfv5zjexUkKfyHHxcg3AZulJorys/QkdmWV5fw7Z5QjQLd2M0P5kfWqNWehoUyNMe16yC4Pdh8gFi94uVNDZzV4kXjLgb2wbcE23HGRBQNBx|acgVvZv5d3Ya6JgsxUdFvBNQ=="

class BidScrape():

    def __init__(self, url, page_counter, tab_counter):
        self.driver = webdriver.Chrome("\webdrivers\chromedriver.exe")
        self.driver.set_script_timeout(20)
        accept_next_alert = True
        delay = 3
        self.driver.get(url)
        self.common_exceptions = (TimeoutException, ElementClickInterceptedException)
        self.page_counter = page_counter
        self.tab_counter = tab_counter 
    
    def query_search(self):
        driver = self.driver
        status = Select(driver.find_element_by_id("ctl00_CPH1_ddlEstadoProceso"))
        status.options[1].click()
        driver.find_element_by_id("ctl00_CPH1_btnListarPliegoAvanzado").click()
        
    def extract(self):
        # WebDriverWait(self.driver, 30).until(EC.element_to_be_clickable((By.XPATH,  "//*[@id='ctl00_CPH1_lnkVolver']"))).click()
        self.driver.execute_script("arguments[0].click();", WebDriverWait(self.driver, 30).until(EC.element_to_be_clickable((By.XPATH,  f"//*[@id='ctl00_CPH1_lnkVolver']"))))
      
            
    def first_page_jump(self):
        self.driver.execute_script("arguments[0].click();", WebDriverWait(self.driver, 30).until(EC.element_to_be_clickable((By.XPATH, "//*[@id='ctl00_CPH1_GridListaPliegos']/tbody/tr[11]/td/table/tbody/tr/td[11]/a"))))
   
        
    def page_jump(self, idx):
        time.sleep(5)
        self.driver.execute_script("arguments[0].click();", WebDriverWait(self.driver, 30).until(EC.element_to_be_clickable((By.XPATH, f"//*[@id='ctl00_CPH1_GridListaPliegos']/tbody/tr[{idx[0]}]/td/table/tbody/tr/td[{idx[1]}]/a"))))
            
    def tab_jump(self, tab_idx):
        time.sleep(5)
        self.driver.execute_script("arguments[0].click();", WebDriverWait(self.driver, 30).until(EC.element_to_be_clickable((By.LINK_TEXT, f"{tab_idx}"))))
         
    def click_process(self, row):
        time.sleep(5)
        self.driver.execute_script("arguments[0].click();", WebDriverWait(self.driver, 30).until(EC.element_to_be_clickable((By.XPATH,  f"//*[@id='ctl00_CPH1_GridListaPliegos_ctl{row}_lnkNumeroProceso']"))))
        # self.wait_background()
        # WebDriverWait(self.driver, 30).until(EC.element_to_be_clickable((By.XPATH,  f"//*[@id='ctl00_CPH1_GridListaPliegos_ctl{row}_lnkNumeroProceso']"))).click()
      
        
    def scrape(self):
        driver = self.driver
        self.first_page_jump()
        if self.page_counter > 1:
            for scraped_pages in range(self.page_counter - 1):
                self.page_jump([12, 12])
        if (self.tab_counter % 10) > 0:
            self.tab_jump(self.tab_counter+1)
    
        for n in range(20):
            for row in range(2, 12):
                row = format(row, "02d")
                self.click_process(row)
                self.extract()
                print("Row " + str(row) + " scraped")
            
            if ((self.tab_counter+1) % 10) == 0:
                self.page_jump([11, 12])
                self.page_counter += 1
                print("Page " + str(self.page_counter) + " scraped")
                self.tab_counter += 1
                print("Tab " + str(self.tab_counter) + " scraped")
            else:
                self.tab_counter += 1
                print("Tab " + str(self.tab_counter) + " scraped")
                self.tab_jump(self.tab_counter + 1)
                
                
            
           
         
            
            
        # except (TimeoutException, NoSuchElementException) as error:
        #     print("finalizing due to error...")
        #     self.driver.quit()
        #     print(self.page_counter, self.tab_counter, self.row_counter)
        #     raise
            
        # print("Scraping successful")
        # self.driver.quit()
        # print(self.page_counter, self.tab_counter, self.row_counter)
    

        
compras_ar = BidScrape("https://comprar.gob.ar/BuscarAvanzado.aspx", 1, 18)
compras_ar.query_search()
compras_ar.scrape()



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

