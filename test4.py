from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import shutil
import time
import os
import traceback

# ============================================================
# 1. REGENERATE SCREENSHOT FOLDER
# ============================================================

SCREENSHOT_DIR = "screenshots_buttons"

# Delete old folder if it exists, then recreate a fresh one
if os.path.exists(SCREENSHOT_DIR):
    shutil.rmtree(SCREENSHOT_DIR)

os.makedirs(SCREENSHOT_DIR)


# ============================================================
# 2. DRIVER SETUP
# ============================================================

service = Service()
driver = webdriver.Chrome(service=service)
driver.maximize_window()

wait = WebDriverWait(driver, 10)
actions = ActionChains(driver)


# ============================================================
# 3. UTILITY FUNCTIONS
# ============================================================

def log(msg: str) -> None:
    """Simple logger with [BUTTONS] prefix."""
    print(f"[BUTTONS] {msg}")


def takeScreenshot(test_id: str) -> None:
    """Save a screenshot file for the given test id."""
    filename = os.path.join(SCREENSHOT_DIR, f"{test_id}.png")
    driver.save_screenshot(filename)
    log(f"Capture sauvegardée : {filename}")


def openButtonsPage() -> None:
    """
    Open the Buttons page if not already there.
    This avoids calling driver.get() three times and reduces timeout risks.
    """
    if "buttons" not in driver.current_url:
        driver.get("https://demoqa.com/buttons")
    # Make sure at least one button is present
    wait.until(EC.presence_of_element_located((By.ID, "doubleClickBtn")))


def runTest(test_id: str, func) -> None:
    """
    Execute one test function:
    - log start and end
    - in case of failure, print stacktrace and take screenshot
    """
    log(f"=== Début {test_id} ===")
    try:
        func()
        log(f"{test_id} : PASS")
    except Exception as e:
        log(f"{test_id} : FAIL -> {e}")
        traceback.print_exc()
        takeScreenshot(test_id)
    log(f"=== Fin {test_id} ===\n")


# ============================================================
# 4. TEST CASES
# ============================================================

def tc1() -> None:
    """
    TC1 : Vérifier le message après un double clic sur 'Double Click Me'.
    Étapes :
      - ouvrir la page (si nécessaire)
      - double cliquer sur le bouton
      - vérifier le message affiché
    """
    openButtonsPage()

    # Wait until the button is clickable
    double_btn = wait.until(
        EC.element_to_be_clickable((By.ID, "doubleClickBtn"))
    )

    # Perform double click using ActionChains
    actions.double_click(double_btn).perform()

    # Wait for the message to appear
    msg_element = wait.until(
        EC.visibility_of_element_located((By.ID, "doubleClickMessage"))
    )
    msg = msg_element.text

    assert "You have done a double click" in msg, (
        f"Message inattendu après double clic : '{msg}'"
    )


def tc2() -> None:
    """
    TC2 : Vérifier le message après un clic droit sur 'Right Click Me'.
    """
    openButtonsPage()

    right_btn = wait.until(
        EC.element_to_be_clickable((By.ID, "rightClickBtn"))
    )

    # Right-click (context click)
    actions.context_click(right_btn).perform()

    msg_element = wait.until(
        EC.visibility_of_element_located((By.ID, "rightClickMessage"))
    )
    msg = msg_element.text

    assert "You have done a right click" in msg, (
        f"Message inattendu après clic droit : '{msg}'"
    )


def tc3() -> None:
    """
    TC3 : Vérifier le message après un clic simple sur 'Click Me'.
    """
    openButtonsPage()

    # Locate the dynamic click button via XPATH using its visible text
    dynamic_btn = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//button[text()='Click Me']"))
    )

    dynamic_btn.click()

    msg_element = wait.until(
        EC.visibility_of_element_located((By.ID, "dynamicClickMessage"))
    )
    msg = msg_element.text

    assert "You have done a dynamic click" in msg, (
        f"Message inattendu après clic simple : '{msg}'"
    )


# ============================================================
# 5. TEST RUNNER
# ============================================================

try:
    # First call will load the page, next calls will reuse it
    runTest("TC1", tc1)
    runTest("TC2", tc2)
    runTest("TC3", tc3)
finally:
    time.sleep(1)
    driver.quit()
