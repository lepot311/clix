Tools written to support the development of the Heroclix Project Tabletop Simulator mod.

Check out the [mod workshop page](https://steamcommunity.com/sharedfiles/filedetails/?id=2428888102).


### Installation
#### Linux
```
git clone https://github.com/lepot311/clix.git
cd clix
python -m venv env
source env/bin/activate
pip install -r requirements.txt
```
#### Windows
```
git clone https://github.com/lepot311/clix.git
cd clix
python -m venv env
.\env\Scripts\activate
pip install -r requirements.txt
```

Tools in this repo:

### ClixGrabber
Uses Selenium ChromeDriver to download images of HeroClix cards from [hcunits.net](http://hcunits.net)

#### Features
- can download entire sets by set id (example: "lotr")
- automatically handles both single and double-sided cards
- increases default browser resolution to 125% for better image quality
- automatically removes margin/padding from HTML-generated cards for seamless edges
- can use Python's multiprocessing to download cards in parallel

#### Usage
- Cards are saved to `./cards/<set_id>/<unit_id>.png`
- Speed up getting lots of cards with the `-m` option.

```
cd cardgrabber
python cardgrabber.py -h
```

Download a single card:
```
python cardgrabber cards hgpc001
```

Download a multiple cards:
```
python cardgrabber cards hgpc001 hx036
```

Download sets of cards:
```
python cardgrabber sets hgpc hx
```

Download FASTER with multiprocessing:
```
python cardgrabber sets hgpc hx -m
```

### ClixMapper
Generates 3D map objects in OBJ format with different heights per tile.

#### Features
- written in vanilla Python
- can generate maps of any size given a width and height in tiles
- automatic UV mapping
- different heightmap options including
  - integer arrays
  - simplex noise (using the `noise` package)
  - random heights