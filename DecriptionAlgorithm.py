#!/usr/bin/env python3
"""
Two ways to run the string-to-values converter:

1. Prompt style: script asks for input via terminal prompt.
2. Argument style: script reads the input string from a command-line argument.
"""
import sys
import argparse

def string_to_values(s: str) -> list[int]:
    """
    Convert a string into a list of integer “portion” sums according to these rules:
    1. Split the input into slots: each 'z' starts a slot that includes itself and the following character
       if the last added character was 'z'; all other characters form single-character slots.
    2. Map each letter a-z to 1-26, non-letters to 0; a multi-character slot is the sum of its chars.
    3. Traverse slots: at each slot value N, sum the next N slots and append the sum; skip 1+N slots.
    """
    def char_val(c: str) -> int:
        c = c.lower()
        return ord(c) - 96 if 'a' <= c <= 'z' else 0

    # 1) Build slots
    slots: list[str] = []
    i = 0
    while i < len(s):
        if s[i].lower() == 'z':
            slot = s[i]
            i += 1
            # Extend slot while the last char is 'z' and there are more characters
            while i < len(s) and s[i].lower() == 'z':
                slot += s[i]
                i += 1
            # Add the next character after the z-chain, if it exists
            if i < len(s):
                slot += s[i]
                i += 1
            slots.append(slot)
        else:
            slots.append(s[i])
            i += 1

    # 2) Compute numeric values for each slot
    slot_vals = [sum(char_val(c) for c in slot) for slot in slots]

    # 3) Compute portions
    result: list[int] = []
    idx = 0
    while idx < len(slot_vals):
        count = slot_vals[idx]
        portion = sum(slot_vals[idx + 1 : idx + 1 + count])
        result.append(portion)
        idx += 1 + count

    return result


def main_prompt() -> None:
    """
    Approach 1: Ask the user to type the string at a prompt.
    """
    user_input = input("Enter the string to convert: ")
    print("Result:", string_to_values(user_input))


def main_arg() -> None:
    """
    Approach 2: Read the string from a command-line argument.
    """
    parser = argparse.ArgumentParser(
        description="Convert a string into portion sums according to the z-chain logic."
    )
    parser.add_argument(
        "string", help="The input string to convert, e.g. 'dz_a_aazzaaa'"
    )
    args = parser.parse_args()
    print(string_to_values(args.string))


if __name__ == "__main__":
    # Choose mode based on presence of extra CLI args
    if len(sys.argv) == 1:
        main_prompt()
    else:
        main_arg()