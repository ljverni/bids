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

        self.page_counter = page_counter
        self.tab_counter = tab_counter
        self.row_counter = 0
        self.iteration = 0
    
    def query_search(self):
        driver = self.driver
        status = Select(driver.find_element_by_id("ctl00_CPH1_ddlEstadoProceso"))
        status.options[1].click()
        driver.find_element_by_id("ctl00_CPH1_btnListarPliegoAvanzado").click()
        
    def selector(self, qty, arg): #SINGLE(s)/MULTIPLE(m) ELEMENTS
        if qty == "s":
            return self.driver.find_element_by_css_selector(arg).text
        elif qty == "m":
            return self.driver.find_elements_by_css_selector(arg)
        
    def extract(self):
        time.sleep(5)
        selector = self.selector
        
        #MAIN DICT
        data_main = {         
            "code": selector("s", "span[id*='NumeroProceso']"), 
            "name": selector("s", "span[id*='NombreProceso']"), 
            "process": selector("s", "span[id*='ProcedimientoSeleccion']"), 
            "stage": selector("s", "span[id*='Etapa']"), 
            "validity": selector("s", "span[id*='MantenimientoOferta']"), 
            "duration": selector("s", "span[id*='DuracionContrato']"), 
            "opening": selector("s", "table[id*='ActasApertura'] p"),     
            } 
        
        #PROVIDERS DICT
        data_providers = {"bid_code": [], "name": [], "tin": [], "po_number": [], "po_amount": [], "currency": []}
        for provider_rows in selector("m", "table[id*='DetalleImputacionAdjudicacion'] tr")[1:]:
            row = provider_rows.find_elements_by_tag_name("td")
            data_providers["bid_code"].append(selector("s", "span[id*='NumeroProceso']"))
            data_providers["name"].append(row[1].text)
            data_providers["tin"].append(row[2].text)
            data_providers["po_number"].append(row[0].text)
            data_providers["po_amount"].append(row[6].text)
            data_providers["currency"].append(row[7].text)
        
        #PRODUCTS DICT
        data_products = {"bid_code": [], "description": [], "qty": []}
        for product_rows in selector("m", "table[id*='DetalleProductos_gvLineaPliego'] tr")[1:]:
            row = product_rows.find_elements_by_tag_name("td")  
            data_products["bid_code"].append(selector("s", "span[id*='NumeroProceso']"))
            data_products["description"].append(row[3].text)
            data_products["qty"].append(row[4].text)
    
        return data_main, data_providers, data_products
            
    def exit_process(self):
        self.driver.execute_script("arguments[0].click();", WebDriverWait(self.driver, 30).until(EC.element_to_be_clickable((By.XPATH,  f"//*[@id='ctl00_CPH1_lnkVolver']"))))
                   
    def tab_jump(self):
        self.driver.execute_script("arguments[0].click();", WebDriverWait(self.driver, 30).until(EC.element_to_be_clickable((By.CSS_SELECTOR, f"a[href*='Page${self.tab_counter}']"))))
        
    def page_jump(self):
        for i in range(1, self.page_counter + 1):
            last_tab = f"{i}{1}"
            self.driver.execute_script("arguments[0].click();", WebDriverWait(self.driver, 30).until(EC.element_to_be_clickable((By.CSS_SELECTOR, f"a[href*='Page${last_tab}']"))))
         
    def enter_process(self, row):
        time.sleep(5)
        self.driver.execute_script("arguments[0].click();", WebDriverWait(self.driver, 30).until(EC.element_to_be_clickable((By.XPATH,  f"//*[@id='ctl00_CPH1_GridListaPliegos_ctl{row}_lnkNumeroProceso']"))))

    def scrape(self):
        driver = self.driver
        if self.iteration == 0:
            self.page_jump()
        if (self.tab_counter % 10) != 1:
            self.tab_jump()
        data_main = {"code": [], "name": [], "process": [], "stage": [], "validity": [], "duration": [], "opening": []}
        data_providers = {"bid_code": [], "name": [], "tin": [], "po_number": [], "po_amount": [], "currency": []}
        data_products = {"bid_code": [], "description": [], "qty": []}
      
        for row in range(1, 11):
            f_row = format(row+1, "02d")
            self.enter_process(f_row)
            self.exit_process()
            print("Row " + str(row) + " scraped")
            self.row_counter += 1
        
        self.tab_counter += 1
        if (self.tab_counter % 10) == 1:
            self.page_counter += 1
        self.tab_jump()
        self.iteration += 1

        return data_main, data_providers, data_products
        
###############
#COUNTERS PULL#
###############
path_counters = fr"local_repo\bids\counters.json"

with open(path_counters) as c:
    counters_current = json.load(c)
    current_page, current_tab = counters_current["page_counter"], counters_current["tab_counter"]

###############
#INSTANTIATION#
###############           
compras_ar = BidScrape("https://comprar.gob.ar/BuscarAvanzado.aspx", current_page, current_tab)
compras_ar.query_search()

##########
#CSV LOAD#
##########
path_main = fr"local_repo\bids\report_bids.csv"
path_providers = fr"local_repo\bids\report_providers.csv"
path_products = fr"local_repo\bids\report_products.csv"

for n in range(5):
    counters = {"page_counter": compras_ar.page_counter, "tab_counter": compras_ar.tab_counter}
    with open(path_counters, "w") as write_file:
        json.dump(counters, write_file, indent=4)
    
    print("TAB N°" + str(compras_ar.tab_counter))
    data_main, data_providers, data_products = compras_ar.scrape()
    
    df_main = pd.DataFrame(data_main)
    df_providers = pd.DataFrame(data_providers)
    df_products = pd.DataFrame(data_products)
    
    # df_main.to_csv(path_main, mode="a", index=False, header=False)
    # df_providers.to_csv(path_providers, mode="a", index=False, header=False)
    # df_products.to_csv(path_products, mode="a", index=False, header=False)

compras_ar.driver.quit()

##########
#LOG FILE#
##########
t1_stop = perf_counter() 
time_info = f"Elapsed time: {str(t1_start)}(Start), {str(t1_stop)}(Stop) \nElapsed time during the whole program in seconds: {str(t1_stop-t1_start)}"
timestamp = f"Timestamp: {datetime.now()}"
pages = f"Pages completed: {compras_ar.page_counter - page_counter_current - 1}\nCurrent page: {compras_ar.page_counter}"
tabs = f"Tabs completed: {compras_ar.tab_counter - tab_counter_current - 1}\nCurrent tab: {compras_ar.tab_counter}"
rows = f"Rows completed: {compras_ar.row_counter}"

log = time_info + "\n" + timestamp + "\n" + pages + "\n" + tabs + "\n" + rows + "\n" + "\n------------------------\n"
print(log)
