import os
import datetime
import random
import sqlite3
import string
import time
from dotenv import load_dotenv
import threading
import binascii

import discord
from discord.ext import commands
from discord import app_commands
from discord import ui

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

load_dotenv('.env')

TOKEN = os.environ['TOKEN']

def convert_to_binary(file_path):
    with open(file_path, 'rb') as file:
        binary_data = file.read()
    return binary_data

def convert_to_image(filename):
    return binascii.unhexlify(filename)

def push_tournament_in_db(t_id, name:str, max_participants:int, datet:str,
                 mode:str, mappa:str, games:int, top_matches:int, iscrizioni_termt:str, lobby:str, cost:int,
                 crossplay:str, kd_limit:int, image: bytes, ps:bool, pc:bool, xbox:bool, team_lenght: int):
    conn = sqlite3.connect('tourneys.sqlite3')
    c = conn.cursor()
    c.execute(f'INSERT INTO tourneys VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
              (int(t_id), name, max_participants,
                datet, mode, mappa, games, top_matches,
                iscrizioni_termt, lobby, cost, crossplay, kd_limit,
                image, ps, pc, xbox, team_lenght))
    conn.commit()
    conn.close()

def generate_random_id(length=9):
    return ''.join([random.choice(string.digits) for n in range(length)])

