from flask import Flask, request
import logging
import sys

app = Flask(__name__)

# Configurar logs para que salgan por stdout (importante para K8s)
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

@app.route('/')
def hello():
    """
    Handles the root endpoint, returning a simple status message.
    """
    logging.info("Peticion recibida en root")
    return "Todo bien por aqui!"

@app.route('/critical-feature')
def critical():
    """
    Handles a critical feature request, simulating a complex calculation.
    Expects 'id' and 'tier' as query parameters.
    Returns a calculated result or an error message.
    """
    logging.info("Iniciando proceso critico...")
    user_id = request.args.get('id')
    
    if not user_id:
        logging.warning("No user_id provided for critical feature.")
        return "Falta ID de usuario", 400

    tier_str = request.args.get('tier')
    if not tier_str:
        logging.warning("No tier provided for critical feature.")
        return "Falta el valor de 'tier'", 400

    try:
        tier = int(tier_str)
    except ValueError:
        logging.warning(f"Invalid tier value provided: '{tier_str}'. Cannot convert to integer.")
        return "Valor de 'tier' inválido. Debe ser un número entero.", 400

    # Explicitly handle division by zero before calculation
    if tier == 0:
        logging.warning("Tier value is 0, division by zero prevented.")
        return "El valor de 'tier' no puede ser cero para el cálculo.", 400

    try:
        # Simulate complex logic
        result = 100 / tier
        logging.info(f"Proceso critico completado para user_id: {user_id}, tier: {tier}. Resultado: {result}")
        return f"Resultado: {result}", 200
    except ZeroDivisionError:
        # This block should ideally not be hit due to the 'if tier == 0' check,
        # but is kept for robustness and specific exception handling.
        logging.error("Unhandled ZeroDivisionError in critical feature. This should have been caught earlier.", exc_info=True)
        return "Error interno del servidor: división por cero inesperada.", 500
    except Exception as e:
        # Catch any other unforeseen exceptions
        logging.error(f"Excepcion critica inesperada en calculo de tier para user_id: {user_id}", exc_info=True)
        return "Error interno del servidor.", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
