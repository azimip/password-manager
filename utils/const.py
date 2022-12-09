from collections import defaultdict

with open("assets/common_add_ons.txt") as add_ons_file:
    ADD_ONS = [line.rstrip() for line in add_ons_file]

LEET = defaultdict(set)
with open("assets/leet.txt") as add_ons_file:
    for line in add_ons_file:
        chars = eval(line.rstrip())
        for ch in chars:
            LEET[ch].update(*chars)
