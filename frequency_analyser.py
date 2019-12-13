#!/usr/bin/python3

import click
import operator
import json
import codecs
import csv


CHARS = 'abcdefghijklmnopqrstuvwxyzäöü'


@click.command()
@click.argument('input') 
@click.option('--sort-count/--sort-key', default=True)
@click.option('--buffer', type=int, default=0)
@click.option('--output', '-o')
@click.option('--csv/--json', default=False)
def cli(input, sort_count, buffer, output, csv):
    input_file = codecs.open(input, 'r', 'utf-8')
    charbuffer = []
    charmap = {}
    strmap = {}
    while True:
        try:
            char = input_file.read(1)
        except UnicodeDecodeError as err:
            charbuffer = []
            continue
        if not char:
            break
        if char not in CHARS:
            charbuffer = []
            continue
        char = char.lower()
        if char in charmap:
            charmap[char] += 1
        else:
            charmap[char] = 1

        if buffer > 0:
            # Update char buffer
            if char == '\n':
                charbuffer = []
            else:
                charbuffer.append(char)
                if len(charbuffer) > buffer + 1:
                    charbuffer.pop(0)
                if len(charbuffer) > 1:
                    string = ''.join(charbuffer)
                    if string in strmap:
                        strmap[string] += 1
                    else:
                        strmap[string] = 1

    if output:
        if csv:
            output_to_csv(charmap, strmap, output)
        else:
            output_to_file(charmap, strmap, output)
    else:
        print_to_console(charmap, strmap, sort_count)


def output_to_csv(charmap, strmap, output):
    with open(output, 'w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        for char, freq in charmap.items():
            writer.writerow([char, freq])
        for char, freq in strmap.items():
            writer.writerow([char, freq])


def output_to_file(charmap, strmap, output):
    with open(output, 'w', encoding='utf-8') as file:
        obj = {
            'single': charmap,
            'combinations': strmap,
        }
        json.dump(obj, file, indent=4, ensure_ascii=False)


def print_to_console(charmap, strmap, sort_count):
    print('Charmap')
    if not sort_count:
        charmap = dict(sorted(charmap.items()))
    else:
        charmap = dict(sorted(
            charmap.items(),
            key=operator.itemgetter(1),
            reverse=True))

    for char, count in charmap.items():
        if char == '\n':
            char = '\\n'
        print(char + ': ' + str(count))

    print('String map')
    if not sort_count:
        strmap = dict(sorted(strmap.items()))
    else:
        strmap = dict(sorted(
            strmap.items(),
            key=operator.itemgetter(1),
            reverse=True))

    for string, count in strmap.items():
        if string == '\n':
            string = '\\n'
        print(string + ': ' + str(count))


if __name__ == "__main__":
    cli()
