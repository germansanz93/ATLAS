from flask import Flask, request
import logging
import sys

app = Flask(__name__)

# Configurar logs para que salgan por stdout (importante para K8s)
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

@app.route('/')
def hello():
    """
    Maneja las solicitudes a la ruta raíz y retorna un mensaje de bienvenida.
    """
    logging.info("Peticion recibida en root")
    return "Todo bien por aqui!"

@app.route('/critical-feature')
def critical_feature():
    """
    Procesa una característica crítica que involucra un cálculo, 
    manejando posibles errores de división por cero o entrada inválida.
    """
    logging.info("Iniciando proceso critico...")
    user_id = request.args.get('id')
    
    if not user_id:
        logging.warning("No user_id provided for critical feature.")
        return "Falta ID", 400

    try:
        # Simulamos que el tier se obtiene de los argumentos y puede ser 0 o inválido
        tier_str = request.args.get('tier', '0') # Default a '0' para simular el error
        tier_value = int(tier_str)
        
        # Simulamos una logica compleja
        result = 100 / tier_value
        return f"Resultado: {result}"
    except ZeroDivisionError as e:
        # Manejo especifico para la division por cero
        logging.error("Excepcion especifica: Division por cero en calculo de tier para user_id %s", user_id, exc_info=True)
        return "Error en calculo: Division por cero no permitida", 400
    except ValueError as e:
        # Manejo especifico para cuando el tier no es un numero valido
        logging.error("Excepcion especifica: El valor de tier '%s' no es un numero valido para user_id %s", tier_str, user_id, exc_info=True)
        return "Error en calculo: El tier debe ser un numero valido", 400
    except Exception as e:
        # Catch-all para cualquier otra excepcion inesperada
        logging.error("Excepcion inesperada en calculo de critical feature para user_id %s", user_id, exc_info=True)
        return "Internal Server Error", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
