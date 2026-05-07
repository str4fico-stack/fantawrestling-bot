import json
import os

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes
)

# TOKEN TELEGRAM
TOKEN = '8755768030:AAGK9YAsiqSQcQNjEeApR8F-95uyhuYtl2U'

# ADMIN TELEGRAM
# SOSTITUISCI CON IL TUO ID TELEGRAM
ADMIN_IDS = [

    5802394692  #Matteo
    1621756331  #Ciro

]

# FILE CLASSIFICA
CLASSIFICA_FILE = "classifica.json"

# CARICA CLASSIFICA
def carica_classifica():

    if os.path.exists(CLASSIFICA_FILE):

        with open(CLASSIFICA_FILE, "r") as file:

            return json.load(file)

    return {}

# SALVA CLASSIFICA
def salva_classifica():

    with open(CLASSIFICA_FILE, "w") as file:

        json.dump(classifica, file)

# CLASSIFICA PERMANENTE
classifica = carica_classifica()

# MATCH DISPONIBILI
matches = {

    "1": {
        "nome": "Cody vs Roman",
        "domanda1": "Chi vince?",
        "domanda2": "Ci sarà interferenza?"
    },

    "2": {
        "nome": "Seth vs Punk",
        "domanda1": "Chi vince?",
        "domanda2": "Ci sarà sangue?"
    },

    "3": {
        "nome": "MITB Match",
        "domanda1": "Chi vince?",
        "domanda2": "Ci sarà cash-in?"
    }

}

# PRONOSTICI
pronostici = {}

# START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    testo = "🏆 FANTAWRESTLING WWE 🏆\n\n"

    testo += "MATCH DISPONIBILI:\n\n"

    for match_id, dati in matches.items():

        testo += f'{match_id}. {dati["nome"]}\n'
        testo += f'   1️⃣ {dati["domanda1"]}\n'
        testo += f'   2️⃣ {dati["domanda2"]}\n\n'

    testo += "COME SCOMMETTERE:\n\n"

    testo += "/pronostico ID risposta1 risposta2 bonus si/no\n\n"

    testo += "ESEMPIO:\n"
    testo += "/pronostico 1 Cody si bonus si"

    await update.message.reply_text(testo)

# PRONOSTICO
async def pronostico(update: Update, context: ContextTypes.DEFAULT_TYPE):

    utente = update.effective_user.first_name

    if len(context.args) < 5:

        await update.message.reply_text(
            '❌ Usa:\n/pronostico ID risposta1 risposta2 bonus si/no'
        )

        return

    match_id = context.args[0]

    if match_id not in matches:

        await update.message.reply_text(
            '❌ Match non esistente'
        )

        return

    risposta1 = context.args[1]
    risposta2 = context.args[2]

    # BONUS SI/NO
    bonus_attivazione = context.args[4].lower()

    bonus = False

    if bonus_attivazione == "si":

        bonus = True

    # CREA MATCH
    if match_id not in pronostici:

        pronostici[match_id] = {}

    pronostici[match_id][utente] = {

        "risposta1": risposta1,
        "risposta2": risposta2,
        "bonus": bonus

    }

    testo_bonus = "❌ BONUS NON ATTIVO"

    if bonus:

        testo_bonus = "🎰 BONUS ATTIVO"

    await update.message.reply_text(

        f'✅ Pronostico salvato!\n\n'
        f'Match: {matches[match_id]["nome"]}\n'
        f'1️⃣ {risposta1}\n'
        f'2️⃣ {risposta2}\n'
        f'{testo_bonus}'

    )

# RISULTATO MATCH
async def risultato(update: Update, context: ContextTypes.DEFAULT_TYPE):

    # CONTROLLO ADMIN
    utente_id = update.effective_user.id

    if utente_id not in ADMIN_IDS:

        await update.message.reply_text(
            '❌ Solo gli admin possono inserire risultati.'
        )

        return

    if len(context.args) < 3:

        await update.message.reply_text(
            '❌ Usa:\n/risultato ID risposta1 risposta2'
        )

        return

    match_id = context.args[0]

    if match_id not in matches:

        await update.message.reply_text(
            '❌ Match non esistente'
        )

        return

    risultato1 = context.args[1]
    risultato2 = context.args[2]

    testo = f'🏆 RISULTATI {matches[match_id]["nome"]}\n\n'

    if match_id not in pronostici:

        testo += "Nessun pronostico."

        await update.message.reply_text(testo)

        return

    for utente, dati in pronostici[match_id].items():

        punti = 0

        corretta1 = (

            dati["risposta1"].lower()
            == risultato1.lower()

        )

        corretta2 = (

            dati["risposta2"].lower()
            == risultato2.lower()

        )

        # 1 punto per risposta corretta
        if corretta1:

            punti += 1

        if corretta2:

            punti += 1

        # BONUS
        if dati["bonus"]:

            # SE ENTRAMBE CORRETTE
            if corretta1 and corretta2:

                punti *= 2

            # SE UNA SBAGLIATA
            else:

                punti = 0

        # CREA UTENTE IN CLASSIFICA
        if utente not in classifica:

            classifica[utente] = 0

        # AGGIUNGI PUNTI
        classifica[utente] += punti

        # SALVA FILE
        salva_classifica()

        bonus_testo = ""

        if dati["bonus"]:

            bonus_testo = " 🎰"

        testo += f'{utente}: +{punti} punti{bonus_testo}\n'

    await update.message.reply_text(testo)

# CLASSIFICA
async def classifica_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):

    testo = '🏅 CLASSIFICA GENERALE\n\n'

    if len(classifica) == 0:

        testo += 'Nessun punto.'

    else:

        classifica_ordinata = sorted(

            classifica.items(),
            key=lambda x: x[1],
            reverse=True

        )

        posizione = 1

        for utente, punti in classifica_ordinata:

            testo += f'{posizione}. {utente} - {punti} punti\n'

            posizione += 1

    await update.message.reply_text(testo)

# RESET CLASSIFICA
async def reset_classifica(update: Update, context: ContextTypes.DEFAULT_TYPE):

    # CONTROLLO ADMIN
    utente_id = update.effective_user.id

    if utente_id not in ADMIN_IDS:

        await update.message.reply_text(
            '❌ Solo gli admin possono resettare.'
        )

        return

    global classifica

    classifica = {}

    salva_classifica()

    await update.message.reply_text(
        '🔄 Classifica resettata!'
    )

# AVVIO BOT
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(
    CommandHandler('start', start)
)

app.add_handler(
    CommandHandler('pronostico', pronostico)
)

app.add_handler(
    CommandHandler('risultato', risultato)
)

app.add_handler(
    CommandHandler('classifica', classifica_cmd)
)

app.add_handler(
    CommandHandler('reset_classifica', reset_classifica)
)

print("BOT ONLINE")

app.run_polling()