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
       
    def page_jump(self):
        WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//*[@id='ctl00_CPH1_GridListaPliegos']/tbody/tr[11]/td/table/tbody/tr/td[11]/a"))).click()
        for scraped_pages in range(self.page_counter - 1):
            WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//*[@id='ctl00_CPH1_GridListaPliegos']/tbody/tr[12]/td/table/tbody/tr/td[12]/a"))).click()
            
    def tab_jump(self):
        if self.tab_counter == 0:
            pass
          
    def wait(self):
        WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//*[@id='ctl00_CPH1_GridListaPliegos']/tbody/tr[11]/td/table/tbody/tr/td[12]/a")))

    def tab_lst(self):
        self.wait()
        tab_grid = self.driver.find_element_by_class_name("pagination-gv")
        return tab_grid.find_elements_by_tag_name("a")[1]
        
    def scrape(self):
        driver = self.driver
        tab_lst = self.tab_lst()
        self.page_jump()
        
        
        if (self.tab_counter % 10) > 1:
            self.tab_jump(self.tab_counter % 10)
        elif (self.tab_counter % 10) == 1:
            pass
    
        
        
                
        
        #         for row in range(2, 12):
        #             row = format(row, "02d")
        #             time.sleep(10)
        #             WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH,  f"//*[@id='ctl00_CPH1_GridListaPliegos_ctl{row}_lnkNumeroProceso']"))).click()
        #             self.extract()
        #             self.row_counter += 1
        #             print("Row " + str(self.row_counter) + " scraped")
                    
        #         self.tab_counter += 1
        #         print("Tab " + str(self.tab_counter) + " scraped")
           
        #     self.page_counter += 1
        #     print("Page" + str(self.page_counter) + " scraped")
            
        # except (TimeoutException, NoSuchElementException) as error:
        #     print("finalizing due to error...")
        #     self.driver.quit()
        #     print(self.page_counter, self.tab_counter, self.row_counter)
        #     raise
            
        # print("Scraping successful")
        # self.driver.quit()
        # print(self.page_counter, self.tab_counter, self.row_counter)
    

        
compras_ar = BidScrape("https://comprar.gob.ar/BuscarAvanzado.aspx", 1, 12, 113)
compras_ar.query_search()
compras_ar.scrape()
