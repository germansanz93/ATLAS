from flask import Flask, request
import logging
import sys

app = Flask(__name__)

# Configurar logs para que salgan por stdout (importante para K8s)
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

@app.route('/')
def hello():
    """
    Handles the root endpoint, providing a basic health check response.
    """
    logging.info("Peticion recibida en root")
    return "Todo bien por aqui!"

@app.route('/critical-feature')
def critical():
    """
    Handles requests for a critical feature, processing a user ID and a tier for a calculation.
    Expects 'id' and 'tier' as query parameters.
    Returns calculation result or appropriate error message with status code.
    """
    logging.info("Iniciando proceso critico...")
    user_id = request.args.get('id')

    if not user_id:
        logging.warning("No user_id provided for critical feature.")
        return "Falta ID de usuario", 400

    tier_param = request.args.get('tier')
    if not tier_param:
        logging.warning(f"No 'tier' provided for user_id: {user_id}")
        return "Falta parametro 'tier'", 400

    try:
        tier = int(tier_param)
        result = 100 / tier
        logging.info(f"Proceso critico completado para user_id: {user_id} con tier: {tier}. Resultado: {result}")
        return f"Resultado: {result}"
    except ValueError as e:
        logging.error(f"Valor invalido para 'tier' proporcionado para user_id: {user_id}. Valor: {tier_param}. Error: {e}", exc_info=True)
        return "El parametro 'tier' debe ser un numero entero valido", 400
    except ZeroDivisionError as e:
        logging.error(f"Intento de division por cero en calculo de tier para user_id: {user_id} con tier: {tier}. Error: {e}", exc_info=True)
        return "Error en el calculo: division por cero no permitida", 400
    except Exception as e:
        # Captura cualquier otra excepción inesperada para evitar fallos no controlados
        logging.error(f"Excepcion inesperada en calculo de tier para user_id: {user_id} con tier: {tier_param}. Error: {e}", exc_info=True)
        return "Internal Server Error", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)