#!/usr/bin/python3

import nacl.utils
import json
import os

from nacl.pwhash import argon2id
from nacl.secret import SecretBox
from nacl.exceptions import CryptoError

from typing import Callable
from pwinput import pwinput
from ensure_file import ensure_file as ef


# DO NOT put a trailing slash!
SAVING_PATH = "~/.trinkey"
SAVING_PATH = os.path.expanduser(SAVING_PATH)

def derive_key(password: str, salt: bytes) -> bytes:
    return argon2id.kdf(SecretBox.KEY_SIZE, password.encode(), salt, opslimit=argon2id.OPSLIMIT_INTERACTIVE, memlimit=argon2id.MEMLIMIT_INTERACTIVE)

def encrypt(message: str, password: str) -> bytes:
    salt = nacl.utils.random(argon2id.SALTBYTES)
    return salt + SecretBox(derive_key(password, salt)).encrypt(message.encode())

def decrypt(encrypted_message: bytes, password: str) -> str:
    return SecretBox(derive_key(password, encrypted_message[:argon2id.SALTBYTES])).decrypt(encrypted_message[argon2id.SALTBYTES:]).decode()

def clear():
    os.system("clear")

ef(f"{SAVING_PATH}", folder=True)
if os.path.exists(f"{SAVING_PATH}/rcman.json.encrypted"):
    plaintext_pass = pwinput("Enter your password:\n>>> ")
else:
    plaintext_pass = pwinput("Enter your password that will be used to encrypt your codes (this can NOT be changed later!):\n>>> ")
    ef(f"{SAVING_PATH}/rcman.json.encrypted", default_value=encrypt("{}", plaintext_pass))

clear()

GRAY = "\x1b[90m"
RED = "\x1b[31m"
YELLOW = "\x1b[33m"
RESET_COLOR = "\x1b[39;49m"

BOLD = "\x1b[1m"
UNDERLINE = "\x1b[4m"
RESET_STYLE = "\x1b[22;23;24;25;26;27;28;29m"

try:
    index: dict[str, list[str]] = json.loads(decrypt(open(f"{SAVING_PATH}/rcman.json.encrypted", "rb").read(), plaintext_pass))
except CryptoError:
    print(f"{BOLD}{RED}WRONG PASSWORD!{RESET_STYLE} LOOOOOOOOOSERRRRRRRRRR{RESET_COLOR}")
    exit()

def save_index():
    global index
    index = sorted_dict(index)
    g = open(f"{SAVING_PATH}/rcman.json.encrypted", "wb")
    g.write(encrypt(json.dumps(index), plaintext_pass))
    g.close()

def continuous_input():
    end = False
    count = 1
    inputs = []

    while not end:
        inputs.append(input(f"{count}: "))
        end = not bool(inputs[-1])
        count += 1

    return inputs[:-1:]

def can_be_int(val: str) -> bool:
    if not val:
        return False

    if val[0] not in "-0123456789":
        return False

    for i in val[1::]:
        if i not in "0123456789":
            return False

    return True

def actions(options: list[str] | tuple[str], start_index: int = 1) -> int:
    c = start_index - 1
    for i in options:
        c += 1
        print(f"{c} {GRAY}-{RESET_COLOR} {i}")

    _in = ""
    while not can_be_int(_in) or (int(_in) > c or int(_in) <= start_index - 1):
        _in = input(">>> ")

    return int(_in)

def sorted_dict(
    obj: dict,
    key: Callable=lambda a: a,
    reverse: bool=False
) -> dict:
    new_dict = {}
    for i in sorted(obj, key=key, reverse=reverse):
        new_dict[i] = obj[i]
    return new_dict

def list_codes():
    while True:
        clear()
        print("Which service do you want to see the codes for?")
        _in = actions(["Return"] + [i for i in index], 0)

        if _in == 0:
            return
        else:
            view_singular([i for i in index][_in - 1])

def confirm(prompt: str, color: str=RED) -> bool:
    print(f"{prompt}")
    return actions([f"{color}Yes{RESET_COLOR}", "No"]) == 1

def view_singular(name: str):
    while True:
        clear()
        print(f"What do you want to do with {BOLD}{name}{RESET_STYLE}?")
        _in = actions(["Return", f"Get codes {GRAY}({len(index[name])}){RESET_COLOR}", "Add a code", f"{YELLOW}Remove a code{RESET_COLOR}", f"{RED}Delete all codes{RESET_COLOR}", "Rename service"], 0)

        if _in == 0:
            return

        elif _in == 1:
            clear()
            print("\n".join(index[name]))
            input(">>> ")

        elif _in == 2:
            new_code = input("Enter the code ('c' to cancel):\n>>> ")
            if new_code != "c":
                index[name].append(new_code)
                save_index()

        elif _in == 3:
            clear()
            print(f"Which code for {BOLD}{name}{RESET_STYLE} do you want to remove?")
            _in2 = actions(["Cancel"] + index[name], 0)

            if _in2 != 0:
                if confirm(f"Are you sure you want to delete the code {index[name][_in2 - 1]}? {UNDERLINE}This can NOT be undone!{RESET_STYLE}", YELLOW):
                    index[name].pop(_in2 - 1)
                    save_index()

        elif _in == 4:
            if confirm(f"Are you sure that you want to delete all of the codes for {BOLD}{name}{RESET_STYLE}? {UNDERLINE}This can NOT be undone!{RESET_STYLE}"):
                del index[name]
                save_index()
                return

        elif _in == 5:
            valid = False

            while not valid:
                new_name = input(f"Enter the new name for {BOLD}{name}{RESET_STYLE} ('c' to cancel):\n>>> ")

                if new_name in index:
                    print(f"{BOLD}{new_name}{RESET_STYLE} is already used!")
                else:
                    valid = True

            if new_name != "c":
                index[new_name] = index[name]
                del index[name]
                save_index()
                view_singular(new_name)
                return

def add_codes():
    clear()

    valid = False
    while not valid:
        name = input("What is the name of the service that you are adding codes for? ('c' to cancel)\n>>> ")
        clear()

        if name in index:
            print(f"{BOLD}{name}{RESET_STYLE} is already used!")
        else:
            valid = True

    if name == "c":
        return

    print(f"Input the codes for {BOLD}{name}{RESET_STYLE}:")
    codes = continuous_input()

    index[name] = codes
    save_index()
    view_singular(name)

def main():
    while True:
        clear()
        print("What would you like to do?")
        _in = actions(["Exit", "Get a code", "Add new codes"], 0)

        if _in == 0:
            return
        elif _in == 1:
            list_codes()
        elif _in == 2:
            add_codes()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        ...
