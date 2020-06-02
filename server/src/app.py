# export FLASK_APP=application.py
# export FLASK_ENV=development
from flask import Flask, render_template, request, send_file, send_from_directory, safe_join, make_response
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import time


ITEM_SHEET = 'items'
CLIENT_SHEET = 'clients'
NADIA_SPREAD_SHEET_KEY = "16GRZw98-vJVntIRdVnoMO6UkMOBRwKadeR_CHsK81vE"
CREDS_JSON = 'creds.json'
PARAMS = {
    "horario": "TBD",
    "donde": "TBD",
    "REGISTRO_URL": 'https://forms.gle/cZCpR9cT13Ph4pmx6',
    "portrait": "https://media.giphy.com/media/YOjrhM2KXm28ZsCjli/giphy.gif",
    "TITULO": "Just because it's impossible, doesn't mean we shouldn't try",
    "CALENDARIO": "https://calendar.google.com/calendar?cid=cHU5OXNidmlhZTBhM2ozMnZxcjk4anRhNzRAZ3JvdXAuY2FsZW5kYXIuZ29vZ2xlLmNvbQ",
    "SUBTITULO": "Simon Sinek",
}

app = Flask(__name__)


class element(object):
    def __init__(self, title=None, content=None):
        self.title = title
        self.content = content

    def GetTitle(self):
        return self.title

    def GetContent(self):
        return self.content

    def setTitle(self, other):
        self.title = other

    def setContent(self, other):
        self.content = other

# Posibles fondos que me gusto la tematica de nasa60s
# https://giphy.com/gifs/nasa-nasa60th-nasahistory-pioneer10-6IhNFaHeGIEomc7J8o
# https://giphy.com/gifs/usnationalarchives-moon-nasa-apollo-69mUSKBujnpgmxcqlg
# https://giphy.com/gifs/usnationalarchives-space-nasa-archivesgif-2463mSK5q2P3qLnoDY
# https://giphy.com/gifs/usnationalarchives-space-nasa-archivesgif-9GJcFf6ioJou0sSvFQ
# https://giphy.com/gifs/trippy-red-green-l0CLT1GgrPCw5OIve
# https://giphy.com/gifs/universe-recursive-nietschze-Pk9GRXyCv4r9MDnYjE


class gsheet_helper(object):
    def __init__(self):
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive.file",
            "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name(
            CREDS_JSON, scope)
        self.client = gspread.authorize(creds)
        self.gsheet = self.client.open_by_key(NADIA_SPREAD_SHEET_KEY)

    def get_items(self):
        items = self.get_sheet(ITEM_SHEET)
        return items

    def get_sheet(self, sheet_name):
        sheet = self.gsheet.worksheet(sheet_name)
        items = pd.DataFrame(sheet.get_all_records())
        return items

    def store_user(self, user_dict):
        sheet = self.ghseet.worksheet(CLIENT_SHEET)
        clients = pd.DataFrame(self.get_sheet(CLIENT_SHEET))
        cond = clients[clients["id"] == user_dict["id"]].empty
        if cond:
            sheet.add_rows(1)
            sheet.append_row([element for element in user_dict.values()])
        else:
            print("quedo listocho paporro")


def format_server_time():
    server_time = time.localtime()
    return time.strftime("%I:%M:%S %p", server_time)


@app.route('/')
def index():
    values = PARAMS

    def GetFromSheets():
        TEXT = []
        data = gsheet_helper().get_items()
        for x in data.iterrows():
            try:
                TEXT.append(element(tuple(x)[1][0], tuple(x)[1][1]))
            except:
                pass
        return TEXT

    TEXT = GetFromSheets()
    intro = element(values["TITULO"], values["SUBTITULO"])
    for i in TEXT:
        t = i.GetTitle()
        c = i.GetContent()
        if t == "Horario":
            values["Horario"] = c
        if t == "Donde":
            values["Donde"] = c
        if t == "portrait":
            values["portrait"] = c
        if t == "titulo":
            values["titulo"] = c
        if t == "subtitulo":
            values["subtitulo"] = c

    context = {'server_time': format_server_time()}  # 1
    template = render_template("index.html",  # 2
                               context=context,
                               TEXT=TEXT,
                               url=values["portrait"],
                               intro=intro,
                               Horario=values["Horario"],
                               Donde=values["Donde"],
                               Calendario=values["CALENDARIO"],
                               REGISTRO_URL=values["REGISTRO_URL"])
    response = make_response(template)
    response.headers['Cache-Control'] = 'public, max-age=300, s-maxage=600'
    return response


@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('../../static/js', path)


@app.route('/images/<path:path>')
def send_img(path):
    return send_from_directory('../../static/images', path)


@app.route('/css/<path:path>')
def send_css(path):
    return send_from_directory('../../static/css', path)


@app.route('/songs/<path:path>')
def send_songs(path):
    return send_from_directory('../../static/songs', path)


@app.route('/fonts/<path:path>')
def send_fonts(path):
    return send_from_directory('../../static/fonts', path)
