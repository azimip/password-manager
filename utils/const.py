from collections import defaultdict

PASSWORD_MINIMUM_LENGTH = 8
SPECIAL_CHARS = ['!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '-', '+', '?', '_', '=', ',', '<', '>']

with open("assets/common_passwords.txt") as f:
    COMMON_PASSWORDS = [line.rstrip() for line in f]

LEET = defaultdict(set)
with open("assets/leet.txt") as add_ons_file:
    for line in add_ons_file:
        chars = eval(line.rstrip())
        for ch in chars:
            LEET[ch].update(*chars)
