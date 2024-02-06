import os

from PIL import Image
from Screenshot import Screenshot
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


class CardGrabber:
    def __init__(self, page_timeout=5, page_zoom=125, output_dir='./cards'):
        self.page_timeout = page_timeout
        self.page_zoom    = page_zoom
        self.output_dir   = output_dir
        self.tmp_dir      = './tmp'

    def __enter__(self):
        self.ob = Screenshot.Screenshot()

        self.driver = webdriver.Chrome()
        self.driver.get('chrome://settings/')
        self.driver.execute_script(f"chrome.settingsPrivate.setDefaultZoom({self.page_zoom / 100});")
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.driver.close()
        self.driver.quit()

    def grab_div_by_id(self, unit_id, div_id, hide_elements=None):
        image_name = f"{unit_id}_{div_id}.png"

        el = self.driver.find_element(By.ID, div_id)

        # take full screenshot
        path_full = None
        image_valid = False

        while (not path_full) or (not image_valid):
            try:
                path_full = self.ob.full_screenshot(
                    self.driver,
                    save_path     = self.tmp_dir,
                    image_name    = image_name,
                    hide_elements = hide_elements or [],
                )
            except Exception:
                print("Image not valid, retrying..")
            else:
                image_valid = True

        # Need to scroll to top, to get absolute coordinates
        self.driver.execute_script("window.scrollTo(0, 0)")

        # adjust coords for zoom
        x1 = int(el.location['x']  * self.page_zoom / 100)
        y1 = int(el.location['y']  * self.page_zoom / 100)
        w  = int(el.size['width']  * self.page_zoom / 100)
        h  = int(el.size['height'] * self.page_zoom / 100)

        x2 = x1 + w
        y2 = y1 + h

        # crop full screenshot to div (in place)
        image_object = Image.open(path_full)
        image_object = image_object.crop((x1, y1, x2, y2))

        path_cropped = os.path.abspath(os.path.join(self.tmp_dir, image_name))
        image_object.save(path_cropped)
        image_object.close()

        print(f"Saved {unit_id} (div={div_id}) to {path_cropped}")
        return path_cropped


    def grab_card(self, unit_id, set_name=None):
        if set_name:
            path_final = f"{self.output_dir}/{set_name}/{unit_id}.png"
        else:
            path_final = f"{self.output_dir}/{unit_id}.png"

        url = f"https://hcunits.net/explore/units/{unit_id}/"
        self.driver.get(url)

        try:
            print(f"Getting {unit_id}...")
            # wait for front of card to load
            element_present = EC.presence_of_element_located((By.ID, 'unitCard0'))
            WebDriverWait(self.driver, self.page_timeout).until(element_present)
        except TimeoutException:
            print("Timed out waiting for page to load")

        card_divs = self.driver.find_elements(By.CLASS_NAME, "unitCardContainer")

        for div in card_divs:
            self.driver.execute_script("arguments[0].setAttribute('style','margin:0; padding:0;')", div)

        path_cropped = self.grab_div_by_id(
            unit_id,
            'unitCardsContainer',
            hide_elements=[
                'id=unitControlsContainer',
                'id=hideUnitButton',
            ],
        )

        os.rename(path_cropped, path_final)
        print(f"Saved {unit_id} -> {path_final}")


if __name__ == '__main__':
    sets = [
        'm24',
    ]

    import requests

    set_name__unit_id = []

    for set_name in sets:
        url = f"https://hcunits.net/api/v1/sets/{set_name}/"
        response = requests.get(url)
        data = response.json()
        for unit in data['unit_list']:
            set_name__unit_id.append([
                set_name,
                unit['unit_id'],
            ])

    def grab(unit_ids):
        with CardGrabber() as grabber:
            unit_ids = [unit_ids]

            for set_name, unit_id in unit_ids:
                print(f"Grabbing {set_name} : {unit_id}")
                grabber.grab_card(unit_id, set_name=set_name)
                break

    from multiprocessing import Pool

    with Pool() as pool:
        print(f"Process pool size: {pool._processes}")
        pool.map(grab, set_name__unit_id)
