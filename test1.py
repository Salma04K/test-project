from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait          # Attentes explicites
from selenium.webdriver.support import expected_conditions as EC  # Expected Conditions
import time
import os
import shutil      # pour supprimer le dossier de screenshots
import traceback

# ==========================
# 1) CONFIGURATION GÉNÉRALE
# ==========================

# Nom du dossier où on va sauvegarder les captures en cas d'échec
SCREENSHOT_DIR = "screenshots_test1"

# On supprime l'ancien dossier de captures s'il existe,
# puis on le recrée pour avoir un dossier "propre" à chaque exécution.
if os.path.exists(SCREENSHOT_DIR):
    shutil.rmtree(SCREENSHOT_DIR)   # supprime le dossier + tout son contenu
os.makedirs(SCREENSHOT_DIR)         # recrée un dossier vide

# Création du service et du driver Chrome (comme dans les slides "Selenium : Usage Simple")
service = Service()
driver = webdriver.Chrome(service=service)
driver.maximize_window()

# WebDriverWait pour faire des "attentes explicites"
wait = WebDriverWait(driver, 10)    # attend max 10 secondes pour que l'élément apparaisse


# ==========================
# 2) FONCTIONS UTILITAIRES
# ==========================

def log(msg: str) -> None:
    """Petit logger pour afficher un préfixe dans la console."""
    print(f"[WEBTABLES] {msg}")


def takeScreenshot(test_id: str) -> None:
    """
    Sauvegarde une capture d'écran dans le dossier SCREENSHOT_DIR
    sous le nom <test_id>.png
    """
    filename = os.path.join(SCREENSHOT_DIR, f"{test_id}.png")
    driver.save_screenshot(filename)
    log(f"Capture d'écran sauvegardée : {filename}")


def openWebTablesPage() -> None:
    """
    Ouvre la page Web Tables et attend que le tableau soit présent.
    Utilise WebDriverWait + expected_conditions (comme dans les slides « Waits »).
    """
    driver.get("https://demoqa.com/webtables")
    # On attend que le tableau soit chargé dans le DOM
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "rt-table")))


def runTest(test_id: str, func) -> None:
    """
    Exécute une fonction de test dans un try/except :
      - log le début et la fin
      - en cas d'exception : affiche la stacktrace et prend une capture d'écran
    """
    log(f"=== Début {test_id} ===")
    try:
        func()
        log(f"{test_id} : PASS ")
    except Exception as e:
        log(f"{test_id} : FAIL  -> {e}")
        traceback.print_exc()
        takeScreenshot(test_id)
    log(f"=== Fin {test_id} ===\n")


# ==========================
# 3) CAS DE TEST WEB TABLES
# ==========================

# ---------- TC1 ----------
def tc1() -> None:
    """
    TC1 : Ajouter un nouvel enregistrement
    Étapes :
      - ouvrir la page
      - cliquer sur "Add"
      - remplir le formulaire
      - vérifier que l'email apparaît dans le tableau
    """
    openWebTablesPage()

    # On attend que le bouton "Add" soit cliquable puis on clique
    add_btn = wait.until(
        EC.element_to_be_clickable((By.ID, "addNewRecordButton"))
    )
    add_btn.click()

    # Attente que le formulaire soit visible
    wait.until(EC.visibility_of_element_located((By.ID, "firstName")))

    # Remplissage du formulaire (localisation par ID comme dans les slides)
    driver.find_element(By.ID, "firstName").send_keys("salma")
    driver.find_element(By.ID, "lastName").send_keys("khlifi")
    driver.find_element(By.ID, "userEmail").send_keys("salma@example.com")
    driver.find_element(By.ID, "age").send_keys("21")
    driver.find_element(By.ID, "salary").send_keys("10000")
    driver.find_element(By.ID, "department").send_keys("IT")

    # Soumission du formulaire
    driver.find_element(By.ID, "submit").click()

    # Vérification : on relit le texte du tableau
    table_text = driver.find_element(By.CLASS_NAME, "rt-table").text
    assert "salma@example.com" in table_text, "L'enregistrement n'a pas été ajouté au tableau"


