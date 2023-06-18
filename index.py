import os
import sqlite3
import threading
import asyncio

import quart
from quart import Quart, render_template, redirect, request, flash, url_for
from quart.wrappers import Response
from werkzeug.utils import secure_filename
import discord

from main import (
    push_tournament_in_db, generate_random_id, convert_to_binary, convert_to_image,
    bot, TOKEN
)

UPLOAD_FOLDER = 'static\\images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'bmp'}

app = Quart(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = b'\x9a\xa4#\x19Ir&\xfc\xc3\xf2!v\xbb\x8f\x07\x80'

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def send_tournament_wrapper(t_id, cost, kd_limit, crossplay, filename):
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    task = loop.create_task(send_tournament(t_id, cost, kd_limit, crossplay, filename))
    if not loop.is_running():
        loop.run_until_complete(task)

def send_message_wrapper(channel, emb, view, file):
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    task = loop.create_task(channel.send(embed=emb, view=view, file=file))
    if not loop.is_running():
        loop.run_until_complete(task)

async def send_tournament(t_id, cost, kd_limit, crossplay, filename):
    conn = sqlite3.connect('tourneys.sqlite3')
    c = conn.cursor()
    c.execute('SELECT * FROM tourneys WHERE id = ?', (t_id,))
    t = c.fetchone()
    emb = discord.Embed(title=t[1], description='Nuovo torneo. Ecco i dettagli:\n')
    emb.add_field(name='Partecipanti massimi', value=t[2])
    emb.add_field(name='Si svolgerà il ', value=t[3])
    emb.add_field(name='Modalità', value=t[4])
    emb.add_field(name='Mappa', value=t[5])
    emb.add_field(name='Costo Iscrizione', value='Gratuito' if cost == 0 else t[10])
    emb.add_field(name='Games', value=t[6])
    emb.add_field(name='Top matches', value=t[7])
    emb.add_field(name='KD Limit', value=kd_limit if kd_limit != 0 else 'Nessun limite')
    emb.add_field(name='Crossplay', value=crossplay)
    guild = bot.get_guild(1039308063322153060)
    rule = discord.utils.get(guild.channels, id=1106669633827766324)
    emb.add_field(name='Regolamento', value=rule.mention)
    emb.add_field(name='Termine iscrizioni il ', value=t[8])
    emb.add_field(name='Lobby', value=t[9])
    user = discord.utils.get(guild.members, id=738924916036075982)
    emb.set_footer(text='👉Seguimi su IG per rimanere aggiornato sui nostri tornei😉👍', icon_url=user.avatar.url)
    emb.set_author(name=user.name, icon_url=user.avatar.url)
    file_ = discord.File(f'static/images/{filename}')
    emb.set_image(url=f'attachment://{filename}')
    view = discord.ui.View()
    iscriviti = discord.ui.Button(label='📩ISCRIVITI ORA!', url='https://discord.com/channels/1039308063322153060/1099245120081104956', style=discord.ButtonStyle.url)
    btn = discord.ui.Button(label='IG Scission_Tv', url='https://www.instagram.com/scission_tv/', style=discord.ButtonStyle.url)
    btn2 = discord.ui.Button(label='IG UpGamingItalia', url='https://www.instagram.com/upgamingitalia/', style=discord.ButtonStyle.url)
    view.add_item(iscriviti)
    view.add_item(btn)
    view.add_item(btn2)
    conn.commit()
    conn.close()
    channel = discord.utils.get(guild.channels, id=1118092464075575377)
    send_message_wrapper(channel, emb, view, file_)


@app.after_request
async def add_header(response: Response) -> Response:
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response

@app.route('/')
async def index() -> str:
    return await render_template('index.html')

@app.route('/invite')
async def invite() -> Response:
    return await redirect('https://discord.com/api/oauth2/authorize?client_id=1102296092332281907&permissions=17602924750928&scope=bot%20applications.commands')

@app.route('/crea', methods=['GET', 'POST'])
async def crea() -> Response:
    if request.method == 'POST':
        error = None
        if 'image' not in await request.files:
            error = 'Nessun\'immagine'
            print(error)
            return await quart.redirect(await quart.url_for('crea'), error=error)
        files = await request.files
        img = files['image']
        if img.filename == '':
            error = 'Nessun file selezionato'
            print(error)
            return await quart.redirect(await quart.url_for('crea'), error=error)
        if img and allowed_file(img.filename):
            filename = secure_filename(img.filename)
            upload_folder = os.path.abspath(app.config['UPLOAD_FOLDER'])
            await img.save(os.path.join('static\\images', filename))
            path = os.path.join('static\\images', filename)
        for key, value in (await request.form).items():
            if value.strip() == '':
                error = 'Non hai inserito tutti i dati!'
                print(error)
                return await render_template('crea.html', error=error)
        form = await request.form
        nome = form.get('nome')
        partecipanti = int(form.get('partecipanti'))
        mappa = form.get('mappa')
        mode = form.get('mode')
        data = form.get('data')
        lobby = form.get('lobby')
        modef = form.get('modef')
        iscrizione: int = form.get('iscrizione')
        matches: int = form.get('matches')
        topmatches = form.get('topmatches')
        kdlimit = form.get('kdlimit')
        crossplay = form.get('crossplay')
        iscrizionitermt = form.get('iscrizionitermt')
        image_binary = convert_to_binary(path)
        team_lenght = int(form.get('team_lenght'))
        platforms = form.getlist('platforms')
        ps = True if len(platforms) >= 1 and platforms[0] else False
        pc = True if len(platforms) >= 2 and platforms[1] else False
        xbox = True if len(platforms) >= 3 and platforms[2] else False
        if team_lenght < 1 or team_lenght > 4:
            error = 'La lunghezza del team deve essere compresa tra 1 e 4'
            print(error)
            return await render_template('crea.html', error=error)
        t_id = int(generate_random_id())
        push_tournament_in_db(t_id, nome, partecipanti, data, mode, mappa, matches, topmatches, iscrizionitermt,
                              lobby, iscrizione, crossplay, kdlimit, image_binary, ps, pc, xbox, team_lenght)
        await flash('Torneo creato correttamente')
        if error is None:
            send_tournament_wrapper(t_id, iscrizione, kdlimit, crossplay, filename)
            return quart.redirect(quart.url_for('result', nome=nome, partecipanti=partecipanti,
                                                mappa=mappa, mode=mode,
                                                data=data, lobby=lobby, modef=modef,
                                                iscrizione=iscrizione, matches=matches, topmatches=topmatches,
                                                kdlimit=kdlimit, crossplay=crossplay, filename=filename,
                                                playstation=ps, xbox=xbox, pc=pc), code=307)
        else:
            await render_template('crea.html', errors=error)
    elif request.method == 'GET':
        return await render_template('crea.html')

@app.route('/result', methods=['GET', 'POST'])
async def result() -> Response:
    nome = request.args.get('nome')
    partecipanti = request.args.get('partecipanti')
    mappa = request.args.get('mappa')
    mode = request.args.get('mode')
    data = request.args.get('data')
    lobby = request.args.get('lobby')
    modef = request.args.get('modef')
    iscrizione = request.args.get('iscrizione')
    matches = request.args.get('matches')
    topmatches = request.args.get('topmatches')
    kdlimit = request.args.get('kdlimit')
    crossplay = request.args.get('crossplay')
    filename = request.args.get('filename')
    ps = request.args.get('playstation')
    xbox = request.args.get('xbox')
    pc = request.args.get('pc')
    return await render_template('result.html', nome=nome, partecipanti=partecipanti,
                                 mappa=mappa, mode=mode,
                                 data=data, lobby=lobby, modef=modef,
                                 iscrizione=iscrizione, matches=matches,
                                 topmatches=topmatches, kdlimit=kdlimit,
                                 crossplay=crossplay, filename=filename,
                                 playstation=ps, xbox=xbox,
                                 pc=pc)

def run_bot():
    bot.run(TOKEN)

if __name__ == '__main__':
    bot_thread = threading.Thread(target=run_bot).start()
    app.run(debug=True)
