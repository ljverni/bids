from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import NoSuchElementException
import re
import time
from datetime import datetime
from datetime import date
from time import perf_counter
import pandas as pd
from os import path
import json

class BidScrape():

    def __init__(self, url):
        self.driver = webdriver.Chrome("\webdrivers\chromedriver.exe")
        self.driver.set_script_timeout(20)
        accept_next_alert = True
        delay = 3
        self.driver.get(url)
        self.row_counter = 0
        self.iteration = 0
    
    def log_file(self, t1_start, t1_stop, message, rows, error, page, tab):
        time_info = f"Elapsed time: {str(t1_start)}(Start), {str(t1_stop)}(Stop) \nElapsed time during the whole program in seconds: {str(t1_stop-t1_start)}"
        timestamp = f"Timestamp: {datetime.now()}"
        pages = f"Parsed pages: {page}"
        tabs = f"Current tab: {tab}"
        log = str(error) + "\n" + message + "\n" + str(rows) + "\n"+ time_info + "\n" + timestamp + "\n" + pages + "\n" + tabs + "\n" + "\n------------------------\n"
        print(log)
        with open(fr"local_repo\bids\bidslog.txt", "a+") as file:
            file.write(log)  
            
    def file_save(self, data_main, data_providers, data_products):
        path_main = fr"local_repo\bids\report_bids.csv"
        path_providers = fr"local_repo\bids\report_providers.csv"
        path_products = fr"local_repo\bids\report_products.csv"
        df_main = pd.DataFrame(data_main)
        df_providers = pd.DataFrame(data_providers)
        df_products = pd.DataFrame(data_products)
        
        df_main.to_csv(path_main, mode="a", index=False, header=False)
        df_providers.to_csv(path_providers, mode="a", index=False, header=False)
        df_products.to_csv(path_products, mode="a", index=False, header=False)
        
    def counters_save(self, page, tab):
        counters = {"page_counter": page, "tab_counter": tab} 
        with open(fr"local_repo\bids\counters.json", "w") as write_file:
            json.dump(counters, write_file, indent=4)  
            
    def counters_load(self):
        with open(fr"local_repo\bids\counters.json") as c:
            counters_current = json.load(c)
            current_page, current_tab = counters_current["page_counter"], counters_current["tab_counter"]
            return current_page, current_tab
        
    def query_search(self):
        driver = self.driver
        status = Select(driver.find_element_by_id("ctl00_CPH1_ddlEstadoProceso"))
        date_range = driver.find_elements_by_class_name("dxeEditArea")
        from_date, to_date = date_range[0], date_range[1]
        from_date.send_keys("01/06/2017")
        to_date.send_keys("01/01/2018")
        status.options[1].click()
        time.sleep(5)
        self.driver.execute_script("arguments[0].click();", WebDriverWait(self.driver, 30).until(EC.element_to_be_clickable((By.XPATH, "//*[@id='ctl00_CPH1_btnListarPliegoAvanzado']"))))
        WebDriverWait(self.driver, 200).until(EC.element_to_be_clickable((By.XPATH,  f"//*[@id='ctl00_CPH1_GridListaPliegos_ctl02_lnkNumeroProceso']")))
        
    def selector(self, qty, arg): #SINGLE(s)/MULTIPLE(m) ELEMENTS
        if qty == "s":
            return self.driver.find_element_by_css_selector(arg).text
        elif qty == "m":
            return self.driver.find_elements_by_css_selector(arg)
        
    def extract_process(self):
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
                   
    def tab_jump(self, tab):
        self.driver.execute_script("arguments[0].click();", WebDriverWait(self.driver, 30).until(EC.element_to_be_clickable((By.CSS_SELECTOR, f"a[href*='Page${tab}']"))))
        
    def page_jump(self, page):
        for i in range(1, page + 1):
            last_tab = f"{i}{1}"
            self.driver.execute_script("arguments[0].click();", WebDriverWait(self.driver, 30).until(EC.element_to_be_clickable((By.CSS_SELECTOR, f"a[href*='Page${last_tab}']"))))
         
    def enter_process(self, row):
        time.sleep(5)
        self.driver.execute_script("arguments[0].click();", WebDriverWait(self.driver, 30).until(EC.element_to_be_clickable((By.XPATH,  f"//*[@id='ctl00_CPH1_GridListaPliegos_ctl{row}_lnkNumeroProceso']"))))
        
    def first_jump(self, tab):
        driver = self.driver
        if self.iteration == 0:
            self.page_jump(page)
            if (tab % 10) != 1:
                self.tab_jump(tab)
        elif self.iteration > 0:
            self.tab_jump(tab)
        

    def scrape(self, tab, page):
        self.first_jump(tab)
        data_main = {"code": [], "name": [], "process": [], "stage": [], "validity": [], "duration": [], "opening": []}
        data_providers = {"bid_code": [], "name": [], "tin": [], "po_number": [], "po_amount": [], "currency": []}
        data_products = {"bid_code": [], "description": [], "qty": []}
      
        for row in range(1, 11):
            f_row = format(row+1, "02d")
            try:
                self.enter_process(f_row)
                extracted_data = self.extract_process()
                self.exit_process()
                print("Row " + str(row) + " scraped")
                self.row_counter += 1
                
                for keys in extracted_data[0]: #MAIN DICT
                    data_main[keys].append(extracted_data[0][keys])
                for key in extracted_data[1]: #PROVIDERS DICT
                    for value in extracted_data[1][key]:
                        data_providers[key].append(value)     
                for key in extracted_data[2]: #PRODUCTS DICT
                    for value in extracted_data[2][key]:
                        data_products[key].append(value)
            except (NoSuchElementException, TimeoutException) as error:
                try:
                    print(f"Unable to extract row {str(row)} data due to the following error: \n{error}")
                    self.exit_process()
                    self.row_counter += 1
                    continue
                except (NoSuchElementException, TimeoutException) as error:
                    raise error
            
        self.iteration += 1
        return data_main, data_providers, data_products
    
    def execute(self, tabs_to_do, page, tab):
        tab = tab
        for n in range(tabs_to_do):
            try:
                print("CURRENT TAB: " + str(tab))
                data_main, data_providers, data_products = self.scrape(tab, page)
                self.file_save(data_main, data_providers, data_products)
                tab += 1
                self.counters_save(int((tab - (tab % 10))/10), tab)
            except (NoSuchElementException, TimeoutException) as error:
                tab += 1
                self.counters_save(int((tab - (tab % 10))/10), tab)
                print("Jumping to next tab due to broken row")
                raise error

