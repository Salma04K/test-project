from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import shutil
import time
import traceback

# ==========================
# 1) Screenshot Folder Setup
# ==========================

SCREENSHOT_DIR = "screenshots_bookstore"

# Recreate fresh folder every run
if os.path.exists(SCREENSHOT_DIR):
    shutil.rmtree(SCREENSHOT_DIR)
os.makedirs(SCREENSHOT_DIR)


# ==========================
# 2) Driver Setup
# ==========================

service = Service()
driver = webdriver.Chrome(service=service)
driver.maximize_window()

wait = WebDriverWait(driver, 10)


# ==========================
# 3) Utility Functions
# ==========================

def log(msg: str) -> None:
    print(f"[BOOKSTORE] {msg}")


def takeScreenshot(test_id: str) -> None:
    """Save screenshot to folder in case of test failure."""
    filename = os.path.join(SCREENSHOT_DIR, f"{test_id}.png")
    driver.save_screenshot(filename)
    log(f"Screenshot saved: {filename}")


def openBooksPage() -> None:
    """Open the Book Store page and wait for the table to load."""
    driver.get("https://demoqa.com/books")
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "rt-table")))


def runTest(test_id: str, func) -> None:
    """Execute test safely and handle errors + screenshots."""
    log(f"=== Start {test_id} ===")
    try:
        func()
        log(f"{test_id} : PASS")
    except Exception as e:
        log(f"{test_id} : FAIL -> {e}")
        traceback.print_exc()
        takeScreenshot(test_id)
    log(f"=== End {test_id} ===\n")


# ==========================
# 4) Test Cases
# ==========================

# TC1 – Search full title
def tc1() -> None:
    """Search for full exact title 'Speaking JavaScript'."""
    openBooksPage()

    searchBox = wait.until(
        EC.visibility_of_element_located((By.ID, "searchBox"))
    )
    searchBox.clear()
    searchBox.send_keys("Speaking JavaScript")

    wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "rt-tbody")))
    tableText = driver.find_element(By.CLASS_NAME, "rt-tbody").text

    assert "Speaking JavaScript" in tableText, "Book not displayed in results"

    # Optional: capture image source further analysis
    img = driver.find_element(By.CSS_SELECTOR, ".rt-tbody img")
    log(f"Image source for Speaking JavaScript: {img.get_attribute('src')}")


# TC2 – Partial keyword search
def tc2() -> None:
    """Search for partial keyword 'Java' and verify results exist."""
    openBooksPage()

    searchBox = wait.until(
        EC.visibility_of_element_located((By.ID, "searchBox"))
    )
    searchBox.clear()
    searchBox.send_keys("Java")

    rows = driver.find_elements(By.CSS_SELECTOR, ".rt-tbody .rt-tr-group")
    assert len(rows) > 0, "No results found for partial keyword search"


# TC3 – No result search
def tc3() -> None:
    """Search for a term that should return no results."""
    openBooksPage()

    searchBox = wait.until(
        EC.visibility_of_element_located((By.ID, "searchBox"))
    )
    searchBox.clear()
    searchBox.send_keys("xyz123")

    noData = wait.until(
        EC.visibility_of_element_located((By.CLASS_NAME, "rt-noData"))
    )
    assert "No rows found" in noData.text, "Expected message not displayed"


# TC4 – Clear search returns full list
def tc4() -> None:
    """Clear search and verify that full list reappears."""
    openBooksPage()

    searchBox = wait.until(
        EC.visibility_of_element_located((By.ID, "searchBox"))
    )
    searchBox.clear()
    searchBox.send_keys("Java")

    filtered = driver.find_elements(By.CSS_SELECTOR, ".rt-tbody .rt-tr-group")
    assert len(filtered) > 0, "Filter returned zero rows unexpectedly"

    searchBox.clear()

    time.sleep(1)  # Optional, prevents flickering on fast machines

    fullList = driver.find_elements(By.CSS_SELECTOR, ".rt-tbody .rt-tr-group")
    assert len(fullList) >= len(filtered), "Full list did not return after clearing search"


# ==========================
# 5) Test Runner
# ==========================

try:
    runTest("TC1", tc1)
    runTest("TC2", tc2)
    runTest("TC3", tc3)
    runTest("TC4", tc4)
finally:
    time.sleep(2)
    driver.quit()
