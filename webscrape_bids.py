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
from datetime import datetime
from datetime import date
from time import perf_counter
import pandas as pd
from os import path
import json

t1_start = perf_counter()
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
        self.iteration = 0
    
    def query_search(self):
        driver = self.driver
        status = Select(driver.find_element_by_id("ctl00_CPH1_ddlEstadoProceso"))
        status.options[1].click()
        driver.find_element_by_id("ctl00_CPH1_btnListarPliegoAvanzado").click()
        
    def selector(self, qty, arg): #Single(s) or Multiple(m) elements
        if qty == "s":
            return self.driver.find_element_by_css_selector(arg).text
        elif qty == "m":
            return self.driver.find_elements_by_css_selector(arg)
        
    def extract(self):
        time.sleep(5)
        selector = self.selector
        contract_info = selector("m", "table[id*='DetalleImputacionAdjudicacion'] td") 
        data_main = {         
            "bid_code": selector("s", "span[id*='NumeroProceso']"), 
            "name": selector("s", "span[id*='NombreProceso']"), 
            "process": selector("s", "span[id*='ProcedimientoSeleccion']"), 
            "stage": selector("s", "span[id*='Etapa']"), 
            "validity": selector("s", "span[id*='MantenimientoOferta']"), 
            "duration": selector("s", "span[id*='DuracionContrato']"), 
            "opening": selector("s", "table[id*='ActasApertura'] p"), 
            "awarded_bidder": contract_info[1].text, 
            "awarded_bidder_id": contract_info[2].text, 
            "amount": contract_info[6].text, 
            "currency": contract_info[7].text      
            } 
        products = [product.text for product in selector("m", "table[id*='gvLineaPliego']  span[id*='lblDescripcion']")]
        products_qty = [qty.text for qty in selector("m", "table[id*='gvLineaPliego']  span[id*='lblCantidad']")]
        data_products = {"bid_code": [], "product": [], "qty": []}
        for prod in range(len(products)):
            data_products["bid_code"].append(selector("s", "span[id*='NumeroProceso']"))
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

    def scrape(self):
        driver = self.driver
        if self.iteration == 0:
            if self.page_counter > 0:
                self.first_page_jump()
            if self.page_counter > 1:
                for scraped_pages in range(self.page_counter - 1):
                    self.page_jump([12, 12])
            if (self.tab_counter % 10) > 0:
                self.tab_jump(self.tab_counter)
            
        data_main = {"bid_code": [], "name": [], "process": [], "stage": [], "validity": [], "duration": [], "opening": [], "awarded_bidder": [], "awarded_bidder_id": [], "amount": [], "currency": []}
        data_products = {"bid_code": [], "product": [], "qty": []}

        for row in range(2, 12):
            row = format(row, "02d")
            self.enter_process(row)
            extracted_data = self.extract()
            self.exit_process()
            print("Row " + str(row) + " scraped")
            for keys in data_main:
                data_main[keys].append(extracted_data[0][keys])
            for keys in data_products:
                data_products[keys].append(extracted_data[1][keys])
        
        if self.tab_counter % 10 == 0 and self.tab_counter != 0:
            self.tab_counter += 1
            self.page_counter += 1
            self.page_jump([11, 12])
        else:
            self.tab_counter += 1
            self.tab_jump(self.tab_counter)
        self.iteration += 1
        return data_main, data_products
        

#COUNTERS PULL
path_counters = fr"local_repo\bids\data_files\counters.json"

if path.exists(path_counters):
    with open(path_counters) as c:
        counters_current = json.load(c)
    for counter in counters_current:
        page_counter_current, tab_counter_current = counter["page_counter"], counter["tab_counter"]
else:
    page_counter_current, tab_counter_current = 0, 0


#INSTANTIATION            
compras_ar = BidScrape("https://comprar.gob.ar/BuscarAvanzado.aspx", page_counter_current, tab_counter_current)
compras_ar.query_search()


#CSV LOAD
path_main = fr"local_repo\bids\data_files\bids_report.json"
path_products = fr"local_repo\bids\data_files\products_report.json"

for n in range(1):
    main_data, product_data = compras_ar.scrape()
    
    df_main = pd.DataFrame().append(main_data, ignore_index=True)
    df_products = pd.DataFrame().append(product_data, ignore_index=True)
    
    if path.exists(path_main):
        df.to_csv(path_main, mode="a", index=False, header=False)
    else:
        df_main.to_csv(path_main, index=False)
        
    if path.exists(path_products):
        df_products.to_csv(path_products, index=False)
    else:
        df_products.to_csv(path_products, mode="a", index=False, header=False)


#JSON COUNTERS LOAD
counters = {"page_counter": compras_ar.page_counter, "tab_counter": compras_ar.tab_counter}
with open(path_counters, "w") as write_file:
    json.dump(counters, write_file, indent=4)
    

#LOG FILE
t1_stop = perf_counter() 
time_info = f"Elapsed time: {str(t1_start)}(Start), {str(t1_stop)}(Stop) \nElapsed time during the whole program in seconds: {str(t1_stop-t1_start)}"
timestamp = f"Timestamp: {datetime.now()}"
pages = f"Pages completed: {compras_ar.page_counter - page_counter_current}\nCurrent page: {compras_ar.page_counter}"
tabs = f"Tabs completed: {compras_ar.tab_counter - tab_counter_current}\nCurrent page: {compras_ar.tab_counter}"

log = time_info + "\n" + timestamp + "\n" + pages + "\n" + tabs 

if path.exists(path_products):
    with open(fr"local_repo\bids\data_files\bidslog.txt", "a+") as log_file:
        log_file.write("\n------------------------\n")
else:
    with open(fr"local_repo\bids\data_files\bidslog.txt", "w") as file:
        file.write(log)