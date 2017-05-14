#!/usr/bin/env python
import logging
import click
import jinja2
import os
import cv2
import math
import matplotlib.colors as pltc
from clarifai.rest import Image as CImage
from clarifai.rest import ClarifaiApp

# INSTRUCTIONS
#
# First add these lines to your init.el:
#     (add-to-list 'load-path "<apparel-directory>")
#     (add-to-list 'custom-theme-load-path "<apparel-directory>")
# and run M-x eval-buffer to reload it
#
# Run the ./apparel.py script to generate the appar.el theme
# from a photo taken from your webcam!
#
# Reload the appar.el file into emacs with
#     M-x load-file RET <apparel-directory>/appar.el
# Then set the theme in the customization menu at
#     M-x customize-themes
# Move the cursor onto the "apparel" theme and hit enter.
#
# Enjoy your fashion-coordinated emacs theme!


logger = logging.getLogger(__name__)


def take_photo(save_as='temp.png'):
    logger.critical("Taking photograph!")
    cap = cv2.VideoCapture(0)

    adjust_to_light_frames = 30
    for i in range(adjust_to_light_frames):
        ret, frame = cap.read()

    if not ret:
        raise Exception
    cv2.imwrite(save_as, frame)
    del(cap)
    return frame, save_as


app = ClarifaiApp(app_id=os.environ['CLARIFAI_CLIENT_ID'],
                  app_secret=os.environ['CLARIFAI_CLIENT_SECRET'])
demo_img_url = 'https://samples.clarifai.com/metro-north.jpg'


def pic_colors(**kwargs):
    logger.critical("Extracting key colors")
    model = app.models.get('color')
    image = CImage(**kwargs)
    output = model.predict([image])
    colors = output['outputs'][0]['data']['colors']
    for c in colors:
        c['hsv'] = hsv_color(c['raw_hex'])
    return sorted(colors, key=lambda c: -c['value'])
    # "value" here is "amount present in image", not "HSV value"


def hsv_color(hex):
    rgb = pltc.hex2color(hex)
    hsv = pltc.rgb_to_hsv(rgb)
    return hsv


html_template = 'apparel.html.template'
html_file = 'apparel.html'
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(
    os.path.dirname(__file__)))


def htmlify(colors, chosen_colors=None, img_url=None):
    logger.critical("Making demo page")
    width, height = 400, 200
    end = -1
    for c in colors:
        c['start'] = end + 1
        end = c['start'] + math.floor(width * c['value'])
        c['end'] = end

    template = jinja_env.get_template(html_template)
    with open(html_file, 'w') as f:
        f.write(template.render(colors=colors, height=height, width=width,
                                img_url=img_url))


theme_template = 'appar.el.template'
theme_file = 'appar.el'
emacs_neutral = ['#839496']
emacs_highlights = ["#268bd2", "#2aa198", "#859900"]
MIN_HSV_VALUE = 0.25


def make_emacs_theme(emacs_colors, new_colors):
    logger.info('Creating emacs theme')
    with open(theme_template, 'r') as template:
        theme = template.read()

    # filter for sufficent brightness, sort by saturation
    chosen_colors = [c for c in new_colors if
                     c['hsv'][2] > MIN_HSV_VALUE and
                     c['hsv'][2] < 0.9]
    chosen_colors = sorted(chosen_colors, key=lambda c: -c['hsv'][1])

    for (i, c) in enumerate(emacs_colors):
        theme = theme.replace(c, chosen_colors[i]['raw_hex'])
    with open(theme_file, 'w') as output:
        output.write(theme)

    return chosen_colors


@click.command()
@click.option('--load', type=str, default=None)
@click.option('--save_as', type=str, default='temp.png')
@click.option('--obnoxious', is_flag=True, default=True)
def main(load, save_as, obnoxious):
    logger.setLevel(logging.INFO)
    logger.critical("Running")

    if obnoxious:
        emacs_colors = emacs_neutral + emacs_highlights
    else:
        emacs_colors = emacs_highlights

    if load:
        colors = pic_colors(filename=load)
        chosen_colors = make_emacs_theme(emacs_colors, colors)
        htmlify(colors, chosen_colors, load)
    else:
        take_photo(save_as=save_as)
        colors = pic_colors(filename=save_as)
        chosen_colors = make_emacs_theme(emacs_colors, colors)
        htmlify(colors, chosen_colors, save_as)

    logger.critical("Done!")


if __name__ == "__main__":
    main()
