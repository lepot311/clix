from Screenshot import Screenshot
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


def grab_card(unit_id):
    ob = Screenshot.Screenshot()
    driver = webdriver.Chrome()
    url = f"https://hcunits.net/explore/units/{unit_id}/"
    driver.get(url)

    timeout = 5
    try:
        print(f"Getting {unit_id}...")
        element_present = EC.presence_of_element_located((By.ID, 'unitCard0'))
        WebDriverWait(driver, timeout).until(element_present)
    except TimeoutException:
        print("Timed out waiting for page to load")

    element = driver.find_element(By.ID, 'unitCard0')
    img_url = ob.get_element(driver, element, save_path=r'./cards/', image_name=f"{unit_id}.png")
    print(f"Saved {unit_id} to {img_url}")
    driver.close()
    driver.quit()

if __name__=='__main__':
    unit_ids = [
        'wkd24DC24-002',
        'affe061',
    ]

    for unit_id in unit_ids:
        grab_card(unit_id)