# ---------- TC2 ----------
def tc2() -> None:
    """
    TC2 : Modifier un enregistrement existant
    Pré-condition : TC1 exécuté avec succès (salma@example.com présent)
    """
    # Vérification de la pré-condition
    table = driver.find_element(By.CLASS_NAME, "rt-table")
    assert "salma@example.com" in table.text, "Pré-condition non satisfaite : salma@example.com n'existe pas"

    # Récupère tous les boutons Edit via un sélecteur CSS (slides DOM + CSS Selector)
    edit_buttons = driver.find_elements(By.CSS_SELECTOR, "span[title='Edit']")
    assert len(edit_buttons) > 0, "Aucun bouton Edit trouvé"

    # On clique sur le dernier bouton Edit (notre enregistrement ajouté)
    edit_buttons[-1].click()

    # Attente que le champ firstName soit visible
    first_name_field = wait.until(
        EC.visibility_of_element_located((By.ID, "firstName"))
    )

    # On efface puis on remplace par "sisi"
    first_name_field.clear()
    first_name_field.send_keys("sisi")

    # Soumission
    driver.find_element(By.ID, "submit").click()

    # Vérification
    table_text = driver.find_element(By.CLASS_NAME, "rt-table").text
    assert "sisi" in table_text, "Le nouveau First Name 'sisi' n'apparaît pas dans le tableau"


# ---------- TC3 ----------
def tc3() -> None:
    """
    TC3 : Supprimer un enregistrement
    Pré-condition : un enregistrement avec 'sisi' existe dans le tableau
    """
    table_text = driver.find_element(By.CLASS_NAME, "rt-table").text
    assert "sisi" in table_text, "Pré-condition non satisfaite : 'sisi' n'existe pas"

    # Tous les boutons Delete via un sélecteur CSS (span[title='Delete'])
    delete_buttons = driver.find_elements(By.CSS_SELECTOR, "span[title='Delete']")
    assert len(delete_buttons) > 0, "Aucun bouton Delete trouvé"

    # On supprime la dernière occurrence (notre ligne 'sisi')
    delete_buttons[-1].click()

    # Vérification : le texte "sisi" ne doit plus apparaître
    table_text_after = driver.find_element(By.CLASS_NAME, "rt-table").text
    assert "sisi" not in table_text_after, "L'enregistrement 'sisi' n'a pas été supprimé"


# ---------- TC4 ----------
def tc4() -> None:
    """
    TC4 : Rechercher un enregistrement par mot-clé
    Étapes :
      - ouvrir la page
      - ajouter une ligne 'sisi'
      - utiliser la barre de recherche
      - vérifier que le tableau affiche 'sisi'
    """
    openWebTablesPage()

    # Ajouter un nouvel enregistrement "sisi"
    wait.until(EC.element_to_be_clickable((By.ID, "addNewRecordButton"))).click()
    wait.until(EC.visibility_of_element_located((By.ID, "firstName")))

    driver.find_element(By.ID, "firstName").send_keys("sisi")
    driver.find_element(By.ID, "lastName").send_keys("khlifi")
    driver.find_element(By.ID, "userEmail").send_keys("sisi@example.com")
    driver.find_element(By.ID, "age").send_keys("22")
    driver.find_element(By.ID, "salary").send_keys("9000")
    driver.find_element(By.ID, "department").send_keys("IT")
    driver.find_element(By.ID, "submit").click()

    # Utilisation de la barre de recherche (champ #searchBox)
    search_box = wait.until(
        EC.visibility_of_element_located((By.ID, "searchBox"))
    )
    search_box.clear()
    search_box.send_keys("sisi")

    # (Optionnel) petit sleep pour laisser le filtre s'appliquer visuellement
    time.sleep(1)

    # Vérification : le tableau filtré doit contenir "sisi"
    table_text = driver.find_element(By.CLASS_NAME, "rt-table").text
    assert "sisi" in table_text, "Aucun résultat contenant 'sisi' après recherche"


# ==========================
# 4) LANCEMENT DES TESTS
# ==========================

try:
    runTest("TC1", tc1)
    runTest("TC2", tc2)
    runTest("TC3", tc3)
    runTest("TC4", tc4)
finally:
    # On attend un peu pour voir le résultat puis on ferme le navigateur
    time.sleep(2)
    driver.quit()
