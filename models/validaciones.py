import re

def validar_numero(numero):
    return bool(re.fullmatch(r'^\+\d{6,15}$', numero))

def validar_no_vacio(x):
    if not x:
        print(f"ADVERTENCIA: El termino '{x}', esta vacío")
        return False
    else:
        return True