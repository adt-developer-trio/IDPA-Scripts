import json


def get_central_keys(layout):
    central = layout[2][1:5] + layout[2][7:11]
    return [key[0] for key in central]


def normalize(val, min_val, max_val):
    return (val - min_val) / (max_val - min_val)


def finger_keys(layout):
    layout = get_first_layer(layout)
    return [
        [
            layout[1][1], layout[2][1], layout[3][1],
            layout[3][2]
        ], [
            layout[1][2], layout[2][2], layout[3][3]
        ], [
            layout[1][3], layout[2][3], layout[3][4]
        ], [
            layout[1][4], layout[2][4], layout[3][5],
            layout[1][5], layout[2][5], layout[3][6]
        ], [
            layout[1][6], layout[2][6], layout[3][7],
            layout[1][7], layout[2][7], layout[3][8]
        ], [
            layout[1][8], layout[2][8], layout[3][9]
        ], [
            layout[1][9], layout[2][9], layout[3][10]
        ], [
            layout[1][10], layout[2][10], layout[3][11],
            layout[1][11], layout[2][11],
            layout[1][12], layout[2][12]
        ]
    ]


def get_column(layout, i):
    layout = get_first_layer(layout)
    return [
        layout[1][i + 1],
        layout[2][i + 1],
        layout[3][i + 2],
    ]


def finger_distance(layout, frequency):
    central_keys = get_central_keys(layout)

    # Relative distance
    distance = 0
    for (key, val) in frequency.items():
        if key not in central_keys:
            distance += val

    # Absolute distance
    sorted_frequencies = sorted(frequency.values())
    minimum = sum(sorted_frequencies[:-8])
    maximum = sum(sorted_frequencies[8:])
    return (
        [distance, distance / get_char_count(frequency)],
        1 - normalize(distance, minimum, maximum)
    )


def finger_distribution(layout, frequency):
    distributions = finger_keys(layout)
    res = []

    all_sum = 0
    for distribution in distributions:
        key_sum = 0
        for key in distribution:
            key_frequency = frequency.get(key, 0)
            key_sum += key_frequency
        res.append(key_sum)
        all_sum += key_sum

    relative_vals = [val / all_sum for val in res]
    val = sum([abs(val - 0.125) for val in relative_vals])

    # Calc best case
    minimum = 0

    # Calc worst case
    lengths = sorted([len(d) for d in distributions])[::-1]
    sorted_frequencies = sorted(frequency.values())[::-1]
    t = 0
    maximum = 0
    for length in lengths:
        next_point = t + length
        if next_point > len(sorted_frequencies):
            next_point = len(sorted_frequencies)

        maximum += abs(sum(sorted_frequencies[t:next_point]) / all_sum - 0.125)
        t += length

    return (relative_vals, 1 - normalize(val, minimum, maximum))


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
    return temp


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
        else:
            count -= val

    relative_vals = \
        [r / count for r in [toprow_vals, homerow_vals, bottomrow_vals]]

    vals_sorted = sorted(frequency.values())[::-1]
    reversed_sorted = vals_sorted[::-1]
    best_case = [sum(vals_sorted[10:21]) / count,
                 sum(vals_sorted[:10]) / count,
                 sum(vals_sorted[21:]) / count]
    worst_case = [sum(reversed_sorted[10:21]) / count,
                  sum(reversed_sorted[:10]) / count,
                  sum(reversed_sorted[21:]) / count]

    normalized = []
    for i in range(3):
        rel = relative_vals[i]
        worst = worst_case[i]
        best = best_case[i]

        val = normalize(rel, worst, best)
        normalized.append(val)

    normalized = sum(normalized[1:]) / 2
    return (relative_vals, normalized)


def combination_occurrences(layout, frequency):

    # 1) Sum up combinations with same keys
    summed = {}
    for combination in frequency.keys():
        key = combination
        if summed.get(combination[::-1]):
            key = combination[::-1]
        summed.update({
            key: frequency.get(key) + frequency.get(key[::-1], 0)})

    positive = 0
    negative = 0
    # 2) Calculate +1 combinations
    columns = [
        [get_column(layout, i) for i in range(4)],
        [get_column(layout, i) for i in range(6, 10)]
    ]

    for hand in columns:
        prev_column = hand.pop(0)
        for column in hand:
            for i in range(len(prev_column)):
                pair = prev_column[i] + column[i]
                sum_pair = summed.get(pair, False) \
                    or summed.get(pair[::-1], False) \
                    or 0
                if sum_pair:
                    positive += sum_pair
            prev_column = column

    # 3) Calculate -1 combinations
    fingers = finger_keys(layout)
    for pair in summed.keys():
        for finger in fingers:
            if all([char in finger for char in pair]):
                negative += summed.get(pair)

    # 4) Differences
    relative = [positive, negative]
    to_compare = sum(summed.values())
    absolute_negative = normalize(-negative, -to_compare, 0)
    return (relative, absolute_negative)


def main():

    with open('./layouts/qwertz.json', 'r', encoding='utf-8') as file:
        layout = json.load(file)

    with open('./output/en/en.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
        frequency = data.get('single')
        combinations = data.get('combinations')

    distance = finger_distance(layout, frequency)
    finger_distr = finger_distribution(layout, frequency)
    row_distr = row_distribution(layout, frequency)
    combination = combination_occurrences(layout, combinations)
    fitness = distance[1] + finger_distr[1] + row_distr[1] + combination[1]

    print(f'Finger Distance : \t\t{str(distance)}')
    print(f'Finger Distribution : \t\t{str(finger_distr)}')
    print(f'Row Distribution : \t\t{str(row_distr)}')
    print(f'Combination Occurences : \t{str(combination)}')
    print(f'Total score: \t{str(fitness)}')


if __name__ == "__main__":
    main()