class IscrizioniViewSolos(ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    @ui.button(label='📩ISCRIVI IL TUO TEAM', style=discord.ButtonStyle.green, custom_id='1')
    async def callback(self, interaction:discord.Interaction, button:ui.Button):
        await interaction.response.send_modal(IscrizioniTeamSolos())

class IscrizioniViewDuos(ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    @ui.button(label='📩ISCRIVI IL TUO TEAM', style=discord.ButtonStyle.green, custom_id='1')
    async def callback(self, interaction:discord.Interaction, button:ui.Button):
        await interaction.response.send_modal(IscrizioniTeamDuos())

class IscrizioniViewTrios(ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    @ui.button(label='📩ISCRIVI IL TUO TEAM', style=discord.ButtonStyle.green, custom_id='1')
    async def callback(self, interaction:discord.Interaction, button:ui.Button):
        await interaction.response.send_modal(IscrizioniTeamTrios())

class IscrizioniViewQuads(ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    @ui.button(label='📩ISCRIVI IL TUO TEAM', style=discord.ButtonStyle.green, custom_id='1')
    async def callback(self, interaction:discord.Interaction, button:ui.Button):
        await interaction.response.send_modal(IscrizioniTeamQuads())

class IscrizioniTeamSolos(ui.Modal, title='Iscrizioni Team'):
    tnome = ui.TextInput(label='Nome team', style=discord.TextStyle.short, max_length=40, row=0,
                         placeholder='Inserisci qui il nome del team')
    tl = ui.TextInput(label='Team Leader', style=discord.TextStyle.long, max_length=1200, row=1,
                         placeholder='Inserisci i dati separati da ", "')
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        conn = sqlite3.connect('tourneys.sqlite3')
        c = conn.cursor()
        team_id = generate_random_id()
        tl_activision = self.tl.value.split(', ')[0]
        tl_name = self.tl.value.split(', ')[1]
        tl = discord.utils.get(interaction.guild.members, name=(tl_name.split('#'))[0],
                               discriminator=(tl_name.split('#'))[1])
        tl_platform = self.tl.value.split(', ')[2]
        tl_link = self.tl.value.split(', ')[3]
        c.execute("SELECT abs(strftime(%s, ?) - strftime('%s', date)) as 'ClosestDate' FROM tourneys ORDER BY abs(strftime(%s, ?)) - strftime('%s', date)) LIMIT 1", 
                  (discord.utils.utcnow(), discord.utils.utcnow()))
        date = c.fetchone()
        c.execute('SELECT * FROM tourneys WHERE date = ?', (date, ))
        tournament = c.fetchone()
        c.execute('INSERT INTO participants VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)',
                  (tl.id, tl_name, tl_platform, 'tl', tl_activision, tl_link, team_id, self.tnome.value, tournament[0]))
        emb = discord.Embed(title='Hai iscritto il tuo team!', description=f'{interaction.user.mention}, hai iscritto i seguenti membri:\n')
        emb.add_field(name='Team Name', value=self.tnome.value)
        emb.add_field(name='Team Leader', value=tl.mention)
        overwrites: dict = {
            interaction.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False)
        }
        channel = await interaction.guild.create_text_channel(f'Clip di {interaction.user.display_name}', overwrites=overwrites)
        await channel.send(f'{interaction.user.mention}, ricorda di pubblicare qui le clip alla fine del torneo!')
        await interaction.edit_original_response(embed=emb)
        conn.commit()
        conn.close()

class IscrizioniTeamDuos(ui.Modal, title='Iscrizioni Team'):
    tnome = ui.TextInput(label='Nome team', style=discord.TextStyle.short, max_length=40, row=0,
                         placeholder='Inserisci qui il nome del team')
    tl = ui.TextInput(label='Team Leader', style=discord.TextStyle.long, max_length=1200, row=1,
                         placeholder='Inserisci i dati separati da ", "')
    tl2 = ui.TextInput(label='Player 2', style=discord.TextStyle.long, max_length=1200, row=2,
                         placeholder='Inserisci i dati separati da ", "')
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        conn = sqlite3.connect('tourneys.sqlite3')
        c = conn.cursor()
        team_id = generate_random_id()
        tl_activision = self.tl.value.split(', ')[0]
        tl_name = self.tl.value.split(', ')[1]
        tl = discord.utils.get(interaction.guild.members, nick=self.tl_name)
        tl_platform = self.tl.value.split(', ')[2]
        tl_link = self.tl.value.split(', ')[3]
        c.execute("SELECT abs(strftime(%s, ?) - strftime('%s', date)) as 'ClosestDate' FROM tourneys ORDER BY abs(strftime(%s, ?)) - strftime('%s', date)) LIMIT 1", 
                  (discord.utils.utcnow(), discord.utils.utcnow()))
        date = c.fetchone()
        c.execute('SELECT * FROM tourneys WHERE date = ?', (date, ))
        tournament = c.fetchone()
        c.execute('INSERT INTO participants VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)',
                  (tl.id, tl_name, tl_platform, 'tl', tl_activision, tl_link, team_id, self.tnome.value, tournament[0]))

        t2_activision = self.tl2.value.split(', ')[0]
        t2_name = self.tl2.value.split(', ')[1]
        t2 = discord.utils.get(interaction.guild.members, nick=self.t2_name)
        t2_platform = self.tl2.value.split(', ')[2]
        t2_link = self.tl2.value.split(', ')[3]
        c.execute('INSERT INTO participants VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)',
                  (t2.id, t2_name, t2_platform, 't2', t2_activision, t2_link, team_id, self.tnome.value, tournament[0]))
        emb = discord.Embed(title='Hai iscritto il tuo team!', description=f'{interaction.user.mention}, hai iscritto i seguenti membri:\n')
        emb.add_field(name='Team Name', value=self.tnome.value)
        emb.add_field(name='Team Leader', value=tl.mention)
        emb.add_field(name='Player 2', value=t2.mention)
        overwrites: dict = {
            interaction.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False)
        }
        channel = await interaction.guild.create_text_channel(f'Clip di {interaction.user.display_name}', overwrites=overwrites)
        await channel.send(f'{interaction.user.mention}, ricorda di pubblicare qui le clip alla fine del torneo!')

        await interaction.edit_original_response(embed=emb)
        conn.commit()
        conn.close()

class IscrizioniTeamTrios(ui.Modal, title='Iscrizioni Team'):
    tnome = ui.TextInput(label='Nome team', style=discord.TextStyle.short, max_length=40, row=0,
                         placeholder='Inserisci qui il nome del team')
    tl = ui.TextInput(label='Team Leader', style=discord.TextStyle.long, max_length=1200, row=1,
                         placeholder='Inserisci i dati separati da ", "')
    tl2 = ui.TextInput(label='Player 2', style=discord.TextStyle.long, max_length=1200, row=2,
                         placeholder='Inserisci i dati separati da ", "')
    tl3 = ui.TextInput(label='Player 3', style=discord.TextStyle.long, max_length=1200, row=3,
                         placeholder='Inserisci i dati separati da ", "')
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        conn = sqlite3.connect('tourneys.sqlite3')
        c = conn.cursor()
        team_id = generate_random_id()
        tl_activision = self.tl.value.split(', ')[0]
        tl_name = self.tl.value.split(', ')[1]
        tl = discord.utils.get(interaction.guild.members, name=(tl_name.split('#'))[0], 
                               discriminator=(tl_name.split('#'))[1])
        tl_platform = self.tl.value.split(', ')[2]
        tl_link = self.tl.value.split(', ')[3]
        c.execute("SELECT abs(strftime(%s, ?) - strftime('%s', date)) as 'ClosestDate' FROM tourneys ORDER BY abs(strftime(%s, ?)) - strftime('%s', date)) LIMIT 1", 
                  (discord.utils.utcnow(), discord.utils.utcnow()))
        date = c.fetchone()
        c.execute('SELECT * FROM tourneys WHERE date = ?', (date, ))
        tournament = c.fetchone()
        c.execute('INSERT INTO participants VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)',
                  (tl.id, tl_name, tl_platform, 'tl', tl_activision, tl_link, team_id, self.tnome.value, tournament[0]))

        t2_activision = self.tl2.value.split(', ')[0]
        t2_name = self.tl2.value.split(', ')[1]
        t2 = discord.utils.get(interaction.guild.members, name=(t2_name.split('#'))[0],
                               discriminator=(t2_name.split('#'))[1])
        t2_platform = self.tl2.value.split(', ')[2]
        t2_link = self.tl2.value.split(', ')[3]
        c.execute('INSERT INTO participants VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)',
                  (t2.id, t2_name, t2_platform, 't2', t2_activision, t2_link, team_id, self.tnome.value, tournament[0]))

        t3_activision = self.tl3.value.split(', ')[0]
        t3_name = self.tl3.value.split(', ')[1]
        t3 = discord.utils.get(interaction.guild.members, name=(t3_name.split('#'))[0],
                               discriminator=(t3_name.split('#'))[1])
        t3_platform = self.tl3.value.split(', ')[2]
        t3_link = self.tl3.value.split(', ')[3]
        c.execute('INSERT INTO participants VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)', 
                  (t3.id, t3_name, t3_platform, 't3', t3_activision, t3_link, team_id, self.tnome.value, tournament[0]))
        emb = discord.Embed(title='Hai iscritto il tuo team!', description=f'{interaction.user.mention}, hai iscritto i seguenti membri:\n')
        emb.add_field(name='Team Name', value=self.tnome.value)
        emb.add_field(name='Team Leader', value=tl.mention)
        emb.add_field(name='Player 2', value=t2.mention)
        emb.add_field(name='Player 3', value=t3.mention)
        overwrites: dict = {
            interaction.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False)
        }
        channel = await interaction.guild.create_text_channel(f'Clip di {interaction.user.display_name}', overwrites=overwrites)
        await channel.send(f'{interaction.user.mention}, ricorda di pubblicare qui le clip alla fine del torneo!')
        await interaction.edit_original_response(embed=emb)
        conn.commit()
        conn.close()

class IscrizioniTeamQuads(ui.Modal, title='Iscrizioni Team'):
    tnome = ui.TextInput(label='Nome team', style=discord.TextStyle.short, max_length=40, row=0,
                         placeholder='Inserisci qui il nome del team')
    tl = ui.TextInput(label='Team Leader', style=discord.TextStyle.long, max_length=1200, row=1,
                         placeholder='Inserisci i dati separati da ", "')
    tl2 = ui.TextInput(label='Player 2', style=discord.TextStyle.long, max_length=1200, row=2,
                         placeholder='Inserisci i dati separati da ", "')
    tl3 = ui.TextInput(label='Player 3', style=discord.TextStyle.long, max_length=1200, row=3,
                         placeholder='Inserisci i dati separati da ", "')
    tl4 = ui.TextInput(label='Player 4', style=discord.TextStyle.long, max_length=1200, row=4,
                         placeholder='Inserisci i dati separati da ", "')
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        conn = sqlite3.connect('tourneys.sqlite3')
        c = conn.cursor()
        team_id = generate_random_id()
        tl_activision = self.tl.value.split(', ')[0]
        tl_name = self.tl.value.split(', ')[1]
        tl = discord.utils.get(interaction.guild.members, name=(tl_name.split('#'))[0], 
                               discriminator=(tl_name.split('#'))[1])
        tl_platform = self.tl.value.split(', ')[2]
        tl_link = self.tl.value.split(', ')[3]
        c.execute("SELECT abs(strftime(%s, ?) - strftime('%s', date)) as 'ClosestDate' FROM tourneys ORDER BY abs(strftime(%s, ?)) - strftime('%s', date)) LIMIT 1", 
                  (discord.utils.utcnow(), discord.utils.utcnow()))
        date = c.fetchone()
        c.execute('SELECT * FROM tourneys WHERE date = ?', (date, ))
        tournament = c.fetchone()
        c.execute('INSERT INTO participants VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)', 
                  (tl.id, tl_name, tl_platform, 'tl', tl_activision, tl_link, team_id, self.tnome.value, tournament[0]))

        t2_activision = self.tl2.value.split(', ')[0]
        t2_name = self.tl2.value.split(', ')[1]
        t2 = discord.utils.get(interaction.guild.members, name=(t2_name.split('#'))[0], 
                               discriminator=(t2_name.split('#'))[1])
        t2_platform = self.tl2.value.split(', ')[2]
        t2_link = self.tl2.value.split(', ')[3]
        c.execute('INSERT INTO participants VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)', 
                  (t2.id, t2_name, t2_platform, 't2', t2_activision, t2_link, team_id, self.tnome.value, tournament[0]))

        t3_activision = self.tl3.value.split(', ')[0]
        t3_name = self.tl3.value.split(', ')[1]
        t3 = discord.utils.get(interaction.guild.members, name=(t3_name.split('#'))[0], 
                               discriminator=(t3_name.split('#'))[1])
        t3_platform = self.tl3.value.split(', ')[2]
        t3_link = self.tl3.value.split(', ')[3]
        c.execute('INSERT INTO participants VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)', 
                  (t3.id, t3_name, t3_platform, 't3', t3_activision, t3_link, team_id, self.tnome.value, tournament[0]))

        t4_activision = self.tl4.value.split(', ')[0]
        t4_name = self.tl4.value.split(', ')[1]
        t4 = discord.utils.get(interaction.guild.members, name=(t4_name.split('#'))[0], 
                               discriminator=(t4_name.split('#'))[1])
        t4_platform = self.tl4.value.split(', ')[2]
        t4_link = self.tl4.value.split(', ')[3]
        c.execute('INSERT INTO participants VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)', 
                  (t4.id, t4_name, t4_platform, 't4', t4_activision, t4_link, team_id, self.tnome.value, tournament[0]))
        emb = discord.Embed(title='Hai iscritto il tuo team!', description=f'{interaction.user.mention}, hai iscritto i seguenti membri:\n')
        emb.add_field(name='Team Name', value=self.tnome.value)
        emb.add_field(name='Team Leader', value=tl.mention)
        emb.add_field(name='Player 2', value=t2.mention)
        emb.add_field(name='Player 3', value=t3.mention)
        emb.add_field(name='Player 4', value=t4.mention)

        overwrites: dict = {
            interaction.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False)
        }
        channel = await interaction.guild.create_text_channel(f'Clip di {interaction.user.display_name}', overwrites=overwrites)
        await channel.send(f'{interaction.user.mention}, ricorda di pubblicare qui le clip alla fine del torneo!')

        await interaction.edit_original_response(embed=emb)
        conn.commit()
        conn.close()


