'''
ClixGrabber

Usage:
  clixgrabber.py [-m] [--cpus=<n>] cards <unit_ids>...
  clixgrabber.py [-m] [--cpus=<n>] sets <set_ids>...

Options:
  -h          Show this help text
  -m          Use multiprocessing
  --cpus=<n>  Number of CPUs to use for multiprocessing
  --zoom=<z>  Page zoom [default: 125]
'''
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


    def grab_card(self, unit_id, set_id=None):
        if set_id:
            path_final = f"{self.output_dir}/{set_id}/{unit_id}.png"
            try:
                os.mkdir(f"{self.output_dir}/{set_id}")
            except FileExistsError:
                pass
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
    import sys

    from docopt import docopt
    import requests

    api = "https://hcunits.net/api/v1"

    def grab(targets):

        with CardGrabber() as grabber:
            for set_id, unit_id in targets:
                print(f"Grabbing {set_id} : {unit_id}")
                grabber.grab_card(unit_id, set_id=set_id)

    def grab_mp(targets):
        targets = [targets]

        with CardGrabber() as grabber:
            for set_id, unit_id in targets:
                print(f"Grabbing {set_id} : {unit_id}")
                grabber.grab_card(unit_id, set_id=set_id)


    args = docopt(__doc__)

    unit_ids = args.get('<unit_ids>')
    set_ids  = args.get('<set_ids>')

    errors = []
    set_id__unit_id = []

    if unit_ids:
        for unit_id in unit_ids:
            # get set name
            url = f"{api}/units/{unit_id}/"
            response = requests.get(url)

            if not response.ok:
                errors.append(set_id)
                continue

            set_id__unit_id.append([
                response.json()['set_id'],
                response.json()['unit_id'],
            ])

    if set_ids:
        for set_id in set_ids:
            print(f"Downloading card list for set '{set_id}'")
            url = f"{api}/sets/{set_id}/"
            response = requests.get(url)

            if not response.ok:
                errors.append(f"Could not find set {set_id} on hcunits.net")
                continue

            data = response.json()

            for unit in data['unit_list']:
                set_id__unit_id.append([
                    set_id,
                    unit['unit_id'],
                ])

    if errors:
        print("Exiting due to the following errors:")
        for e in errors:
            print(error)
        sys.exit(1)

    if args.get('-m'):
        print("Using multiprocessing.")
        from multiprocessing import Pool

        if args.get('--cpus'):
            try:
                n_cpus = int(args.get('--cpus'))
            except ValueError:
                sys.exit("ERROR: n_cpus must be an integer number.")
            pool = Pool(n_cpus)
        else:
            pool = Pool()

        with pool as p:
            print(f"  Process pool size: {p._processes}")
            p.map(grab_mp, set_id__unit_id)

    else:
        grab(set_id__unit_id)
