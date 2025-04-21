from selenium import webdriver

driver = webdriver.Chrome()
driver.get("http://example.com")
print(driver.title)
driver.quit()
