from flask import jsonify
from flask import request
from pymongo import MongoClient
from bson import ObjectId
import backend.GlobalInfo.Keys as keys
import backend.GlobalInfo.ResponseMessages as ResponseMessage
import datetime

if keys.dbconn==None:
    mongoconect=MongoClient(keys.strConnection)
    keys.dbconn=mongoconect[keys.strDBConnection]
    dbCor=keys.dbconn['coordenadas']
    # dbConfig=keys.dbconn['control_riego']
    # dbHistorial=keys.dbconn['historial_riego']
    
def fnMensaje():
    try:
        arrFinal=[]
        consulta=dbCor.find({})
        listCor=list(consulta)
        if len(listCor)!=0:
            for objCor in listCor:
                objFormateado={
                    "id":str(objCor.get("_id")),
                    "lat":objCor.get("lat"),
                    "long":objCor.get("long"),
                    "temperatura":objCor.get("temperatura"),
                    "pulso":objCor.get("pulso"),
                    "oxigenacion":objCor.get("oxigeno"),
                }
                arrFinal.append(objFormateado)
        objResponse=ResponseMessage.succ200.copy()
        objResponse['Coordenadas']=arrFinal
        return jsonify(objResponse)
    except Exception as e:
        print("Error en fnMensaje",e)
        objResponse=ResponseMessage.err500.copy()
        return jsonify(objResponse)

def fnInsertarCoordenadas(data):
    try:
        # ahora no necesitas volver a pedir el JSON, ya te lo pasan
        campos_requeridos = ['id', 'lat', 'long', 'temperatura', 'pulso', 'oxigeno']
        for campo in campos_requeridos:
            if campo not in data:
                objResponse = ResponseMessage.err400.copy()
                objResponse['message'] = f'Falta el campo: {campo}'
                return jsonify(objResponse), 400

        id_documento = data['id']
        datos_actualizados = {
            "lat": data['lat'],
            "long": data['long'],
            "temperatura": data['temperatura'],
            "pulso": data['pulso'],
            "oxigeno": data['oxigeno'],
            "timestamp": datetime.datetime.now()
        }

        resultado = dbCor.update_one(
            {"_id": ObjectId(id_documento)},
            {"$set": datos_actualizados}
        )

        if resultado.matched_count > 0:
            objResponse = ResponseMessage.succ200.copy()
            objResponse['message'] = "Lectura actualizada correctamente"
            return jsonify(objResponse), 200
        else:
            objResponse = ResponseMessage.err404.copy()
            objResponse['message'] = "No se encontró el documento con ese ID"
            return jsonify(objResponse), 404

    except Exception as e:
        print("Error en fnInsertarCoordenadas:", e)
        objResponse = ResponseMessage.err500.copy()
        objResponse['message'] = 'Error al actualizar lectura'
        return jsonify(objResponse), 500
# def fnMensajeId(id):
#     try:
#         arrFinal=[]
#         consulta=dbUsers.find({"_id":ObjectId(id)})
#         listUsuarios=list(consulta)
#         if len(listUsuarios)!=0:
#             for objUser in listUsuarios:
#                 objFormateado={
#                     "id":str(objUser.get("_id")),
#                     "user":objUser.get("user"),
#                     "email":objUser.get("email"),
#                     "password":objUser.get("password"),
#                 }
#                 arrFinal.append(objFormateado)
#         objResponse=ResponseMessage.succ200.copy()
#         objResponse['Respuesta']=arrFinal
#         return jsonify(objResponse)
#     except Exception as e:
#         print("Error en fnMensaje",e)
#         objResponse=ResponseMessage.err500.copy()
#         return jsonify(objResponse)
    
