import os

from PIL import Image
from Screenshot import Screenshot
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


PAGE_TIMEOUT =   5
PAGE_ZOOM    = 150


def grab_card(unit_id):
    ob = Screenshot.Screenshot()
    driver = webdriver.Chrome()
    url = f"https://hcunits.net/explore/units/{unit_id}/"
    driver.get(url)
    driver.execute_script(f"document.body.style.zoom='{PAGE_ZOOM}%'")

    try:
        print(f"Getting {unit_id}...")
        element_present = EC.presence_of_element_located((By.ID, 'unitCard0'))
        WebDriverWait(driver, PAGE_TIMEOUT).until(element_present)
    except TimeoutException:
        print("Timed out waiting for page to load")

    element = driver.find_element(By.ID, 'unitCard0')
    img_url = ob.get_element(driver, element, save_path=r'./cards/', image_name=f"{unit_id}.png")

    save_path = r'./cards/'
    image_name = f"{unit_id}.png"

    image = ob.full_screenshot(driver, save_path=save_path, image_name=image_name)
    # Need to scroll to top, to get absolute coordinates
    driver.execute_script("window.scrollTo(0, 0)")
    location = element.location
    size = element.size
    x = location['x']  * PAGE_ZOOM / 100
    y = location['y']  * PAGE_ZOOM / 100
    w = size['width']  * PAGE_ZOOM / 100
    h = size['height'] * PAGE_ZOOM / 100
    width = x + w
    height = y + h

    image_object = Image.open(image)
    image_object = image_object.crop((int(x), int(y), int(width), int(height)))
    img_url = os.path.abspath(os.path.join(save_path, image_name))
    image_object.save(img_url)
    image_object.close()

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
