from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
import re
import time



class BidScrape():

    def __init__(self, url, page_counter, tab_counter, row_counter):
        self.driver = webdriver.Chrome("\webdrivers\chromedriver.exe")
        self.driver.set_script_timeout(20)
        accept_next_alert = True
        delay = 3
        self.driver.get(url)
        self.page_counter = page_counter
        self.tab_counter = tab_counter 
    
    def query_search(self):
        driver = self.driver
        status = Select(driver.find_element_by_id("ctl00_CPH1_ddlEstadoProceso"))
        status.options[1].click()
        driver.find_element_by_id("ctl00_CPH1_btnListarPliegoAvanzado").click()
        
    def extract(self):
        driver = self.driver
        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH,  "//*[@id='ctl00_CPH1_lnkVolver']"))).click()
       
        
    def first_page_jump(self):
        time.sleep(5)
        WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.LINK_TEXT, "..."))).click()
        
    def page_jump(self, idx):
        for scraped_pages in range(self.page_counter - 1):
            time.sleep(5)
            WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.XPATH, f"//*[@id='ctl00_CPH1_GridListaPliegos']/tbody/tr[{idx[0]}]/td/table/tbody/tr/td[{idx[1]}]/a"))).click()
            
    def tab_jump(self, tab_idx):
        WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.LINK_TEXT, f"{tab_idx}"))).click()
        
    def scrape(self):
        driver = self.driver
        # self.first_page_jump()
        self.page_jump([12, 12])
        if (self.tab_counter % 10) > 0:
            self.tab_jump(self.tab_counter+1)
            
        for n in range(20):
            for row in range(2, 12):
                row = format(row, "02d")
                
                WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR,  f"#ctl00_CPH1_GridListaPliegos_ctl02_lnkNumeroProceso a"))).click()
                
                self.extract()
                self.row_counter += 1
                print("Row " + str(self.row_counter) + " scraped")
            
            if (self.tab_counter % 10) == 0:
                self.page_jump([11, 12])
                print("Page" + str(self.page_counter) + " scraped")
                self.page_counter += 1
                print("Tab " + str(self.tab_counter) + " scraped")
                self.tab_counter += 1
            else:
                self.tab_jump(self.tab_counter + 1)
                print("Tab " + str(self.tab_counter) + " scraped")
                self.tab_counter += 1
            
           
        #     self.page_counter += 1
        #     
            
        # except (TimeoutException, NoSuchElementException) as error:
        #     print("finalizing due to error...")
        #     self.driver.quit()
        #     print(self.page_counter, self.tab_counter, self.row_counter)
        #     raise
            
        # print("Scraping successful")
        # self.driver.quit()
        # print(self.page_counter, self.tab_counter, self.row_counter)
    

        
compras_ar = BidScrape("https://comprar.gob.ar/BuscarAvanzado.aspx", 0, 1, 0)
compras_ar.query_search()
compras_ar.scrape()
