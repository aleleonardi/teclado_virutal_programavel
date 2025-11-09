import json
import os
import pyautogui
import pyperclip
import time
import subprocess

CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'config.json')

SPECIAL_KEYS = {
    'ENTER': 'enter',
    'ESC': 'esc',
    'TAB': 'tab',
    'SPACE': 'space',
    'BACKSPACE': 'backspace',
    'DELETE': 'delete',
    'F1': 'f1', 'F2': 'f2', 'F3': 'f3', 'F4': 'f4', 'F5': 'f5',
    'F6': 'f6', 'F7': 'f7', 'F8': 'f8', 'F9': 'f9', 'F10': 'f10',
    'F11': 'f11', 'F12': 'f12'
}

MODIFIERS = {
    'CTRL': 'ctrl',
    'ALT': 'alt',
    'SHIFT': 'shift',
}


def load_config():
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_config(cfg):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)


def _press_combo(parts):
    """Executa combinações como CTRL+SHIFT+C."""
    keys = []
    for p in parts:
        up = p.upper()
        if up in MODIFIERS:
            keys.append(MODIFIERS[up])
        elif up in SPECIAL_KEYS:
            keys.append(SPECIAL_KEYS[up])
        else:
            keys.append(p.lower())
    pyautogui.hotkey(*keys)


def _focus_vnc_window():
    """Procura e ativa uma janela de destino (VNC ou Editor de Texto)."""
    try:
        result = subprocess.run(['wmctrl', '-l'], capture_output=True, text=True)
        for line in result.stdout.splitlines():
            # procura por possíveis destinos
            if any(x in line.lower() for x in ['vnc', 'viewer', 'editor de texto', 'gedit', 'documento']):
                win_id = line.split()[0]
                subprocess.run(['wmctrl', '-i', '-a', win_id])
                time.sleep(0.3)
                return True
    except Exception as e:
        print(f"[ERRO foco janela] {e}")
    return False



def send_return(retorno: str, *, copy_to_clipboard=True, delay=0.02):
    """Foca a janela do VNC e envia o retorno configurado."""
    _focus_vnc_window()

    if '+' in retorno and retorno.upper().split('+')[0] in MODIFIERS:
        parts = retorno.split('+')
        _press_combo(parts)
        return

    up = retorno.upper()
    if up in SPECIAL_KEYS:
        pyautogui.press(SPECIAL_KEYS[up])
        return

    if copy_to_clipboard and len(retorno) > 3:
        try:
            pyperclip.copy(retorno)
            pyautogui.hotkey('ctrl', 'v')
            return
        except Exception:
            pass

    for ch in retorno:
        pyautogui.typewrite(ch)
        time.sleep(delay)