#####
#EXE#
##### 

try:
    t1_start = perf_counter()         
    compras_ar = BidScrape("https://comprar.gob.ar/BuscarAvanzado.aspx")
    compras_ar.query_search()
    page, tab = compras_ar.counters_load()
    compras_ar.execute(234, page, tab)
    t1_stop = perf_counter()
    page, tab = compras_ar.counters_load()
    compras_ar.log_file(t1_start, t1_stop, "Extraction process Successful, parsed rows: ", compras_ar.row_counter, "No Error", page, tab)
    
except (TimeoutException, NoSuchElementException, WebDriverException) as error:
    print(error)
    t1_stop = perf_counter() 
    page, tab = compras_ar.counters_load()
    compras_ar.log_file(t1_start, t1_stop, "Extraction process partially Successful, parsed rows: ", compras_ar.row_counter, error, page, tab)
    t1_start = perf_counter()         
    compras_ar = BidScrape("https://comprar.gob.ar/BuscarAvanzado.aspx")
    compras_ar.query_search()
    page, tab = compras_ar.counters_load()
    compras_ar.execute(100, page, tab)

finally:
    compras_ar.driver.quit()



####DATE SPANS AND ROWS
"""
19/08/2016 - 01/06/2017 751 - DONE
01/06/2017 - 01/01/2018 2342 
01/01/2018 - 01/06/2018 1789
01/06/2018 - 01/09/2018 1730
01/09/2018 - 01/01/2019 3335
01/01/2019 - 01/04/2019 1511
01/04/2019 - 01/07/2019 2729
01/07/2019 - 01/10/2019 3303
01/10/2019 - 01/01/2020 2457
01/01/2020 - 04/06/2020 1504
"""
