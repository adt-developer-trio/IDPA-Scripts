#!/usr/bin/python3
from PIL import Image, ImageDraw, ImageFont
import json
import click


@click.command()
@click.argument('layout_file', type=click.File('r'))
@click.argument('frequency_file', type=click.File('r'), required=False)
@click.option('--output', '-o', default='heatmap.png')
def cli(layout_file, frequency_file, output):
    # Parse json files
    layout_data = json.load(layout_file)
    freq_data = json.load(frequency_file) if frequency_file else None
    # Generate layout
    layout = generate_layout(layout_data, freq_data['single'])
#   layout_data = process_layout(layout_data, freq_data)
    # Save image
    img = render_layout(layout)
    img.save(output)


def generate_row(keys, freq_data):
    glyphs = []
    sizes = []
    freq = []

    next_size = None

    for key in keys:
        # If it's a special "key" handle it accordingly
        if isinstance(key, dict):
            if 'w' in key:
                next_size = key['w']
        else:
            # Get the glyph
            glyphs.append(key)
            # Get the size and reset it
            size = next_size or 1
            next_size = None
            sizes.append(size)
            # Get the frequency
            freq.append(freq_data.get(key.lower(), 0))

    return glyphs, sizes, freq


def generate_layout(layout_data, freq_data):
    glyphs = []
    sizes = []
    freq = []

    # Go through every key in the layout
    for row in layout_data:
        glyph_row, sizes_row, freq_row = generate_row(row, freq_data)
        glyphs.append(glyph_row)
        sizes.append(sizes_row)
        freq.append(freq_row)

    return {
        'glyphs': glyphs,
        'sizes': sizes,
        'freq': freq,
        }


def render_layout(layout):
    # Create the image
    # TODO: The size should not be static
    img = Image.new('RGB', (2000, 720))
    draw = ImageDraw.Draw(img)

    # Find highest frquency
    max_freq = max(map(max, layout['freq']))

    zipped = list(zip(layout['glyphs'], layout['sizes'], layout['freq']))
    print(zipped[2])

    # Estimate the size of a key
    # TODO: This need to be improved
    unit = img.height / len(zipped)

    # Prepare font
    font = ImageFont.truetype('arial.ttf', round(unit/3))

    # Iterate over every row
    for row_nr, row_keys in enumerate(zipped):
        # Keep track of the offset from the left border
        offset = 0
        # Zip it
        keys = zip(row_keys[0], row_keys[1], row_keys[2])
        # Iterate over every key
        for key_nr, key in enumerate(keys):
            # Calculate the effective size
            size = unit * key[1]
            # Calculate the rectangle
            topleft = (offset, row_nr * unit)
            botright = (offset + size, row_nr * unit + unit)
            # Update the offset
            offset += size
            # Calculate color
            alpha = round(key[2] / max_freq * 255)
            # Draw the key
            draw.rectangle([topleft, botright], (round(255-alpha), 255, round(255-alpha)), 'gray')
            draw.text(topleft, key[0], 'black', font=font)
    return img


if __name__ == "__main__":
    cli()
