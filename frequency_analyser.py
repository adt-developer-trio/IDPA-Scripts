#!/usr/bin/python3

import click
import operator
import json


@click.command()
@click.argument('input', type=click.File('r'))
@click.option('--sort-count/--sort-key', default=True)
@click.option('--alpha-only', is_flag=True, default=False)
@click.option('--buffer', type=int, default=0)
@click.option('--output', '-o')
def cli(input, sort_count, alpha_only, buffer, output):
    charbuffer = []
    charmap = {}
    strmap = {}
    while True:
        char = input.read(1)
        if not char:
            break
        if alpha_only and not char.isalpha():
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
        output_to_file(charmap, strmap, output)
    else:
        print_to_console(charmap, strmap, sort_count)


def output_to_file(charmap, strmap, output):
    with open(output, 'w') as file:
        obj = {
            'single': charmap,
            'combinations': strmap,
        }
        json.dump(obj, file, indent=4)


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
