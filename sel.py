from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import random
import time

def check_price():
    # Path to your chromedriver
    service = Service("C:\\Users\\Zohaib\\OneDrive\\Desktop\\chromedriver-win64\\chromedriver.exe")
    
    # Configure Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--remote-debugging-port=9222")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")

    # Start Chrome WebDriver
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        print("Navigating to the Walmart product page...")
        driver.get("https://www.walmart.ca/en/ip/6000206890893")
        
        # Simulate mouse movement
        actions = ActionChains(driver)
        actions.move_by_offset(random.randint(0, 100), random.randint(0, 100)).perform()
        time.sleep(random.uniform(0.25, 1))
        
        # Wait for the price element to load using its full XPath
        print("Waiting for the price element to load...")
        wait = WebDriverWait(driver, 20)  # Increased timeout to 20 seconds
        price_element = wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div[1]/div/div[2]/div[1]/section/main/div[2]/div[2]/div/div[1]/div/div/div[2]/div/div/div[2]/div/div/div[1]/span[1]/span[2]/span")))
        price = price_element.text if price_element else "Price not found"
        
        # Simulate mouse movement again
        actions.move_by_offset(random.randint(0, 50), random.randint(0, 50)).perform()
        time.sleep(random.uniform(0.25, 1))
        
        # Check stock status
        print("Checking stock status...")
        try:
            stock_element = driver.find_element(By.CSS_SELECTOR, "button[data-automation-id='atc']")
            in_stock = "In Stock"
        except:
            in_stock = "Out of Stock"
        
        print(price)
    except Exception as e:
        print(f"An error occurred: {e}")
        print("Page source for debugging (headless mode):")
        print(driver.page_source)  # Dump page source for debugging
    finally:
        driver.quit()

check_price()
