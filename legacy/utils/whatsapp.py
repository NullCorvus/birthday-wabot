import os
import time
import urllib
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

class WhatsAppBot:
    def __init__(self):
        self.driver = None
        self.inicializar_driver()

    def inicializar_driver(self):
        home_dir = os.path.expanduser('~')
        profile_path = os.path.join(home_dir, "mensajeWhatsapp")
        
        if not os.path.exists(profile_path):
            os.makedirs(profile_path)

        options = Options()
        options.add_argument(f"user-data-dir={profile_path}")
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)

    def enviar_mensaje(self, id, numero, nombre, mensaje, model):
        encoded_message = urllib.parse.quote(mensaje)
        wa_url = f"https://web.whatsapp.com/send?phone={numero}&text={encoded_message}"
        
        time.sleep(5)
        hoy = datetime.now()
        fecha = hoy.strftime("%Y-%m-%d %H:%M:%S")
        
        try:
            self.driver.get(wa_url)
            
            message_input_field = WebDriverWait(self.driver, 25).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[contenteditable="true"][role="textbox"]'))
            )

            button = WebDriverWait(self.driver, 15).until(
                EC.element_to_be_clickable((
                    By.CSS_SELECTOR,
                    'button[data-icon="wds-ic-send-filled"], button[aria-label="Enviar"], button[aria-label="Send"]'
                ))
            )

            button.click()
            time.sleep(3)
            model.agregar_log(id, nombre, numero, fecha, mensaje, "Enviado", "")
            return True

        except Exception as e:
            model.agregar_log(id, nombre, numero, fecha, mensaje, "No Enviado", str(e))
            return False