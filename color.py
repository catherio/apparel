#!/usr/bin/env python
import logging
import click
import jinja2
import os
from clarifai.rest import Image as CImage
from clarifai.rest import ClarifaiApp

logger = logging.getLogger(__name__)

CLIENT_ID = 'vmNalxaskF6tLZ19R20trI_bACz0Ies8SpWULYaV'
CLIENT_SECRET = '5KK0XWtDaarvsiSlwsDc4oJM-OXqSD6y2nF8jVWm'
app = ClarifaiApp(app_id=CLIENT_ID, app_secret=CLIENT_SECRET)

jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(
    os.path.dirname(__file__)))


def pic_colors(img_url):
    model = app.models.get('color')
    image = CImage(url=img_url)
    output = model.predict([image])
    return output['outputs'][0]['data']['colors']


def solarized_colors():
    return [
        {'raw_hex': '#002b36', 'value': 0.0666},
        {'raw_hex': '#073642', 'value': 0.0666},
        {'raw_hex': '#586e75', 'value': 0.0666},
        {'raw_hex': '#657b83', 'value': 0.0666},
        {'raw_hex': '#839496', 'value': 0.0666},
        {'raw_hex': '#93a1a1', 'value': 0.0666},
        {'raw_hex': '#eee8d5', 'value': 0.0666},
        {'raw_hex': '#fdf6e3', 'value': 0.0666},
        {'raw_hex': '#b58900', 'value': 0.0666},
        {'raw_hex': '#cb4b16', 'value': 0.0666},
        {'raw_hex': '#d33682', 'value': 0.0666},
        {'raw_hex': '#6c71c4', 'value': 0.0666},
        {'raw_hex': '#268bd2', 'value': 0.0666},
        {'raw_hex': '#2aa198', 'value': 0.0666},
        {'raw_hex': '#859900', 'value': 0.0666}
    ]


def htmlify(colors, img_url=None):
    width, height = 400, 200
    end = -1
    for c in colors:
        c['start'] = end + 1
        end = c['start'] + width * c['value']
        c['end'] = end

    template = jinja_env.get_template('color.html.template')
    with open('color.html', 'w') as f:
        f.write(template.render(colors=colors, height=height, width=width,
                                img_url=img_url))


@click.command()
def main():
    logger.setLevel(logging.INFO)
    logger.critical("Running")

#    img_url = 'https://samples.clarifai.com/metro-north.jpg'
#    colors = pic_colors(img_url)

    colors = solarized_colors()
    img_url = None

    htmlify(colors, img_url)
    logger.critical("Done!")


if __name__ == "__main__":
    main()
