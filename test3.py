from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException
import shutil
import os
import time
import requests

# --------------------------------------
# Prepare screenshot folder
# --------------------------------------
SCREENSHOT_DIR = "screenshots_broken"

if os.path.exists(SCREENSHOT_DIR):
    shutil.rmtree(SCREENSHOT_DIR)
os.makedirs(SCREENSHOT_DIR)

# --------------------------------------
# WebDriver setup
# --------------------------------------
service = Service()
driver = webdriver.Chrome(service=service)
driver.maximize_window()
wait = WebDriverWait(driver, 10)

# --------------------------------------
# Simple helpers
# --------------------------------------
def screenshot(name):
    driver.save_screenshot(os.path.join(SCREENSHOT_DIR, f"{name}.png"))

def openPage():
    driver.get("https://demoqa.com/broken")

def run(name, func):
    try:
        func()
        print(f"{name} : PASS")
    except Exception as e:
        print(f"{name} : FAIL")
        screenshot(name)
    print("")

# --------------------------------------
# TC1 - Valid Link
# --------------------------------------
def tc1():
    openPage()
    link = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href='http://demoqa.com']"))
    )

    # Try to click normally, fallback to JS
    try:
        link.click()
    except:
        driver.execute_script("arguments[0].click();", link)

    time.sleep(1)

    # Check HTTP status
    status = requests.get(driver.current_url).status_code
    assert status == 200

# --------------------------------------
# TC2 - Broken Link
# --------------------------------------
def tc2():
    openPage()
    broken = wait.until(
        EC.element_to_be_clickable((By.LINK_TEXT, "Click Here for Broken Link"))
    )

    try:
        broken.click()
    except:
        driver.execute_script("arguments[0].click();", broken)

    time.sleep(1)

    # Status must be 200 → If not, FAIL
    status = requests.get(driver.current_url).status_code
    assert status == 200  # will FAIL (status 500) and take screenshot

# --------------------------------------
# Run tests
# --------------------------------------
try:
    run("TC1_VALID_LINK", tc1)
    run("TC2_BROKEN_LINK", tc2)
finally:
    driver.quit()
