import time
from models.mensaje import MensajeModel
from utils.whatsapp import WhatsAppBot

class EnviarMensajeBot:
    def __init__(self):
        self.model = MensajeModel()
        self.whatsapp_bot = WhatsAppBot()

    def enviar_mensajes(self):
        mensaje_texto = self.model.obtener_mensaje()
        cumpleañeros = self.model.obtener_cumpleaños()

        if cumpleañeros:
            print(f"\n¡Hoy es el cumpleaños de {len(cumpleañeros)} persona(s)!")
            for persona in cumpleañeros:
                id_cumpleanero, nombre_cumpleanero, numero_cumpleanero, fecha_nac_cumpleanero = persona
                print(f"Preparando mensaje para {nombre_cumpleanero} ({numero_cumpleanero})...")

                mensaje_personalizado = mensaje_texto.format(nombre=nombre_cumpleanero)
                envio_exitoso = False

                if not self.model.verificar_envio_hoy(id_cumpleanero):
                    envio_exitoso = self.whatsapp_bot.enviar_mensaje(
                        id_cumpleanero, numero_cumpleanero, nombre_cumpleanero, 
                        mensaje_personalizado, self.model
                    )

                if envio_exitoso:
                    print(f"Mensaje enviado a {nombre_cumpleanero}.")
                else:
                    print(f"No se pudo enviar el mensaje a {nombre_cumpleanero}.")

                time.sleep(5)
        else:
            print("No hay cumpleaños hoy. ¡A descansar! 😴")

        print("\nProceso de envío de cumpleaños completado.")

if __name__ == "__main__":
    bot = EnviarMensajeBot()
    bot.enviar_mensajes()