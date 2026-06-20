import gspread

gc = gspread.service_account(
    filename="credentials.json"
)

spreadsheet = gc.open("Excursiones Meza")

destinos = spreadsheet.worksheet("Destinos")
reservas = spreadsheet.worksheet("Reservas")
pagos = spreadsheet.worksheet("Pagos")


def obtener_destinos():
    return destinos.get_all_records()