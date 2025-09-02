# main_controller.py esta clase de encarga de manejar las rutas y la logica de la api

from flask import Blueprint, jsonify, request, redirect, session, url_for, render_template
import os, uuid

from ..application.usecases.receipt_processing_service import ReceiptProcessingService
from ..infrastructure.auth.google_auth import GoogleAuth
from ..infrastructure.sheets.google_sheets_service import GoogleSheetsService
from ..infrastructure.gemini.gemini_service_impl import GeminiServiceImpl

# se crea el blueprint para organizar las rutas
main_bp = Blueprint('main', __name__, template_folder='../../templates')

# se declaran las dependencias que seran inyectadas desde main.py
main_bp.receipt_processor: ReceiptProcessingService = None
main_bp.google_auth_service: GoogleAuth = None
main_bp.gemini_service: GeminiServiceImpl = None

# diccionario para rastrear el estado de los procesos
process_status = {}

# ruta principal que redirige a la pagina de login
@main_bp.route('/')
def home():
    return redirect(url_for('main.login_page'))

# ruta para la pagina de login
@main_bp.route('/login')
def login_page():
    return render_template("login.html")

# ruta para la pagina de subida de archivos
@main_bp.route('/upload')
def upload_page():
    # se verifica si el usuario esta autenticado
    if 'user_credentials' not in session:
        return redirect(url_for('main.login_page'))
    return render_template("upload.html")

# ruta para iniciar el proceso de autenticacion con google
@main_bp.route('/auth')
def auth():
    # se obtiene la url de autenticacion y el estado
    auth_url, state = main_bp.google_auth_service.get_auth_url()
    session['state'] = state
    return redirect(auth_url)

# ruta de retorno de la autenticacion de google
@main_bp.route('/oauth2callback')
def oauth2callback():
    state = session.get('state')
    code = request.args.get('code')
    # se verifica que el codigo de autorizacion exista
    if not code:
        return "código de autorización faltante", 400

    # se intercambia el codigo por credenciales y se guardan en la sesion
    email, creds = main_bp.google_auth_service.exchange_code_for_token(code, state)
    main_bp.google_auth_service.store_user_creds_in_session(email, creds, session)

    return redirect(url_for('main.upload_page'))

# endpoint para procesar un recibo
@main_bp.route('/api/process', methods=['POST'])
def process_receipt():
    # se verifica que el usuario este autenticado
    if 'user_credentials' not in session:
        return jsonify({"error": "usuario no autenticado"}), 401

    # se genera un id unico para el proceso
    process_id = str(uuid.uuid4())
    process_status[process_id] = "pending"

    # se verifica si el archivo esta en la peticion
    if 'image' not in request.files:
        return jsonify({"error": "no se ha subido ningun archivo"}), 400
    file = request.files['image']
    if file.filename == '':
        return jsonify({"error": "no se ha seleccionado ningun archivo"}), 400

    # se crea un directorio temporal y se guarda el archivo
    temp_path = os.path.join("temp", file.filename)
    os.makedirs("temp", exist_ok=True)
    file.save(temp_path)

    try:
        # ocr y procesamiento del recibo
        raw_text = main_bp.receipt_processor.ocr_service.extract_text(temp_path)
        receipt_data = main_bp.receipt_processor.process_receipt(temp_path)
        process_status[process_id] = "completed"
    except Exception as e:
        process_status[process_id] = "failed"
        return jsonify({"error": str(e)}), 500
    finally:
        # se elimina el archivo temporal
        os.remove(temp_path)

    try:
        # se recuperan las credenciales de la sesion
        creds = main_bp.google_auth_service.get_creds_from_session(session)
        user_email = session['user_credentials']['email']

        # se guarda la informacion en google sheets
        sheets_service = GoogleSheetsService(creds=creds, user_email=user_email)
        result_sheet = sheets_service.save_to_sheet(receipt_data)

        message = "datos guardados en google sheets"
        spreadsheet_id = result_sheet["spreadsheet_id"]

    except Exception as e:
        message = f"datos procesados, pero no se pudieron guardar en sheets: {e}"
        spreadsheet_id = None

    # se devuelve la respuesta en formato json
    return jsonify({
        "process_id": process_id,
        "data": receipt_data,
        "message": message,
        "spreadsheet_id": spreadsheet_id
    })

# endpoint para obtener el estado del procesamiento
@main_bp.route('/api/status/<process_id>')
def get_status(process_id):
    return jsonify({"process_id": process_id, "status": process_status.get(process_id, "not found")})