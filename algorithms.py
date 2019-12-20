import json


def get_central_keys(layout):
    central = layout[2][1:5] + layout[2][7:11]
    return [key[0] for key in central]


def finger_keys(layout):
    return [
        [
            layout[1][1][0], layout[2][1][0], layout[3][1][0],
            layout[3][2][0]
        ], [
            layout[1][2][0], layout[2][2][0], layout[3][3][0]
        ], [
            layout[1][3][0], layout[2][3][0], layout[3][4][0]
        ], [
            layout[1][4][0], layout[2][4][0], layout[3][5][0],
            layout[1][5][0], layout[2][5][0], layout[3][6][0]
        ], [
            layout[1][6][0], layout[2][6][0], layout[3][7][0],
            layout[1][7][0], layout[2][7][0], layout[3][8][0]
        ], [
            layout[1][8][0], layout[2][8][0], layout[3][9][0]
        ], [
            layout[1][9][0], layout[2][9][0], layout[3][10][0]
        ], [
            layout[1][10][0], layout[2][10][0], layout[3][11][0],
            layout[1][11][0], layout[2][11][0],
            layout[1][12][0], layout[2][12][0]
        ]
    ]


def finger_distance(layout, frequency):
    central_keys = get_central_keys(layout)

    # Relative distance
    distance = 0
    for (key, val) in frequency.items():
        if key not in central_keys:
            distance += val

    # Absolute distance
    absolute = sum(sorted(frequency.values())[:-8])
    return (distance, distance / absolute)


def finger_distribution(layout, frequency):
    distributions = finger_keys(layout)
    res = []

    all_sum = get_char_count(frequency)
    for distribution in distributions:
        key_sum = 0
        for key in distribution:
            key_frequency = frequency.get(key, 0)
            key_sum += key_frequency
        res.append(key_sum)

    relative_vals = [val / all_sum for val in res]
    absolute_val = sum([abs(val - 0.125) for val in relative_vals])
    return (relative_vals, absolute_val)


def hand_distribution(layout, frequency):
    finger_vals = finger_distribution(layout, frequency)
    left = sum(finger_vals[0:4])
    right = sum(finger_vals[4:])
    return ([left, right], [abs(left - 0.5), abs(right - 0.5)])


def get_first_layer(layout):
    temp = []
    for line in layout:
        line_vals = []
        for key in line:
            if isinstance(key, list):
                line_vals.append(key[0])
            else:
                line_vals.append(str(key))
        temp.append(line_vals)


def get_char_count(frequency):
    return sum(frequency.values())


def row_distribution(layout, frequency):
    homerow_vals = 0
    bottomrow_vals = 0
    toprow_vals = 0

    homerow = layout[2]
    bottomrow = layout[3]
    toprow = layout[1]

    count = get_char_count(frequency)

    for (key, val) in frequency.items():
        if key in homerow:
            homerow_vals += val
        elif key in toprow:
            toprow_vals += val
        elif key in bottomrow:
            bottomrow_vals += val

    relative_vals = \
        [r / count for r in [toprow_vals, homerow_vals, bottomrow_vals]]

    vals_sorted = sorted(frequency.values())
    absolute_vals = [sum(vals_sorted[10:21]) / count,
                     sum(vals_sorted[:10]) / count,
                     sum(vals_sorted[21:]) / count]

    vals_zipped = zip(absolute_vals, relative_vals)
    absolute_val = sum([abs(a - r) / a for (a, r) in vals_zipped])
    return (relative_vals, absolute_val)


def main():

    with open('./layouts/qwertz.json', 'r', encoding='utf-8') as file:
        layout = json.load(file)

    with open('./output/de/de.json', 'r', encoding='utf-8') as file:
        frequency = json.load(file).get('single')

    print(get_central_keys(layout))
    print(finger_keys(layout))
    print(finger_distance(layout, frequency))
    print(finger_distribution(layout, frequency))
    print(row_distribution(layout, frequency))


if __name__ == "__main__":
    main()
