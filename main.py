#!/usr/bin/env python3

import os
import platform
import subprocess
from sys import argv
import tkinter as tk
import tempfile
from pytimedinput import timedInput
from notifypy import Notify
import time
import psutil
import bcrypt

from creds import get_creds

OS = platform.system()
PASSWORD = get_creds().encode()

notification = Notify()
notification.title = "XAN STOP."

# fichier à kill à chaque fois que le mot de passe n'est pas sorti
TARGET = argv[1] if argv else "StreetFighter6"


# Version MacOS
def prompt_terminal_mac():
    apple_script = '''
        try
            display dialog "Mot de passe :" ¬
                default answer "" ¬
                with hidden answer ¬
                buttons {"Annuler", "OK"} ¬
                default button "OK" ¬
                giving up after 5
            text returned of result
        on error
            return ""
        end try
    '''

    result = subprocess.run(
        ["osascript", "-e", apple_script],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        return None

    password = result.stdout.strip()
    return password or None

# version Windows
def prompt_terminal_win():
    result = {"password": None}

    root = tk.Tk()
    root.title("NO SF6 ZONE")
    root.resizable(False, False)
    root.attributes("-topmost", True)

    frame = tk.Frame(root, padx=20, pady=15)
    frame.pack()

    tk.Label(frame, text="Mot de passe :").pack(anchor="w")

    password_entry = tk.Entry(frame, show="*", width=30)
    password_entry.pack(pady=(5, 10))
    password_entry.focus_set()

    def validate():
        password = password_entry.get()
        result["password"] = password or None
        root.destroy()

    def cancel():
        root.destroy()

    tk.Button(frame, text="Valider", command=validate).pack()

    password_entry.bind("<Return>", lambda event: validate())
    root.protocol("WM_DELETE_WINDOW", cancel)

    root.after(5000, cancel)
    root.mainloop()

    return result["password"]


def mdp_check() -> bool:
    # passw = prompt_terminal_win() if OS == "Windows" else prompt_terminal_mac()
    
    passw = prompt_terminal_win() if OS == "Windows" else prompt_terminal_mac()

    if passw is None:
        notification.message = "TEMPS ÉCOULÉ ! Va me lancer un jeu solo espèce de malade."
        notification.send()
        return False

    if bcrypt.checkpw(passw.encode(), PASSWORD):
        notification.message = "Hold up... Let him cook..."
        notification.send()
        return True
        
    notification.message = "TU ARRÊTE."
    notification.send()
    return False


def check_process_in_list():

    for proc in psutil.process_iter(attrs=['name']):
        try:
            process_name = proc.info.get("name") or ""
            if TARGET.lower() in process_name.lower():
                print(process_name)
                return proc.pid
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    return None


def main():
    while True:
        pid = check_process_in_list()

        if pid is None:
            time.sleep(1)
            continue
        # Si le jeu qu'on cherche est en train de s'allumer
        # On lance le mdp check: les processus sont suspendus.
        pro = psutil.Process(pid)
        if not mdp_check():
            # Here we go again
            try:
                pro.kill()
                time.sleep(5)
            except:
                continue
        return
            
if __name__ == "__main__":
    try:
        main()
    except:
        print("Signal d'arrêt capté, fermeture du script.")