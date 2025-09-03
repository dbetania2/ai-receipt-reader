# src/infrastructure/sheets/google_sheets_service.py

import os
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from ...application.usecases.receipt_processing_result import ReceiptProcessingResult
from .sheet_factory import SheetFactory
from ..db.sqlite_manager import get_spreadsheet_id, set_spreadsheet_id


class GoogleSheetsService:
    def __init__(self, creds, user_email: str):
        self.creds = creds
        self.user_email = user_email
        self.range_name = "'Gastos'!A1"

        # Inicializamos la factory
        self.sheet_factory = SheetFactory(self.creds)

        # Revisamos si ya existe un spreadsheet para el usuario
        self.spreadsheet_id = get_spreadsheet_id(self.user_email)
        if not self.spreadsheet_id:
            if not self.creds or not self.user_email:
                raise ValueError("No hay credenciales disponibles para crear la hoja del usuario")
            self.spreadsheet_id = self.sheet_factory.create_user_spreadsheet(
                title=f"ticketapp - {self.user_email}"
            )
            set_spreadsheet_id(self.user_email, self.spreadsheet_id)

        self.service = build('sheets', 'v4', credentials=self.creds)

    def save_to_sheet(self, result: ReceiptProcessingResult):
        try:
            # Verificamos si la hoja está vacía
            is_sheet_empty = False
            try:
                result_check = self.service.spreadsheets().values().get(
                    spreadsheetId=self.spreadsheet_id,
                    range="'Gastos'!A1:A1"
                ).execute()
                if 'values' not in result_check:
                    is_sheet_empty = True
            except HttpError as e:
                if e.resp.status == 400:
                    is_sheet_empty = True
                else:
                    raise

            # Si está vacía, escribimos encabezados
            if is_sheet_empty:
                headers = ["fecha", "producto", "cantidad", "precio unitario", "total"]
                header_body = {'values': [headers]}
                self.service.spreadsheets().values().append(
                    spreadsheetId=self.spreadsheet_id,
                    range=self.range_name,
                    valueInputOption='RAW',  # RAW evita interpretación automática
                    body=header_body
                ).execute()

            # Construimos las filas, forzando fecha como texto con ' delante
            rows = [
                [f"'{item.fecha}", item.producto, item.cantidad, f"{item.precio:.2f}", ""]
                for item in result.receipt_data_list
            ]
            # Agregamos la fila del total al final
            rows.append(["", "", "", "", f"{result.total:.2f}"])

            body = {'values': rows}
            result_append = self.service.spreadsheets().values().append(
                spreadsheetId=self.spreadsheet_id,
                range=self.range_name,
                valueInputOption='RAW',  # RAW para mantener el formato
                insertDataOption='INSERT_ROWS',
                body=body
            ).execute()

            updated_cells = result_append.get('updates', {}).get('updatedCells', 0)
            print(f"{updated_cells} celdas actualizadas")

            return {
                "spreadsheet_id": self.spreadsheet_id,
                "updated_cells": updated_cells
            }

        except Exception as e:
            print(f"Error al escribir en Google Sheets: {e}")
            raise
