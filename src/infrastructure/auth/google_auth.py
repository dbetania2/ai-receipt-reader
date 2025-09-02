# google_auth.py esta clase maneja la autenticacion con google

import os
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

class GoogleAuth:
    # el constructor inicializa la clase con la url de autenticacion
    def __init__(self, auth_url: str):
        # estos son los permisos o scopes necesarios
        self.scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive.file",
            "openid",
            "https://www.googleapis.com/auth/userinfo.email"
        ]
        # se obtiene la ruta del archivo de secretos del cliente desde las variables de entorno
        self.client_secrets_file = os.environ.get("CLIENT_SECRETS_FILE")
        self.auth_url = auth_url

    def get_auth_url(self):
        """devuelve la url de autorizacion de google y el estado de la sesion oauth."""
        # se crea el objeto flow para manejar el flujo de autenticacion
        flow = Flow.from_client_secrets_file(
            self.client_secrets_file,
            scopes=self.scopes,
            redirect_uri=f"{self.auth_url}/oauth2callback"
        )
        # se genera la url de autorizacion
        auth_url, state = flow.authorization_url(
            access_type="offline",
            include_granted_scopes="true"
        )
        return auth_url, state

    def exchange_code_for_token(self, code, state):
        """
        intercambia el codigo de autorizacion por credenciales y devuelve (email, creds).
        """
        # se crea un nuevo objeto flow
        flow = Flow.from_client_secrets_file(
            self.client_secrets_file,
            scopes=self.scopes,
            state=state,
            redirect_uri=f"{self.auth_url}/oauth2callback"
        )
        # se intercambia el codigo por un token
        flow.fetch_token(code=code)

        creds = flow.credentials

        # se obtiene el email del usuario usando la api de oauth2
        oauth2_service = build('oauth2', 'v2', credentials=creds)
        user_info = oauth2_service.userinfo().get().execute()
        email = user_info.get('email')

        return email, creds

    def store_user_creds_in_session(self, email, creds, session):
        """guardar credenciales y email en sesion tras login oauth."""
        # se guarda un diccionario con las credenciales en la sesion
        session['user_credentials'] = {
            "email": email,
            "creds": {
                'token': creds.token,
                'refresh_token': creds.refresh_token,
                'token_uri': creds.token_uri,
                'client_id': creds.client_id,
                'client_secret': creds.client_secret,
                'scopes': creds.scopes
            }
        }

    def get_creds_from_session(self, session):
        """reconstruye objeto credentials desde sesion."""
        user_data = session.get('user_credentials')
        if not user_data:
            raise ValueError("no hay credenciales en la sesion. el usuario debe iniciar sesion primero.")
        creds_data = user_data['creds']
        # se crea y devuelve el objeto credentials
        return Credentials(
            token=creds_data['token'],
            refresh_token=creds_data.get('refresh_token'),
            token_uri=creds_data['token_uri'],
            client_id=creds_data['client_id'],
            client_secret=creds_data['client_secret'],
            scopes=creds_data['scopes']
        )