class Bot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='!', intents=discord.Intents.all())

    async def on_ready(self):
        print('Il bot è online!')
        synced = await bot.tree.sync()
        print(f'Comandi sincronizzati: {len(synced)}')
        conn = sqlite3.connect('tourneys.sqlite3')
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS tourneys (id INTEGER PRIMARY KEY,
                    name TEXT, max_participants INTEGER, date DATETIME, mode TEXT, map TEXT, games INTEGER,
                    top_matches INTEGER, iscrizioni_term DATETIME, lobby TEXT, cost INTEGER, crossplay TEXT,
                    kd_limit INTEGER, image BLOB, ps BOOLEAN, xbox BOOLEAN, pc BOOLEAN, team_lenght INTEGER)''')
        c.execute('''CREATE TABLE IF NOT EXISTS participants (id INTEGER PRIMARY KEY, name TEXT, platform TEXT,
        type INTEGER, activision TEXT, link TEXT, team_id INTEGER, team_name TEXT, tournament_id INTEGER, FOREIGN KEY(tournament_id) REFERENCES tourneys(id))
        ''')
        conn.commit()
        conn.close()
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.competing, name=f' UpGaming'))

    async def setup_hook(self):
        self.add_view(IscrizioniViewSolos())
        self.add_view(IscrizioniViewDuos())
        self.add_view(IscrizioniViewTrios())
        self.add_view(IscrizioniViewQuads())

bot = Bot()

@bot.tree.command(name='create', description='Crea un nuovo torneo')
@app_commands.describe(name='Il nome del torneo', max_participants='Numero massimo di partecipanti',
                       date='Data del torneo(hh:mm:dd:MM:yyyy)', mode='Modalità del torneo',
                       mappa='Mappa del torneo', games='Partite da giocare',
                       top_matches='Alla meglio di quante partite',
                       iscrizioni_term='Data termine iscrizioni(hh:mm:dd:MM:yyyy)',
                        lobby='Lobby(privata o pubblica)', cost='Costo di iscrizione al torneo',
                        crossplay='Attivato/disattivato', kd_limit='Limite rapporto kills/deaths',
                       image='Immagine del torneo', ps='Playstation(True/False)', pc='Pc(True/False)',
                       xbox='Xbox(True/False)', team_lenght='Solos, Duos, Trios, Quads')
@app_commands.choices(team_lenght=[app_commands.Choice(name='Solos', value=1),
                               app_commands.Choice(name='Duos', value=2),
                               app_commands.Choice(name='Trios', value=3),
                               app_commands.Choice(name='Quads', value=4)])
async def create(interaction:discord.Interaction, name:str, max_participants:int, date:str,
                 mode:str, mappa:str, games:int, top_matches:int, iscrizioni_term:str, lobby:str, cost:int,
                 crossplay:str, kd_limit:int, image:discord.Attachment, ps:bool=True, pc:bool=True, xbox:bool=True, team_lenght:app_commands.Choice[int]=4):
    datet = datetime.datetime(year=int((date.split(':'))[4]), month=int((date.split(':'))[3]),
                             day=int((date.split(':'))[2]), hour=int((date.split(':'))[0]),
                             minute=int((date.split(':'))[1]), second=0)
    iscrizioni_termt = datetime.datetime(year=int((iscrizioni_term.split(':'))[4]), month=int((iscrizioni_term.split(':'))[3]), 
                             day=int((iscrizioni_term.split(':'))[2]), hour=int((iscrizioni_term.split(':'))[0]),
                             minute=int((iscrizioni_term.split(':'))[1]), second=0)
    if datet <= datetime.datetime.now() or iscrizioni_termt <= datetime.datetime.now():
        await interaction.response.send_message('Inserisci una data futura.')
    conn = sqlite3.connect('tourneys.sqlite3')
    c = conn.cursor()
    t_id = generate_random_id()
    team_lenght = team_lenght.value
    await image.save(f'static\\images\\{image.filename}')
    push_tournament_in_db(int(t_id), name, max_participants, datet, mode, mappa, games, top_matches,
                        iscrizioni_termt, lobby, cost, crossplay, kd_limit,
                        convert_to_binary(f'static\\images\\{image.filename}'), ps, pc, xbox, team_lenght)
    c.execute(f'SELECT * FROM tourneys WHERE id = ?', (t_id, ))
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
    rule = discord.utils.get(interaction.guild.channels, id=1106669633827766324)
    emb.add_field(name='Regolamento', value=rule.mention)
    emb.add_field(name='Termine iscrizioni il ', value=t[8])
    emb.add_field(name='Lobby', value=t[9])
    emb.set_footer(text='👉Seguimi su IG per rimanere aggiornato sui nostri tornei😉👍', icon_url=interaction.user.avatar.url)
    emb.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)
    image_url = image.url
    emb.set_image(url=image_url)
    view=ui.View()
    iscriviti = ui.Button(label='📩ISCRIVITI ORA!', url='https://discord.com/channels/1039308063322153060/1099245120081104956', style=discord.ButtonStyle.url)
    btn = ui.Button(label='IG Scission_Tv', url='https://www.instagram.com/scission_tv/', style=discord.ButtonStyle.url)
    btn2 = ui.Button(label='IG UpGamingItalia', url='https://www.instagram.com/upgamingitalia/', style=discord.ButtonStyle.url)
    view.add_item(iscriviti)
    view.add_item(btn)
    view.add_item(btn2)
    conn.commit()
    conn.close()
    await interaction.response.send_message('Mandato!', ephemeral=True, delete_after=1) 
    await interaction.channel.send(embed=emb, view=view)


@bot.tree.command(name='iscrizioni', description='Manda un bottone per accedere alle iscrizioni team')
@app_commands.describe(nome='Il nome del torneo')
async def iscrizioni(interaction: discord.Interaction, nome:str):
    conn = sqlite3.connect('tourneys.sqlite3')
    c = conn.cursor()
    c.execute('SELECT * FROM tourneys WHERE name = ?', (nome, ))
    torneo = c.fetchone()
    if torneo is None:
        await interaction.response.send_message('Il torneo non esiste.')
    else:
        emb = discord.Embed(title='Iscrizioni Team',
                            description='''Clicca il bottone qui sotto per iscrivere il tuo team.\n
                             Dovrai inserire i dati nel seguente formato:\n **Nome team:** <nome_team>\n
                                **Team Leader:** <nome_activision>, <nome_discord>#<discriminatore>, <piattaforma>, <link_live>\n
                                **Player 2:** <nome_activision>, <nome_discord>#<discriminatore>, <piattaforma>, <link_live>\n
                                **Player 3:** <nome_activision>, <nome_discord>#<discriminatore>, <piattaforma>, <link_live>\n
                                **Player 4:** <nome_activision>, <nome_discord>#<discriminatore>, <piattaforma>, <link_live>\n
                                **ATTENZIONE: Se non inserisci i dati correttamente essi potrebbero non essere conservati correttamente.**''')
        if torneo[-1] == 1:
            view = IscrizioniViewSolos()
        elif torneo[-1] == 2:
            view = IscrizioniViewDuos()
        elif torneo[-1] == 3:
            view = IscrizioniViewTrios()
        elif torneo[-1] == 4:
            view = IscrizioniViewQuads()
        else:
            view = view
        def disattiva_iscrizioni():
            for child in view.children:
                child.disabled = True
            return
        now = datetime.datetime.now()
        run_at = now + datetime.timedelta(days=(time.strptime(torneo[8], '%Y-%m-%dT%H:%M')).tm_mday - now.day,
                                        hours=(time.strptime(torneo[8], '%Y-%m-%dT%H:%M').tm_hour) - now.hour,
                                        minutes=(time.strptime(torneo[8], '%Y-%m-%dT%H:%M').tm_min) - now.minute,
                                        seconds=(time.strptime(torneo[8], '%Y-%m-%dT%H:%M').tm_sec) - now.second)
        threading.Timer(run_at, disattiva_iscrizioni).start()
        await interaction.response.send_message(embed=emb, view=view)

if __name__ == '__main__':
    bot.run(TOKEN)
