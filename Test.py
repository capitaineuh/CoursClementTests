import logging
import os
import shutil
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time

# Réinitialiser le dossier "test-output"
output_dir = 'test-output'
if os.path.exists(output_dir):
    shutil.rmtree(output_dir)
os.makedirs(output_dir)

# Configurer le logging pour écraser le fichier à chaque exécution
logging.basicConfig(
    filename=os.path.join(output_dir, 'test_log.log'),
    filemode='w',  # 'w' pour écraser le fichier à chaque exécution
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
)

def take_screenshot(driver, step_name):
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    screenshot_name = os.path.join(output_dir, f"screenshot_{step_name}_{timestamp}.png")
    driver.save_screenshot(screenshot_name)
    logging.info(f"Screenshot saved as {screenshot_name}")

driver = webdriver.Edge()
driver.get("http://localhost:3000/")

try:
    time.sleep(2)
    
    input_box = driver.find_element(By.ID, "prompt")
    mode1 = driver.find_element(By.ID, "mode1")
    mode2 = driver.find_element(By.ID, "mode2")
    mode3 = driver.find_element(By.ID, "mode3")
    historique = driver.find_element(By.ID, "cookies")
    
    input_box.send_keys("Bonjour, chatbot!" + Keys.RETURN)
    time.sleep(2)
    valider = driver.find_element(By.ID, "send")
    valider.click()
    
    # Attendre que l'élément de réponse soit présent et visible
    response_element = WebDriverWait(driver, 5).until(
        EC.visibility_of_element_located((By.ID, "reponse"))
    )
    
    # Vérifier la réponse
    response = response_element.text
    if "Erreur" in response:
        logging.info("L'assertion a réussi : Le texte 'Error communicating' est présent dans le champ de réponse.")
    else:
        raise AssertionError("Erreur 500 (Serveur error) : Le texte attendu n'est pas présent.")
    
    # mode1.click()
    # response_element = WebDriverWait(driver, 5).until(
    #     EC.visibility_of_element_located((By.ID, "reponse"))
    # )
    
except TimeoutException:
    logging.error("TimeoutException: Erreur 500 (Serveur error), probleme to fetch API.")
    take_screenshot(driver, "timeout_exception")
except NoSuchElementException:
    logging.error("NoSuchElementException: L'élément spécifié n'a pas été trouvé sur la page.")
    take_screenshot(driver, "no_such_element_exception")
except AssertionError as e:
    logging.error(f"AssertionError: {e}")
    take_screenshot(driver, "assertion_error")
except Exception as e:
    logging.error(f"An unexpected error occurred: {e}")
    take_screenshot(driver, "unexpected_error")
    
finally:
    # Fermer le navigateur
    time.sleep(2)
    driver.quit()