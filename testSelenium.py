import unittest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

import time

pathIsma = '/home/isma/Isma/UNI/WEBPROGRAMMING/WebProgramming_LAB4/chromedriver'



class PythonOrgSearch(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Chrome(pathIsma)

    def testTwidder(self):
        driver = self.driver
        driver.get("http://localhost:8080")

        #sign up
        driver.find_element_by_name("name").clear()
        driver.find_element_by_name("name").send_keys("nameTestSearch")
        driver.find_element_by_name("f-name").clear()
        driver.find_element_by_name("f-name").send_keys("f-nameTestSearch")
        driver.find_element_by_name("city").clear()
        driver.find_element_by_name("city").send_keys("citiTestSearch")
        driver.find_element_by_name("country").clear()
        driver.find_element_by_name("country").send_keys("countryTest")
        driver.find_element_by_name("semail").clear()
        driver.find_element_by_name("semail").send_keys("testSearch@mail.com")
        driver.find_element_by_name("spassword").clear()
        driver.find_element_by_name("spassword").send_keys("testpw")
        driver.find_element_by_name("Rspassword").clear()
        driver.find_element_by_name("Rspassword").send_keys("testpw")
        driver.find_element_by_xpath("//input[@value='Sign Up']").click()


        if "User successfully created" in driver.find_element_by_id("messageSignUpSucc").get_attribute("innerHTML"):
            print "user created"
        if "Email already exists" in driver.find_element_by_id("messageSignUpErr").get_attribute("innerHTML"):
            print "email already exists"

        #sign in
        time.sleep(3)
        driver.find_element_by_name("lemail").clear()
        driver.find_element_by_name("lemail").send_keys("testSearch@mail.com")
        driver.find_element_by_name("lpassword").clear()
        driver.find_element_by_name("lpassword").send_keys("testpw")
        driver.find_element_by_xpath("//input[@value='Login']").click()

        #send message
        time.sleep(5)
        driver.find_element_by_name("message").send_keys("This is a test message")
        driver.find_element_by_xpath("//input[@value='Send message']").click()

        #find user
        time.sleep(3)
        driver.find_element_by_id("navBrowse").click()

        driver.find_element_by_name("email").clear()
        driver.find_element_by_name("email").send_keys("testSearch@mail.com")
        driver.find_element_by_xpath("//input[@value='Search User']").click()

        #change password
        time.sleep(3)
        driver.find_element_by_id("navAccount").click()

        driver.find_element_by_name("current_password").clear()
        driver.find_element_by_name("current_password").send_keys("testpw")
        driver.find_element_by_name("new_password").clear()
        driver.find_element_by_name("new_password").send_keys("testpw")
        driver.find_element_by_name("rnew_password").clear()
        driver.find_element_by_name("rnew_password").send_keys("testpw")
        driver.find_element_by_xpath("//input[@value='Change Password']").click()
        if "Password changed" in driver.find_element_by_id("messageChPasswordS").get_attribute("innerHTML"):
            print "password changed"

        if "The token is not correct" in driver.find_element_by_id("messageChPassword").get_attribute("innerHTML"):
            print "The token is not correct"

        if "The password is not correct" in driver.find_element_by_id("messageChPassword").get_attribute("innerHTML"):
            print "The password is not correct"


        time.sleep(4)

def tearDown(self):
        self.driver.close()

if __name__ == "__main__":
    unittest.main()
