from flask import Flask,jsonify,request
from flask_cors import CORS, cross_origin

import backend.Functions as CallMethood
import backend.GlobalInfo.ResponseMessages as ResponseMessage

app = Flask(__name__)
CORS(app, resources={r"/*":{"origins":"*"}})

@app.route("/mensaje", methods= ['GET'])
@cross_origin(allow_headers=['Content_Type'])
def mensaje():
    try:
        objResult=CallMethood.fnMensaje()
        return objResult
    except Exception as e:
        print("Error en mensaje", e)
        return jsonify(ResponseMessage.err500)
    
@app.route('/coordenadas/<id>', methods=['PUT'])
@cross_origin(allow_headers=['Content-Type'])
def actualizar_coordenadas(id):
    try:
        # Tomamos el JSON enviado y lo inyectamos junto con el ID
        data = request.get_json()
        data['id'] = id  # Aseguramos que el ID vaya en el diccionario

        # Llamamos la función que realiza la actualización
        return CallMethood.fnInsertarCoordenadas(data)
    except Exception as e:
        print("Error en actualizar_coordenadas:", e)
        return jsonify(ResponseMessage.err500), 500

@app.route("/registrar-token", methods=["POST"])
@cross_origin(allow_headers=['Content-Type'])
def registrar_token():
    try:
        # Llama a la función del backend que maneja el registro
        return CallMethood.registrar_token_fcm(request.json)
    except Exception as e:
        print("Error en registrar_token:", e)
        return jsonify(ResponseMessage.err500), 500

# app.run(host="0.0.0.0",port=5000,debug=True,threaded=True)