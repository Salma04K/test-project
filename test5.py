from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import shutil
import time
import os
import traceback

# ============================================================
# 1. REGENERATE SCREENSHOT FOLDER
# ============================================================

SCREENSHOT_DIR = "screenshots_browserwindows"

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


# ============================================================
# 3. UTILITY FUNCTIONS
# ============================================================

def log(msg: str) -> None:
    print(f"[BROWSER-WINDOWS] {msg}")


def takeScreenshot(test_id: str) -> None:
    file = os.path.join(SCREENSHOT_DIR, f"{test_id}.png")
    driver.save_screenshot(file)
    log(f"Capture sauvegardée : {file}")


def openBrowserWindowsPage() -> None:
    """
    Load the Browser Windows page only if we are not already on it.
    Avoids reloading multiple times + reduces timeouts.
    """
    if "browser-windows" not in driver.current_url:
        driver.get("https://demoqa.com/browser-windows")

    wait.until(
        EC.presence_of_element_located((By.ID, "tabButton"))
    )


def runTest(test_id: str, func) -> None:
    """
    Execute a test case with logs, error handling and screenshot on failure.
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
    Vérifier que 'New Tab' ouvre un nouvel onglet affichant
    le texte 'This is a sample page'.
    """
    openBrowserWindowsPage()

    main_window = driver.current_window_handle

    # Click "New Tab"
    wait.until(EC.element_to_be_clickable((By.ID, "tabButton"))).click()
    time.sleep(1)

    windows = driver.window_handles
    assert len(windows) > 1, "Aucun nouvel onglet ouvert"

    # Switch to new tab
    driver.switch_to.window(windows[1])

    # Validate text
    heading = wait.until(
        EC.visibility_of_element_located((By.ID, "sampleHeading"))
    )
    assert heading.text == "This is a sample page"

    # Close new tab
    driver.close()
    driver.switch_to.window(main_window)


def tc2() -> None:
    """
    Vérifier que 'New Window' ouvre une nouvelle fenêtre
    contenant le texte 'This is a sample page'.
    """
    openBrowserWindowsPage()

    main_window = driver.current_window_handle

    # Click "New Window"
    wait.until(EC.element_to_be_clickable((By.ID, "windowButton"))).click()
    time.sleep(1)

    windows = driver.window_handles
    assert len(windows) > 1, "Aucune nouvelle fenêtre ouverte"

    driver.switch_to.window(windows[1])

    heading = wait.until(
        EC.visibility_of_element_located((By.ID, "sampleHeading"))
    )
    assert heading.text == "This is a sample page"

    driver.close()
    driver.switch_to.window(main_window)


def tc3() -> None:
    """
    Vérifier que 'New Window Message' ouvre une nouvelle fenêtre message.
    Le contenu exact n'est pas vérifié (affichage + fermeture uniquement).
    """
    openBrowserWindowsPage()

    main_window = driver.current_window_handle
    before = set(driver.window_handles)

    wait.until(
        EC.element_to_be_clickable((By.ID, "messageWindowButton"))
    ).click()

    time.sleep(1)

    after = set(driver.window_handles)
    new_windows = list(after - before)

    assert len(new_windows) == 1, "Aucune nouvelle fenêtre message ouverte"

    # Switch → small pause → close
    msg_window = new_windows[0]
    driver.switch_to.window(msg_window)
    time.sleep(0.5)

    driver.close()
    driver.switch_to.window(main_window)


# ============================================================
# 5. TEST RUNNER
# ============================================================

try:
    runTest("TC1", tc1)
    runTest("TC2", tc2)
    runTest("TC3", tc3)
finally:
    time.sleep(1)
    driver.quit()
