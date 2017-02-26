import unittest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

import time

pathIsma = '/home/isma/Isma/UNI/WEBPROGRAMMING/WebProgramming_LAB4/chromedriver'



class PythonOrgSearch(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Chrome(pathIsma)

    def test(self):
        driver = self.driver
        driver.get("http://localhost:8080")

        driver.find_element_by_name("name").clear()
        driver.find_element_by_name("name").send_keys("nameTest")
        driver.find_element_by_name("f-name").clear()
        driver.find_element_by_name("f-name").send_keys("f-nameTest")
        driver.find_element_by_name("city").clear()
        driver.find_element_by_name("city").send_keys("citiTest")
        driver.find_element_by_name("country").clear()
        driver.find_element_by_name("country").send_keys("countryTest")
        driver.find_element_by_name("email").clear()
        driver.find_element_by_name("email").send_keys("test@mail.com")
        driver.find_element_by_name("email").send_keys("test@mail.com")
        driver.find_element_by_name("password").clear()
        driver.find_element_by_name("password").send_keys("testpw")
        driver.find_element_by_name("password").send_keys("testpw")
        driver.find_element_by_name("Rpassword").clear()
        driver.find_element_by_name("Rpassword").send_keys("testpw")
        driver.find_element_by_xpath("//input[@value='Sign Up']").click()

        #time.sleep(5)
        #driver.find_element_by_name("email").clear()
        #driver.find_element_by_name("email").send_keys("test@mail.com")
        #driver.find_element_by_name("password").clear()
        #driver.find_element_by_name("password").send_keys("testpw")
        #driver.find_element_by_xpath("//input[@value='Login']").click()

        time.sleep(5)
        driver.find_element_by_xpath("//input[@value='browse']").click()



    def tearDown(self):
        self.driver.close()

if __name__ == "__main__":
    unittest.main()
