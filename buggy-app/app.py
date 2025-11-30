from flask import Flask, request
import logging
import sys

app = Flask(__name__)

# Configurar logs para que salgan por stdout (importante para K8s)
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

@app.route('/')
def hello():
    """
    Maneja la ruta raíz del microservicio.
    Registra una petición de información cuando se accede a esta ruta.
    """
    logging.info("Peticion recibida en root")
    return "Todo bien por aqui!"

@app.route('/critical-feature')
def critical():
    """
    Maneja la ruta de una característica crítica que incluye lógica compleja.
    Requiere un 'id' de usuario como parámetro de consulta.
    Simula un cálculo que puede generar un error de división por cero si el 'tier' es 0.
    Maneja errores de 'id' faltante y errores de cálculo, registrándolos y devolviendo respuestas adecuadas.
    """
    logging.info("Iniciando proceso critico...")
    user_id = request.args.get('id')

    if not user_id:
        logging.warning("No user_id provided")
        return "Falta ID", 400

    try:
        # ERROR INTENCIONAL CORREGIDO:
        # El 'tier' se ha ajustado a un valor no cero para evitar ZeroDivisionError.
        # En un escenario real, 'tier' provendría de una fuente dinámica y requeriría validación.
        tier = 1  # Corregido de 0 a 1 para evitar ZeroDivisionError
        result = 100 / tier
        return f"Resultado: {result}"
    except ZeroDivisionError as e:
        # Logueamos el error específico con stacktrace completo
        logging.error("Excepcion critica: Division por cero en el calculo de tier", exc_info=True)
        return "Internal Server Error", 500
    except Exception as e:
        # Capturamos cualquier otra excepcion inesperada
        logging.error(f"Ocurrio un error inesperado en el calculo de tier: {e}", exc_info=True)
        return "Internal Server Error", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
