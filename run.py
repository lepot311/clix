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
PATH_CARDS   = './cards/'

def grab_div_by_id(div_id):
    image_name = f"{unit_id}_{div_id}.png"

    el = driver.find_element(By.ID, div_id)

    # take full screenshot
    image = ob.full_screenshot(driver, save_path=PATH_CARDS, image_name=image_name)

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
    image_object = Image.open(image)
    image_object = image_object.crop((x1, y1, x2, y2))

    path_cropped = os.path.abspath(os.path.join(PATH_CARDS, image_name))
    image_object.save(path_cropped)
    image_object.close()

    print(f"Saved {unit_id} (div={div_id}) to {path_cropped}")
    return path_cropped


def grab_card(ob, driver, unit_id):
    url = f"https://hcunits.net/explore/units/{unit_id}/"
    driver.get(url)
    driver.execute_script(f"document.body.style.zoom='{PAGE_ZOOM}%'")

    try:
        print(f"Getting {unit_id}...")
        # wait for front of card to load
        element_present = EC.presence_of_element_located((By.ID, 'unitCard0'))
        WebDriverWait(driver, PAGE_TIMEOUT).until(element_present)
    except TimeoutException:
        print("Timed out waiting for page to load")

    path_front = grab_div_by_id('unitCard0')

    try:
        path_back = grab_div_by_id('unitCard1')
    except NoSuchElementException:
        path_back = False

    if path_back:
        # merge images
        image_front = Image.open(path_front)
        image_back  = Image.open(path_back)

        width  = image_front.width + image_back.width
        height = image_front.height

        merged = Image.new('RGBA', (width, height))
        merged.paste(image_front, (0, 0))
        merged.paste(image_back,  (image_front.width, 0))

        path_merged = f"./cards/{unit_id}.png"
        merged.save(path_merged)

        print(f"Saved merged image to {path_merged}")

        image_front.close()
        image_back.close()
        merged.close()

        # clean up tmp images
        os.remove(path_front)
        os.remove(path_back)
    else:
        os.rename(path_front, f"{path_front.rsplit('_')[0]}.png")

if __name__ == '__main__':
    unit_ids = [
        'ffxdps002',
        'wkd24DC24-002',
        'affe061',
    ]

    ob = Screenshot.Screenshot()
    driver = webdriver.Chrome()

    for unit_id in unit_ids:
        grab_card(ob, driver, unit_id)

    driver.close()
    driver.quit()

