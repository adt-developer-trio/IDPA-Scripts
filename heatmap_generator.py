#!/usr/bin/python3
from PIL import Image, ImageDraw, ImageFont
import json
import click

keyboard = [
  [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2],
  [1.5, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, [1.5, 1.25]],
  [1.75, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
  [1.25, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2.75],
  [1.25, 1.25, 1.25, 6.25, 1.25, 1.25, 1.25, 1.25]
]

@click.command()
@click.argument('layout_file', type=click.File('r'))
@click.argument('frequency_file', type=click.File('r'), required=False)
@click.option('--output', '-o', default='heatmap.png')
def cli(layout_file, frequency_file, output):
    # Parse json files
    layout_data = json.load(layout_file)
    freq_data = json.load(frequency_file)['single'] if frequency_file else None
    # Generate layout
    layout = generate_layout(layout_data, freq_data)
#   layout_data = process_layout(layout_data, freq_data)
    # Save image
    img = render_layout(layout)
    img.save(output)


def generate_row(keys, freq_data):
    glyphs = []
    freq = []

    for key in keys:
        # Get the glyph
        glyphs.append(key)

        # Get the frequency
        if freq_data:
            if isinstance(key, list):
                freq.append(freq_data.get(key[0].lower(), 0))
            else:
                freq.append(freq_data.get(key.lower(), 0))
        else:
            freq.append(0)

    return glyphs, freq


def generate_layout(layout_data, freq_data):
    glyphs = []
    freq = []

    # Go through every key in the layout
    for row in layout_data:
        glyph_row, freq_row = generate_row(row, freq_data)
        glyphs.append(glyph_row)
        freq.append(freq_row)

    return {
        'glyphs': glyphs,
        'freq': freq,
        }


def render_layout(layout):
    # Create the image
    # TODO: The size should not be static
    img = Image.new('RGB', (1500, 500), 'white')
    draw = ImageDraw.Draw(img)

    # Find highest frquency
    max_freq = max(map(max, layout['freq']))

    zipped = list(zip(layout['glyphs'], keyboard, layout['freq']))

    # Estimate the size of a key
    unit = img.height / len(zipped)

    # Set the padding
    pad = 10

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
            # Calculate color
            if key[2] == 0:
                color = 'white'
            else:
                color = get_color(key[2], max_freq)
            # Calculate the effective size
            if isinstance(key[1], list):
                size = unit * key[1][0]
                # Calculate the rectangle
                topleft = (offset, row_nr * unit)
                botright = (
                    offset + unit * max(key[1]),
                    row_nr * unit + unit * 2
                )
                # Draw the key
                points = [
                    topleft,
                    (topleft[0] + unit * key[1][0], topleft[1]),
                    botright,
                    (botright[0] - key[1][1] * unit, botright[1]),
                    (botright[0] - key[1][1] * unit, botright[1] - unit),
                    (topleft[0], topleft[1] + unit)
                ]
                draw.polygon(points, color, 'gray')
            else:
                size = unit * key[1]
                # Calculate the rectangle
                topleft = (offset, row_nr * unit)
                botright = (offset + size, row_nr * unit + unit)
                # Draw the key
                draw.rectangle([topleft, botright], color, 'gray')
            # Update the offset
            offset += size
            # Draw the glyph
            topleft_pad = (topleft[0] + pad, topleft[1] + pad)
            if isinstance(key[0], list):
                # chars = [char.title() for char in key[0]]
                chars = key[0]
                layers = len(chars)
                font_height = font.getsize(chars[0])[1]
                botleft_pad = (
                    topleft[0] + pad,
                    topleft[1] + unit - font_height - pad
                )
                draw.text(botleft_pad, chars[0], 'black', font=font)
                if layers >= 2:
                    draw.text(topleft_pad, chars[1], 'black', font=font)
                if layers == 3:
                    font_size = font.getsize(chars[2])
                    botright_pad = (
                        botright[0] - font_size[0] - pad,
                        botright[1] - font_size[1] - pad
                    )
                    draw.text(botright_pad, chars[2], 'black', font=font)
            else:
                # draw.text(topleft_pad, key[0].title(), 'black', font=font)
                draw.text(topleft_pad, key[0], 'black', font=font)
    draw.rectangle([(0, 0), (img.width - 1, img.height - 1)], None, 'grey')

    return img


def get_color(val, max_val):
    value = val / max_val
    hue = (1 - value) * 220
    sat = 100
    lig = 50
    return f'hsl({hue}, {sat}%, {lig}%)'


if __name__ == "__main__":
    cli()
