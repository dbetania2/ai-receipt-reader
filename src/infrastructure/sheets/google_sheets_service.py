# google_sheet_service.py esta clase se encarga de interactuar con google sheets para guardar datos

import os
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from ...application.usecases.receipt_processing_result import ReceiptProcessingResult
from .sheet_factory import SheetFactory
from ..db.sqlite_manager import get_spreadsheet_id, set_spreadsheet_id

class GoogleSheetsService:
    # esta clase maneja la logica para guardar datos de recibos en google sheets
    def __init__(self, creds, user_email: str):
        # se inicializa el servicio para un usuario
        # si no hay una hoja, crea una nueva y la guarda en la base de datos
        self.creds = creds
        self.user_email = user_email
        self.range_name = "'Gastos'!A1"

        # se inicializa la fabrica de hojas
        self.sheet_factory = SheetFactory(self.creds)

        # se recupera el id de la hoja de calculo de sqlite
        self.spreadsheet_id = get_spreadsheet_id(self.user_email)
        if not self.spreadsheet_id:
            # se crea una hoja nueva si no existe
            if not self.creds or not self.user_email:
                raise ValueError("no hay credenciales disponibles para crear la hoja del usuario")
            self.spreadsheet_id = self.sheet_factory.create_user_spreadsheet(
                title=f"ticketapp - {self.user_email}"
            )
            # se guarda el nuevo id en la base de datos
            set_spreadsheet_id(self.user_email, self.spreadsheet_id)

        # se inicializa el servicio de sheets
        self.service = build('sheets', 'v4', credentials=self.creds)

    def save_to_sheet(self, result: ReceiptProcessingResult):
        # esta funcion guarda los datos del recibo en la hoja de calculo del usuario
        try:
            # se verifica si la hoja esta vacia para agregar encabezados
            is_sheet_empty = False
            try:
                # se verifica si la celda a1 tiene valores
                result_check = self.service.spreadsheets().values().get(
                    spreadsheetId=self.spreadsheet_id,
                    range="'Gastos'!A1:A1"
                ).execute()
                if 'values' not in result_check:
                    is_sheet_empty = True
            except HttpError as e:
                # se maneja el error si la hoja esta completamente vacia
                if e.resp.status == 400:
                    is_sheet_empty = True
                else:
                    raise

            if is_sheet_empty:
                # se definen los encabezados
                headers = ["fecha", "producto", "cantidad", "precio unitario"]
                header_body = {'values': [headers]}
                # se anaden los encabezados a la hoja
                self.service.spreadsheets().values().append(
                    spreadsheetId=self.spreadsheet_id,
                    range=self.range_name,
                    valueInputOption='USER_ENTERED',
                    body=header_body
                ).execute()

            # se preparan las filas de datos del recibo
            rows = [
                [item.fecha, item.producto, item.cantidad, item.precio]
                for item in result.receipt_data_list
            ]
            # se anade la fila del total
            rows.append(["", "", "total", result.total])

            body = {'values': rows}
            # se anaden los datos del recibo a la hoja
            result_append = self.service.spreadsheets().values().append(
                spreadsheetId=self.spreadsheet_id,
                range=self.range_name,
                valueInputOption='USER_ENTERED',
                insertDataOption='INSERT_ROWS',
                body=body
            ).execute()

            updated_cells = result_append.get('updates', {}).get('updatedCells', 0)
            print(f"{updated_cells} celdas actualizadas")

            # se devuelve el id de la hoja y el numero de celdas actualizadas
            return {
                "spreadsheet_id": self.spreadsheet_id,
                "updated_cells": updated_cells
            }

        except Exception as e:
            # se maneja el error general de escritura en google sheets
            print(f"error al escribir en google sheets: {e}")
            raise
