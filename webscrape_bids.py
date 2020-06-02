from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import NoSuchElementException
import re
import time


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
        
    def selector(self, qty, arg):
        if qty == "u":
            return self.driver.find_element_by_css_selector(arg).text
        elif qty == "b":
            return self.driver.find_elements_by_css_selector(arg)
        
    def extract(self):
        selector = self.selector
        contract_info = selector("b", "table[id*='DetalleImputacionAdjudicacion'] td")
        data_main = {         
            {"bid_code": selector("u", "span[id*='NumeroProceso']")}, 
            {"name": selector("u", "span[id*='NombreProceso']")}, 
            {"process": selector("u", "span[id*='ProcedimientoSeleccion']")}, 
            {"stage": selector("u", "span[id*='Etapa']")}, 
            {"validity": selector("u", "span[id*='MantenimientoOferta']")}, 
            {"duration": selector("u", "span[id*='DuracionContrato']")}, 
            {"opening": selector("u", "table[id*='ActasApertura'] p")}, 
            {"awarded_bidder": contract_info[1].text}, 
            {"awarder_bidder_id": contract_info[2].text}, 
            {"amount": contract_info[6].text}, 
            {"currency": contract_info[7].text}      
            } 
        products = [product.text for product in selector("b", "span[id*='lblDescripcion']")]
        products_qty = [qty.text for qty in selector("b", "span[id*='lblCantidad']")]
        data_products = {"bid_code": [], "product": [], "qty": []}
        for prod in range(len(products)):
            data_products["bid_code"].append(selector("u", "span[id*='NumeroProceso']"))
            data_products["product"].append(products[prod])
            data_products["qty"].append(products_qty[prod])
        return data_main, data_products
            
    def exit_process(self):
        self.driver.execute_script("arguments[0].click();", WebDriverWait(self.driver, 30).until(EC.element_to_be_clickable((By.XPATH,  f"//*[@id='ctl00_CPH1_lnkVolver']"))))
        
    def first_page_jump(self):
        self.driver.execute_script("arguments[0].click();", WebDriverWait(self.driver, 30).until(EC.element_to_be_clickable((By.XPATH, "//*[@id='ctl00_CPH1_GridListaPliegos']/tbody/tr[11]/td/table/tbody/tr/td[11]/a"))))
      
    def page_jump(self, idx):
        time.sleep(5)
        self.driver.execute_script("arguments[0].click();", WebDriverWait(self.driver, 30).until(EC.element_to_be_clickable((By.XPATH, f"//*[@id='ctl00_CPH1_GridListaPliegos']/tbody/tr[{idx[0]}]/td/table/tbody/tr/td[{idx[1]}]/a"))))
            
    def tab_jump(self, tab_idx):
        time.sleep(5)
        self.driver.execute_script("arguments[0].click();", WebDriverWait(self.driver, 30).until(EC.element_to_be_clickable((By.LINK_TEXT, f"{tab_idx}"))))
         
    def enter_process(self, row):
        time.sleep(5)
        self.driver.execute_script("arguments[0].click();", WebDriverWait(self.driver, 30).until(EC.element_to_be_clickable((By.XPATH,  f"//*[@id='ctl00_CPH1_GridListaPliegos_ctl{row}_lnkNumeroProceso']"))))

    def scrape(self, tab_n):
        driver = self.driver
        self.first_page_jump()
        if self.page_counter > 1:
            for scraped_pages in range(self.page_counter - 1):
                self.page_jump([12, 12])
        if (self.tab_counter % 10) > 0:
            self.tab_jump(self.tab_counter+1)
    
        for n in range(tab_n):
            for row in range(2, 12):
                row = format(row, "02d")
                self.enter_process(row)
                extracted_data = self.extract()
                self.exit_process()
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
        self.driver.quit()    
        
                
compras_ar = BidScrape("https://comprar.gob.ar/BuscarAvanzado.aspx", 1, 18)
compras_ar.query_search()
compras_ar.scrape(10)






