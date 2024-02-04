import os

from PIL import Image
from Screenshot import Screenshot
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


PAGE_TIMEOUT =   5
PAGE_ZOOM    = 125
OUTPUT_DIR   = './cards'

def grab_div_by_id(div_id, hide_elements=None):
    image_name = f"{unit_id}_{div_id}.png"

    el = driver.find_element(By.ID, div_id)

    # take full screenshot
    path_full = ob.full_screenshot(driver, save_path=OUTPUT_DIR, image_name=image_name, hide_elements=hide_elements or [])

    # Need to scroll to top, to get absolute coordinates
    driver.execute_script("window.scrollTo(0, 0)")

    # adjust coords for zoom
    x1 = int(el.location['x']  * PAGE_ZOOM / 100)
    y1 = int(el.location['y']  * PAGE_ZOOM / 100)
    w  = int(el.size['width']  * PAGE_ZOOM / 100)
    h  = int(el.size['height'] * PAGE_ZOOM / 100)

    x2 = x1 + w
    y2 = y1 + h

    # crop full screenshot to div (in place)
    image_object = Image.open(path_full)
    image_object = image_object.crop((x1, y1, x2, y2))

    path_cropped = os.path.abspath(os.path.join(OUTPUT_DIR, image_name))
    image_object.save(path_cropped)
    image_object.close()

    print(f"Saved {unit_id} (div={div_id}) to {path_cropped}")
    return path_cropped


def grab_card(ob, driver, unit_id):
    double = False
    path_final = f"{OUTPUT_DIR}/{unit_id}.png"

    url = f"https://hcunits.net/explore/units/{unit_id}/"
    driver.get(url)

    try:
        print(f"Getting {unit_id}...")
        # wait for front of card to load
        element_present = EC.presence_of_element_located((By.ID, 'unitCard0'))
        WebDriverWait(driver, PAGE_TIMEOUT).until(element_present)
    except TimeoutException:
        print("Timed out waiting for page to load")

    card_divs = driver.find_elements(By.CLASS_NAME, "unitCardContainer")

    for div in card_divs:
        driver.execute_script("arguments[0].setAttribute('style','margin:0; padding:0;')", div)

    path_cropped = grab_div_by_id('unitCardsContainer', hide_elements=['id=unitControlsContainer',])

    os.rename(path_cropped, path_final)
    print(f"Saved {unit_id} -> {path_final}")

if __name__ == '__main__':
    unit_ids = [
        'ffxdps002',
        'wkd24DC24-002',
        'affe061',
    ]

    ob = Screenshot.Screenshot()

    driver = webdriver.Chrome()
    driver.get('chrome://settings/')
    driver.execute_script(f"chrome.settingsPrivate.setDefaultZoom({PAGE_ZOOM / 100});")

    for unit_id in unit_ids:
        grab_card(ob, driver, unit_id)

    driver.close()
    driver.quit()

