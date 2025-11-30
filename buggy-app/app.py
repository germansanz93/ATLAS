from flask import Flask, request
import logging
import sys

app = Flask(__name__)

# Configurar logs para que salgan por stdout (importante para K8s)
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

@app.route('/')
def hello():
    """
    Handles the root endpoint, returning a simple health check message.
    """
    logging.info("Peticion recibida en root")
    return "Todo bien por aqui!"

@app.route('/critical-feature')
def critical():
    """
    Processes a critical feature request, simulating a complex calculation.
    It expects a 'user_id' query parameter and handles a simulated division by zero gracefully.
    """
    logging.info("Iniciando proceso critico...")
    user_id = request.args.get('id')
    
    if not user_id:
        logging.warning("No user_id provided for critical feature.")
        return "Falta ID de usuario", 400

    try:
        # ERROR INTENCIONAL original: 
        # Simulamos que calculamos un descuento y dividimos por cero si el tier es 0
        tier_value = 0 # Mantiene la simulación del 'tier' siendo 0, usando snake_case
        
        # FIX: Añadimos una validación para el caso de división por cero.
        # Esto previene que se lance un ZeroDivisionError para este escenario conocido
        # y evita la generación de un log de ERROR innecesario.
        if tier_value == 0:
            logging.warning("Intento de división por cero: el valor de tier es 0. Devolviendo 400.")
            return "El tier no puede ser cero para este cálculo", 400
            
        result_calculation = 100 / tier_value # Variable renombrada a snake_case
        return f"Resultado: {result_calculation}"
    # FIX: Manejamos ZeroDivisionError específicamente como fallback
    # por si la validación anterior falla o el 'tier_value' cambia dinámicamente.
    except ZeroDivisionError as e:
        logging.error(f"Excepción crítica inesperada de división por cero en cálculo de tier: {e}", exc_info=True)
        return "Internal Server Error", 500
    # FIX: Se mantiene un bloque catch de Exception general para cualquier otro error no previsto,
    # pero diferenciado del ZeroDivisionError esperado.
    except Exception as e:
        logging.error(f"Excepción crítica general en cálculo de tier: {e}", exc_info=True)
        return "Internal Server Error", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
