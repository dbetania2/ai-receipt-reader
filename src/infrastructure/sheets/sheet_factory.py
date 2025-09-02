# sheet_factory.py esta clase se encarga de crear hojas de calculo en google sheets

from googleapiclient.discovery import build

class SheetFactory:
    def __init__(self, creds):
        """
        inicializa la fabrica con credenciales de google sheets/drive
        """
        self.creds = creds
        # se construye el servicio de sheets
        self.service = build("sheets", "v4", credentials=self.creds)

    def create_user_spreadsheet(self, title="ticketapp"):
        """
        crea una nueva hoja en el drive del usuario autenticado
        agrega una hoja llamada 'gastos' y encabezados iniciales
        devuelve el spreadsheetid
        """
        # se crea el cuerpo para la nueva hoja
        body = {
            "properties": {"title": title},
            "sheets": [{"properties": {"title": "gastos"}}]
        }
        # se envia la peticion para crear la hoja
        resp = self.service.spreadsheets().create(body=body).execute()
        spreadsheet_id = resp["spreadsheetId"]

        # se definen los encabezados iniciales
        headers = [["fecha", "producto", "cantidad", "precio unitario", "total (fila al final)"]]
        # se anaden los encabezados a la hoja
        self.service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range="'gastos'!a1",
            valueInputOption="USER_ENTERED",
            body={"values": headers}
        ).execute()

        return spreadsheet_id