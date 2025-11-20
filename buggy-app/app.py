from flask import Flask, request
import logging
import sys

app = Flask(__name__)

# Configurar logs para que salgan por stdout (importante para K8s)
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

@app.route('/')
def hello():
    logging.info("Peticion recibida en root")
    return "Todo bien por aqui!"

@app.route('/critical-feature')
def critical():
    logging.info("Iniciando proceso critico...")
    # Simulamos una logica compleja
    user_id = request.args.get('id')
    
    if not user_id:
        logging.warning("No user_id provided")
        return "Falta ID", 400

    try:
        # ERROR INTENCIONAL: 
        # Simulamos que calculamos un descuento y dividimos por cero si el tier es 0
        tier = 0 
        result = 100 / tier
        return f"Resultado: {result}"
    except Exception as e:
        # Logueamos el error con stacktrace completo
        logging.error("Excepcion critica en calculo de tier", exc_info=True)
        return "Internal Server Error", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)