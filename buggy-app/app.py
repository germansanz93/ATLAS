from flask import Flask, request, jsonify
import logging
import sys
from typing import Union, Tuple, Dict, Any

app = Flask(__name__)

# Configurar logs para que salgan por stdout (importante para K8s)
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

@app.route('/')
# FIXED BY AIOPS AGENT
def hello() -> Tuple[str, int]:
    """
    Handles requests to the root endpoint.
    Logs the reception of the request and returns a success message.
    """
    logging.info("Peticion recibida en root")
    return "Todo bien por aqui!", 200 # Explicitly return 200 OK for clarity

@app.route('/critical-feature')
# FIXED BY AIOPS AGENT
def critical() -> Tuple[Dict[str, Any], int]:
    """
    Handles requests to the critical feature endpoint.
    Processes user ID and an optional 'tier' parameter to simulate a complex calculation
    that may lead to a division by zero error.
    Validates inputs and handles specific errors, returning JSON responses as per API guidelines.
    """
    logging.info("Iniciando proceso critico...")

    # FIXED BY AIOPS AGENT
    # 3. Seguridad: Valida siempre los inputs antes de procesarlos.
    # 1. Tipado: Usa Type Hints de Python.
    user_id: Union[str, None] = request.args.get('id')
    tier_str: Union[str, None] = request.args.get('tier')

    if not user_id:
        logging.warning("No user_id provided for critical feature request.")
        # FIXED BY AIOPS AGENT
        # 2. Gestión de Errores: Devuelve mensajes de error en formato JSON, no texto plano.
        return jsonify({"error": "Missing 'id' parameter. Please provide a user ID."}), 400

    tier: int
    if tier_str is None:
        # FIXED BY AIOPS AGENT
        # If 'tier' is not provided, default to 0 to simulate the intended ZeroDivisionError scenario
        # as per the original problem description's intent.
        tier = 0
        logging.info("No 'tier' parameter provided, defaulting to 0 for simulation.")
    else:
        try:
            # FIXED BY AIOPS AGENT
            # Validate 'tier' input type.
            tier = int(tier_str)
        except ValueError:
            logging.warning(f"Invalid 'tier' parameter received: '{tier_str}'. Expected an integer.")
            # FIXED BY AIOPS AGENT
            # 2. Gestión de Errores: Devuelve mensajes de error en formato JSON, no texto plano.
            return jsonify({"error": f"Invalid 'tier' parameter. Must be an integer. Received '{tier_str}'."}), 400

    try:
        # Simulamos una logica compleja, donde 'tier' podría ser 0.
        result = 100 / tier
        # FIXED BY AIOPS AGENT
        # API success responses should also be JSON for consistency.
        return jsonify({"message": f"Calculation successful. Result: {result}", "user_id": user_id, "tier_used": tier}), 200
    # FIXED BY AIOPS AGENT
    # 2. Gestión de Errores: No uses try/except genéricos (Exception) si puedes capturar el error específico.
    # Capturamos el error específico ZeroDivisionError.
    except ZeroDivisionError as e:
        logging.error(f"Critical calculation error: Division by zero attempted with tier={tier} for user_id={user_id}.", exc_info=True)
        # FIXED BY AIOPS AGENT
        # 2. Gestión de Errores: Devuelve mensajes de error en formato JSON, no texto plano.
        return jsonify({"error": "Calculation failed: Division by zero is not allowed.", "details": str(e), "user_id": user_id, "tier_attempted": tier}), 400
    # FIXED BY AIOPS AGENT
    # Captura cualquier otra excepción inesperada como último recurso para mayor robustez.
    except Exception as e:
        logging.error(f"An unexpected internal server error occurred in critical feature for user_id={user_id}.", exc_info=True)
        # FIXED BY AIOPS AGENT
        # 2. Gestión de Errores: Devuelve mensajes de error en formato JSON, no texto plano.
        return jsonify({"error": "An unexpected internal server error occurred.", "details": str(e), "user_id": user_id}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
