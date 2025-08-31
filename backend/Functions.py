from flask import jsonify, request
from pymongo import MongoClient
from bson import ObjectId
import backend.GlobalInfo.Keys as keys
import backend.GlobalInfo.ResponseMessages as ResponseMessage
import datetime
import firebase_admin
from firebase_admin import credentials, messaging

# -------------------- INICIALIZAR FIREBASE ADMIN --------------------
# Usar variable de entorno en Render
firebase_path = os.environ.get("FIREBASE_ADMIN_KEY_PATH", "backend/keys/monitoreogpf-98cb4438dfa9.json")
cred = credentials.Certificate(firebase_path)
firebase_admin.initialize_app(cred)

# -------------------- UMbrales CRÍTICOS --------------------
BPM_MIN = 40
BPM_MAX = 120
TEMP_MIN = 35.0
TEMP_MAX = 41.0

# -------------------- CONEXIÓN A MONGO --------------------
if keys.dbconn is None:
    mongoconect = MongoClient(keys.strConnection)
    keys.dbconn = mongoconect[keys.strDBConnection]

dbCor = keys.dbconn['coordenadas']   # colección de coordenadas
dbFCMTokens = keys.dbconn['fcm_tokens']  # colección de tokens FCM

# -------------------- FUNCIONES FCM --------------------
def send_alert_fcm(tokens, title, body):
    """
    Envía una alerta FCM full-screen a una lista de tokens.
    """
    for token in tokens:
        message = messaging.Message(
            token=token,
            android=messaging.AndroidConfig(
                priority='high',
                notification=messaging.AndroidNotification(
                    channel_id='alert_channel',
                    title=title,
                    body=body,
                    sound='default',
                    click_action='FLUTTER_NOTIFICATION_CLICK',
                    tag='urgent',
                    # Full-screen intent en Android
                    visibility=messaging.AndroidNotificationVisibility.PUBLIC
                )
            )
        )
        try:
            response = messaging.send(message)
            print(f"Alerta enviada a {token}: {title} - {body}")
            print("Respuesta FCM:", response)
        except Exception as e:
            print(f"Error enviando alerta a {token}: {e}")

# -------------------- FUNCIONES PRINCIPALES --------------------
def fnMensaje():
    try:
        arrFinal = []
        consulta = dbCor.find({})
        listCor = list(consulta)

        if len(listCor) != 0:
            # Obtener todos los tokens registrados
            tokens = [doc['token'] for doc in dbFCMTokens.find({})]

            for objCor in listCor:
                temperatura = objCor.get("temperatura")
                pulso = objCor.get("pulso")

                # 🔔 Verificar si hay valores críticos
                alert_triggered = False
                alert_msg = ""

                if pulso is not None and (pulso < BPM_MIN or pulso > BPM_MAX):
                    alert_triggered = True
                    alert_msg += f"Pulso crítico: {pulso} BPM\n"

                if temperatura is not None and (temperatura < TEMP_MIN or temperatura > TEMP_MAX):
                    alert_triggered = True
                    alert_msg += f"Temperatura crítica: {temperatura}°C\n"

                # Enviar notificación FCM si hay alerta y hay tokens
                if alert_triggered and tokens:
                    send_alert_fcm(tokens, "🚨 Alerta Crítica de Animal", alert_msg)

                objFormateado = {
                    "id": str(objCor.get("_id")),
                    "lat": objCor.get("lat"),
                    "long": objCor.get("long"),
                    "temperatura": temperatura,
                    "pulso": pulso,
                    "oxigenacion": objCor.get("oxigeno"),
                }
                arrFinal.append(objFormateado)

        objResponse = ResponseMessage.succ200.copy()
        objResponse['Coordenadas'] = arrFinal
        return jsonify(objResponse)

    except Exception as e:
        print("Error en fnMensaje", e)
        objResponse = ResponseMessage.err500.copy()
        return jsonify(objResponse)

def fnInsertarCoordenadas(data):
    try:
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

def registrar_token_fcm(data):
    """
    Registra un token FCM desde la app Ionic.
    Recibe JSON: { "fcm_token": "TOKEN_DEL_DISPOSITIVO" }
    """
    try:
        token = data.get("fcm_token")
        if not token:
            return jsonify({"status": "error", "message": "Falta fcm_token"}), 400

        # Guardar token si no existe
        if dbFCMTokens.find_one({"token": token}) is None:
            dbFCMTokens.insert_one({"token": token, "timestamp": datetime.datetime.now()})
            return jsonify({"status": "ok", "message": "Token registrado"}), 200
        else:
            return jsonify({"status": "ok", "message": "Token ya registrado"}), 200

    except Exception as e:
        print("Error en registrar_token_fcm:", e)
        return jsonify({"status": "error", "message": "Error al registrar token"}), 500
