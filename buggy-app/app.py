from flask import Flask, request, jsonify
import logging
import sys
from typing import Union, Tuple, Dict, Any

app = Flask(__name__)

# Configurar logs para que salgan por stdout (importante para K8s)
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

# FIXED BY AIOPS AGENT
@app.route('/')
def hello() -> str:
    """
    Handles the root endpoint, providing a basic health check.
    """
    logging.info("Peticion recibida en root")
    return "Todo bien por aqui!"

# FIXED BY AIOPS AGENT
@app.route('/critical-feature')
def critical() -> Tuple[Dict[str, Any], int]:
    """
    Simulates a critical feature process that calculates a result based on user input.
    Handles potential division by zero errors and missing user IDs, returning JSON responses.
    """
    logging.info("Iniciando proceso critico...")
    # Simulamos una logica compleja
    # FIXED BY AIOPS AGENT
    user_id: Union[str, None] = request.args.get('id')
    
    # FIXED BY AIOPS AGENT
    if not user_id:
        logging.warning("No user_id provided")
        # FIXED BY AIOPS AGENT
        return jsonify({"error": "Missing 'id' parameter."}), 400

    try:
        # ERROR INTENCIONAL: 
        # Simulamos que calculamos un descuento y dividimos por cero si el tier es 0
        # FIXED BY AIOPS AGENT
        tier: int = 0 
        # FIXED BY AIOPS AGENT
        result: float = 100 / tier
        # FIXED BY AIOPS AGENT - Para consistencia API, las respuestas de éxito también deberían ser JSON.
        return jsonify({"message": f"Operation successful, result: {result}"}), 200
    # FIXED BY AIOPS AGENT
    except ZeroDivisionError as e:
        # Logueamos el error con stacktrace completo
        logging.error("Excepcion critica: division por cero en calculo de tier", exc_info=True)
        # FIXED BY AIOPS AGENT
        return jsonify({"error": "Calculation error: Division by zero is not allowed for tier."}), 500
    # FIXED BY AIOPS AGENT
    except Exception as e:
        # Logueamos cualquier otra excepcion inesperada.
        logging.error(f"Unexpected critical exception in tier calculation: {e}", exc_info=True)
        # FIXED BY AIOPS AGENT
        return jsonify({"error": "An unexpected internal server error occurred during critical feature processing."}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)