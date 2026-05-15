# Fantawrestling WWE Bot V5 - Programma Completo

# VERSIONE V5.5 ATTIVA


import json
import os
from datetime import datetime
from zoneinfo import ZoneInfo

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    JobQueue,
    filters
)

TOKEN = os.getenv("TOKEN")

ADMIN_IDS = [

    5802394692,  # Matteo
    1621756331   # Ciro

]

CARDS_FILE = "cards.json"
CLASSIFICA_FILE = "classifica.json"
PRONOSTICI_FILE = "pronostici.json"
UTENTI_FILE = "utenti.json"
SEASONS_FILE = "seasons.json"


(
    CARD_NAME,
    NUM_MATCHES,
    OPEN_TIME,
    CLOSE_TIME,
    MATCH_NAME,
    QUESTION_1,
    ANSWERS_1,
    QUESTION_2,
    ANSWERS_2,

    RESULT_CARD,
    RESULT_MATCH,
    RESULT_1,
    RESULT_2,

PERCENT_CARD,
PERCENT_MATCH,


CLOSE_CARD,
NEW_SEASON



) = range(18)


def load_json(file_name):

    if os.path.exists(file_name):

        with open(file_name, "r", encoding="utf-8") as file:

            return json.load(file)

    return {}


def save_json(file_name, data):

    with open(file_name, "w", encoding="utf-8") as file:

        json.dump(data, file, indent=4, ensure_ascii=False)


cards = load_json(CARDS_FILE)
classifica = load_json(CLASSIFICA_FILE)
pronostici = load_json(PRONOSTICI_FILE)
utenti = load_json(UTENTI_FILE)
seasons = load_json(SEASONS_FILE)

if "attiva" not in seasons:


    seasons["attiva"] = "Season 1"

    save_json(SEASONS_FILE, seasons)

def is_admin(user_id):

    return user_id in ADMIN_IDS

if "hall_of_fame" not in seasons:

    seasons["hall_of_fame"] = []

    save_json(SEASONS_FILE, seasons)


# ==========================================
# START
# ==========================================

# ==========================================
# START
# ==========================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = str(update.effective_user.id)

    utenti[user_id] = {
        "nome": update.effective_user.first_name
    }

    save_json(UTENTI_FILE, utenti)

    await update.message.reply_text(
        "🤖 Bot avviato!\n\nUsa /fantawrestling"
    )


# ==========================================
# FANTAWRESTLING MENU
# ==========================================

async def fantawrestling(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = []

    now = datetime.now(ZoneInfo("Europe/Rome"))

    for card_id, card in cards.items():

        apertura = datetime.strptime(
            card["apertura"],
            "%d/%m/%Y %H:%M"
        ).replace(tzinfo=ZoneInfo("Europe/Rome"))

        chiusura = datetime.strptime(
            card["chiusura"],
            "%d/%m/%Y %H:%M"
        ).replace(tzinfo=ZoneInfo("Europe/Rome"))

        if apertura <= now <= chiusura:

            keyboard.append([
                InlineKeyboardButton(
                    card["nome"],
                    callback_data=f"card_{card_id}"
                )
            ])

    if len(keyboard) == 0:

        await update.message.reply_text(
            "⛔ Nessuna card disponibile."
        )

        return

    reply_markup = InlineKeyboardMarkup(keyboard)

    # CHAT PRIVATA
    if update.effective_chat.type == "private":

        await update.message.reply_text(
            "🏆 CARD DISPONIBILI",
            reply_markup=reply_markup
        )

        return

    # CHAT GRUPPO
    try:

        await context.bot.send_message(
            chat_id=update.effective_user.id,
            text="🏆 CARD DISPONIBILI",
            reply_markup=reply_markup
        )

        await update.message.reply_text(
            "📩 Controlla la chat privata col bot!"
        )

    except:

        bot_username = (
            await context.bot.get_me()
        ).username

        await update.message.reply_text(
            f"⚠️ Prima devi avviare il bot in privato:\n\n"
            f"👉 https://t.me/{bot_username}\n\n"
            f"Poi premi /start e riprova."
        )

# ==========================================
# APRI CARD
# ==========================================

async def open_card(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()

    card_id = query.data.replace("card_", "")

    context.user_data["current_card"] = card_id

    card = cards[card_id]

    testo = f'🏆 {card["nome"]}\n\n'
    testo += "Seleziona un match:\n\n"

    keyboard = []

    for i, match in enumerate(card["match"]):

        keyboard.append([
            InlineKeyboardButton(
                match["nome"],
                callback_data=f"match_{card_id}_{i}"
            )
        ])

    await query.message.reply_text(
        testo,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ==========================================
# APRI MATCH
# ==========================================

async def open_match(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()

    data = query.data.split("_")

    card_id = data[1]
    match_index = int(data[2])

    card = cards[card_id]
    match = card["match"][match_index]

    context.user_data["match_index"] = match_index

    testo = f'🔥 {match["nome"]}\n\n'
    testo += f'1️⃣ {match["domanda1"]}\n\n'

    keyboard = []

    for risposta in match["risposte1"]:

        keyboard.append([
            InlineKeyboardButton(
                risposta,
                callback_data=f"r1_{risposta}"
            )
        ])

    await query.message.reply_text(
        testo,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ==========================================
# RISPOSTA 1
# ==========================================

async def risposta1(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()

    risposta = query.data.replace("r1_", "")

    context.user_data["risposta1"] = risposta

    card_id = context.user_data["current_card"]
    match_index = context.user_data["match_index"]

    match = cards[card_id]["match"][match_index]

    testo = f'2️⃣ {match["domanda2"]}\n\n'

    keyboard = []

    for risposta in match["risposte2"]:

        keyboard.append([
            InlineKeyboardButton(
                risposta,
                callback_data=f"r2_{risposta}"
            )
        ])

    await query.message.reply_text(
        testo,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ==========================================
# RISPOSTA 2
# ==========================================

async def risposta2(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()

    risposta = query.data.replace("r2_", "")

    context.user_data["risposta2"] = risposta

    keyboard = [
        [
            InlineKeyboardButton(
                "🎰 ATTIVA BONUS",
                callback_data="bonus_si"
            )
        ],
        [
            InlineKeyboardButton(
                "❌ NO BONUS",
                callback_data="bonus_no"
            )
        ]
    ]

    await query.message.reply_text(
        "Vuoi attivare il bonus?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ==========================================
# BONUS
# ==========================================

async def bonus(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()

    bonus_attivo = query.data == "bonus_si"

    user_id = str(query.from_user.id)
    nome = query.from_user.first_name

    card_id = context.user_data["current_card"]
    match_index = str(context.user_data["match_index"])

    # CREA UTENTE
    if user_id not in pronostici:

        pronostici[user_id] = {}
    # MATCH GIÀ VOTATO
    match_gia_votato = False

    if (
        user_id in pronostici
        and card_id in pronostici[user_id]
        and match_index in pronostici[user_id][card_id]["match"]
    ):

        match_gia_votato = True
    # CREA CARD
    if card_id not in pronostici[user_id]:

        pronostici[user_id][card_id] = {
            "bonus_usato": False,
            "match": {}
        }

    # CONTROLLO BONUS UNICO
    if bonus_attivo:

        if pronostici[user_id][card_id]["bonus_usato"]:

            await query.message.reply_text(
                "❌ Hai già usato il bonus in questa card."
            )

            return

        pronostici[user_id][card_id]["bonus_usato"] = True

    pronostici[user_id][card_id]["match"][match_index] = {

        "utente": nome,
        "risposta1": context.user_data["risposta1"],
        "risposta2": context.user_data["risposta2"],
        "bonus": bonus_attivo

    }

    save_json(PRONOSTICI_FILE, pronostici)

    if match_gia_votato:

        testo = "✏️ Pronostico modificato!\n\n"

    else:

        testo = "✅ Pronostico salvato!\n\n"

    if bonus_attivo:

        testo += "🎰 BONUS ATTIVO"

    else:

        testo += "❌ BONUS NON ATTIVO"

    await query.message.reply_text(testo)

    # MATCH NON ANCORA VOTATI
    card = cards[card_id]

    match_votati = pronostici[user_id][card_id]["match"]

    keyboard = []

    for i, match in enumerate(card["match"]):

        if str(i) not in match_votati:

            keyboard.append([
                InlineKeyboardButton(
                    match["nome"],
                    callback_data=f"match_{card_id}_{i}"
                )
            ])

    if len(keyboard) > 0:

        await query.message.reply_text(
            "🎮 Match ancora da votare:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    else:

        await query.message.reply_text(
            "🏆 Hai completato tutti i pronostici della card!"
        )

# ==========================================
# CREA CARD
# ==========================================

async def crea_card(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not is_admin(update.effective_user.id):

        return ConversationHandler.END

    context.user_data["new_card"] = {
        "match": []
    }

    await update.message.reply_text(
        "📋 Nome della card?"
    )

    return CARD_NAME


async def set_card_name(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data["new_card"]["nome"] = update.message.text


    context.user_data["new_card"]["season"] = seasons["attiva"]

    await update.message.reply_text(
        "🎮 Quanti match vuoi inserire?"
    )

    return NUM_MATCHES


async def set_num_matches(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data["num_matches"] = int(update.message.text)
    context.user_data["current_match"] = 0

    await update.message.reply_text(
        "⏰ Data apertura scommesse?\nFormato: 15/05/2026 18:00"
    )

    return OPEN_TIME


async def set_open_time(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data["new_card"]["apertura"] = update.message.text

    await update.message.reply_text(
        "🔒 Data chiusura scommesse?"
    )

    return CLOSE_TIME


async def set_close_time(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data["new_card"]["chiusura"] = update.message.text

    await update.message.reply_text(
        "🏆 Nome Match 1?"
    )

    return MATCH_NAME


async def set_match_name(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data["temp_match"] = {
        "nome": update.message.text
    }

    await update.message.reply_text(
        "1️⃣ Prima domanda?"
    )

    return QUESTION_1


async def set_question1(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data["temp_match"]["domanda1"] = update.message.text

    await update.message.reply_text(
        "Risposte domanda 1?\nFormato: Cody,Roman"
    )

    return ANSWERS_1


async def set_answers1(update: Update, context: ContextTypes.DEFAULT_TYPE):

    risposte = update.message.text.split(",")

    context.user_data["temp_match"]["risposte1"] = risposte

    await update.message.reply_text(
        "2️⃣ Seconda domanda?"
    )

    return QUESTION_2


async def set_question2(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data["temp_match"]["domanda2"] = update.message.text

    await update.message.reply_text(
        "Risposte domanda 2?\nFormato: Si,No"
    )

    return ANSWERS_2


async def set_answers2(update: Update, context: ContextTypes.DEFAULT_TYPE):

    risposte = update.message.text.split(",")

    context.user_data["temp_match"]["risposte2"] = risposte

    context.user_data["new_card"]["match"].append(
        context.user_data["temp_match"]
    )

    context.user_data["current_match"] += 1

    if context.user_data["current_match"] < context.user_data["num_matches"]:

        numero = context.user_data["current_match"] + 1

        await update.message.reply_text(
            f'🏆 Nome Match {numero}?'
        )

        return MATCH_NAME

    # SALVA CARD
    nuovo_id = str(len(cards) + 1)

    cards[nuovo_id] = context.user_data["new_card"]

    save_json(CARDS_FILE, cards)

    await update.message.reply_text(
        "✅ Card creata correttamente!"
    )

    return ConversationHandler.END



# ==========================================
# LISTA CARD
# ==========================================

async def lista_card(update: Update, context: ContextTypes.DEFAULT_TYPE):

    testo = "📋 CARD PROGRAMMATE\n\n"

    if len(cards) == 0:

        testo += "Nessuna card disponibile."

    else:

        for card_id, card in cards.items():

            testo += f'ID: {card_id}\n'
            testo += f'🏆 {card["nome"]}\n'
            testo += f'⏰ Apertura: {card["apertura"]}\n'
            testo += f'🔒 Chiusura: {card["chiusura"]}\n'
            testo += f'🎮 Match: {len(card["match"])}\n\n'

    await update.message.reply_text(testo)


# ==========================================
# CLASSIFICA
# ==========================================

async def classifica_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):

    testo = "🏅 CLASSIFICA\n\n"

    classifica_ordinata = sorted(
        classifica.items(),
        key=lambda x: x[1],
        reverse=True
    )

    if len(classifica_ordinata) == 0:

        testo += "Nessun punteggio disponibile."

    else:

        posizione = 1

        for utente, punti in classifica_ordinata:

            testo += f'{posizione}. {utente} - {punti} punti\n'
            posizione += 1

    await update.message.reply_text(testo)


# ==========================================
# RESET CLASSIFICA
# ==========================================

async def reset_classifica(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not is_admin(update.effective_user.id):

        return

    global classifica

    classifica = {}

    save_json(CLASSIFICA_FILE, classifica)

    await update.message.reply_text(
        "🔄 Classifica resettata"
    )

# ==========================================
# CALCOLO PUNTI
# ==========================================

def calcola_punti(
    risposta1_utente,
    risposta2_utente,
    risultato1,
    risultato2,
    bonus
):

    punti = 0

    corrette = 0

    if risposta1_utente == risultato1:

        corrette += 1

    if risposta2_utente == risultato2:

        corrette += 1

    # BONUS
    if bonus:

        if corrette == 2:

            return 4

        return 0

    return corrette

# ==========================================
# INSERISCI RISULTATI
# ==========================================

async def inserisci_risultati(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_chat.type != "private":

        await update.message.reply_text(
            "📩 Usa questo comando in privato col bot."
        )

        return ConversationHandler.END

    if not is_admin(update.effective_user.id):

        return ConversationHandler.END

    keyboard = []

    for card_id, card in cards.items():

        keyboard.append([
            InlineKeyboardButton(
                card["nome"],
                callback_data=f"resultcard_{card_id}"
            )
        ])

    await update.message.reply_text(
        "🏆 Seleziona la card:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    return RESULT_CARD


async def result_card_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()

    card_id = query.data.replace("resultcard_", "")

    context.user_data["result_card"] = card_id

    card = cards[card_id]

    keyboard = []

    for i, match in enumerate(card["match"]):

        keyboard.append([
            InlineKeyboardButton(
                match["nome"],
                callback_data=f"resultmatch_{i}"
            )
        ])

    await query.message.reply_text(
        "🎮 Seleziona il match:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    return RESULT_MATCH


async def result_match_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()

    match_index = int(
        query.data.replace("resultmatch_", "")
    )

    context.user_data["result_match"] = match_index

    card_id = context.user_data["result_card"]

    match = cards[card_id]["match"][match_index]

    keyboard = []

    for risposta in match["risposte1"]:

        keyboard.append([
            InlineKeyboardButton(
                risposta,
                callback_data=f"real1_{risposta}"
            )
        ])

    await query.message.reply_text(
        f'1️⃣ {match["domanda1"]}',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    return RESULT_1


async def result_1_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()

    risposta = query.data.replace("real1_", "")

    context.user_data["real_result_1"] = risposta

    card_id = context.user_data["result_card"]
    match_index = context.user_data["result_match"]

    match = cards[card_id]["match"][match_index]

    keyboard = []

    for risposta in match["risposte2"]:

        keyboard.append([
            InlineKeyboardButton(
                risposta,
                callback_data=f"real2_{risposta}"
            )
        ])

    await query.message.reply_text(
        f'2️⃣ {match["domanda2"]}',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    return RESULT_2


async def result_2_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()

    risultato2 = query.data.replace("real2_", "")

    risultato1 = context.user_data["real_result_1"]

    card_id = context.user_data["result_card"]
    match_index = str(context.user_data["result_match"])

    risultati_testo = "🏆 RISULTATI MATCH\n\n"

    for user_id, dati in pronostici.items():

        if card_id not in dati:

            continue

        if match_index not in dati[card_id]["match"]:

            continue

        pronostico = dati[card_id]["match"][match_index]

        nome = pronostico["utente"]

        punti = calcola_punti(
            pronostico["risposta1"],
            pronostico["risposta2"],
            risultato1,
            risultato2,
            pronostico["bonus"]
        )

        if nome not in classifica:

            classifica[nome] = 0

        classifica[nome] += punti

        risultati_testo += f'{nome} +{punti} punti\n'

    save_json(CLASSIFICA_FILE, classifica)

    await query.message.reply_text(risultati_testo)

    return ConversationHandler.END

# ==========================================
# PERCENTUALI LIVE
# ==========================================

async def percentuali(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    
    if update.effective_chat.type != "private":

        await update.message.reply_text(
            "📩 Usa questo comando in privato col bot."
        )

        return ConversationHandler.END
    keyboard = []

    for card_id, card in cards.items():

        keyboard.append([
            InlineKeyboardButton(
                card["nome"],
                callback_data=f"percentcard_{card_id}"
            )
        ])

    await update.message.reply_text(
        "📊 Seleziona una card:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    return PERCENT_CARD


async def percent_card_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()

    card_id = query.data.replace("percentcard_", "")

    context.user_data["percent_card"] = card_id

    card = cards[card_id]

    keyboard = []

    for i, match in enumerate(card["match"]):

        keyboard.append([
            InlineKeyboardButton(
                match["nome"],
                callback_data=f"percentmatch_{i}"
            )
        ])

    await query.message.reply_text(
        "🎮 Seleziona il match:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    return PERCENT_MATCH


async def percent_match_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()

    match_index = str(
        query.data.replace("percentmatch_", "")
    )

    card_id = context.user_data["percent_card"]

    match = cards[card_id]["match"][int(match_index)]

    conteggio_1 = {}
    conteggio_2 = {}

    totale = 0

    # PREPARA RISPOSTE
    for risposta in match["risposte1"]:

        conteggio_1[risposta] = 0

    for risposta in match["risposte2"]:

        conteggio_2[risposta] = 0

    # CONTA VOTI
    for user_id, dati in pronostici.items():

        if card_id not in dati:

            continue

        if match_index not in dati[card_id]["match"]:

            continue

        voto = dati[card_id]["match"][match_index]

        conteggio_1[voto["risposta1"]] += 1
        conteggio_2[voto["risposta2"]] += 1

        totale += 1

    testo = f'🔥 {match["nome"]}\n\n'

    testo += f'1️⃣ {match["domanda1"]}\n\n'

    for risposta, valore in conteggio_1.items():

        percentuale = 0

        if totale > 0:

            percentuale = round(
                (valore / totale) * 100
            )

        testo += f'📊 {risposta} — {percentuale}%\n'

    testo += "\n"

    testo += f'2️⃣ {match["domanda2"]}\n\n'

    for risposta, valore in conteggio_2.items():

        percentuale = 0

        if totale > 0:

            percentuale = round(
                (valore / totale) * 100
            )

        testo += f'📊 {risposta} — {percentuale}%\n'

    await query.message.reply_text(testo)

    return ConversationHandler.END

# ==========================================
# PROFILO UTENTE
# ==========================================

async def profilo(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = str(update.effective_user.id)

    nome = update.effective_user.first_name

    punti = 0

    if nome in classifica:

        punti = classifica[nome]

    match_giocati = 0
    bonus_usati = 0
    risposte_corrette = 0
    risposte_totali = 0

    for uid, dati in pronostici.items():

        if uid != user_id:

            continue

        for card_id, card_data in dati.items():

            if "match" not in card_data:

                continue

            for match_id, match in card_data["match"].items():

                match_giocati += 1

                if match["bonus"]:

                    bonus_usati += 1

                # Accuracy stimata
                risposte_totali += 2

    accuracy = 0

    if risposte_totali > 0:

        accuracy = round(
            (punti / risposte_totali) * 100
        )

        if accuracy > 100:

            accuracy = 100

    # POSIZIONE CLASSIFICA
    classifica_ordinata = sorted(
        classifica.items(),
        key=lambda x: x[1],
        reverse=True
    )

    posizione = "-"

    for index, (utente, score) in enumerate(classifica_ordinata):

        if utente == nome:

            posizione = index + 1
            break
    # ==========================================
    # BADGE
    # ==========================================

    badges = []

    if punti >= 10:

        badges.append("🔥 The Predictor")

    if bonus_usati >= 5:

        badges.append("🎰 Bonus Master")

    if match_giocati >= 20:

        badges.append("🏆 Main Eventer")

    if posizione == 1:

        badges.append("👑 Undisputed Champion")

    if punti == 0 and match_giocati >= 5:

        badges.append("💀 Jobber")

    badge_text = ""

    if len(badges) > 0:

        badge_text = "\n\n🏆 BADGE\n\n"

        for badge in badges:

            badge_text += f"{badge}\n"

    posizione_text = "-"

    if posizione != "-":

        posizione_text = f"#{posizione}"

    testo = (
        f'👤 {nome}\n\n'
        f'🏅 Punti: {punti}\n'
        f'🎮 Match giocati: {match_giocati}\n'
        f'🎰 Bonus usati: {bonus_usati}\n'
        f'🔥 Accuracy: {accuracy}%\n'
        f'📊 Posizione in classifica: {posizione_text}'
        f'{badge_text}'
    )

    await update.message.reply_text(testo)


# ==========================================
# NOTIFICHE CARD
# ==========================================

async def controlla_card(context: ContextTypes.DEFAULT_TYPE):

    now = datetime.now(ZoneInfo("Europe/Rome"))

    for card_id, card in cards.items():

        chiusura = datetime.strptime(
            card["chiusura"],
            "%d/%m/%Y %H:%M"
        ).replace(tzinfo=ZoneInfo("Europe/Rome"))

        differenza = (chiusura - now).total_seconds()

        # NOTIFICA A 30 MINUTI
        if 1700 < differenza < 1800:

            for user_id in utenti:

                try:

                    await context.bot.send_message(
                        chat_id=user_id,
                        text=(
                            f"⚠️ Mancano 30 minuti alla chiusura delle scommesse!\n\n"
                            f"🏆 {card['nome']}"
                        )
                    )

                except:

                    pass


# ==========================================
# CHIUSURA FORZATA CARD
# ==========================================

async def chiudi_card(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not is_admin(update.effective_user.id):

        return ConversationHandler.END

    keyboard = []

    for card_id, card in cards.items():

        keyboard.append([
            InlineKeyboardButton(
                card["nome"],
                callback_data=f"closecard_{card_id}"
            )
        ])

    await update.message.reply_text(
        "🔒 Seleziona la card da chiudere:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    return CLOSE_CARD


async def close_card_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()

    card_id = query.data.replace(
        "closecard_",
        ""
    )

    now = datetime.now(
        ZoneInfo("Europe/Rome")
    )

    cards[card_id]["chiusura"] = now.strftime(
        "%d/%m/%Y %H:%M"
    )

    save_json(CARDS_FILE, cards)

    await query.message.reply_text(
        "🔒 Scommesse chiuse manualmente!"
    )

    return ConversationHandler.END

# ==========================================
# SEASON ATTIVA
# ==========================================

async def season(update: Update, context: ContextTypes.DEFAULT_TYPE):

    testo = (
        f'🏆 SEASON ATTIVA\n\n'
        f'{seasons["attiva"]}'
    )

    await update.message.reply_text(testo)


# ==========================================
# CREA SEASON
# ==========================================

async def crea_season(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not is_admin(update.effective_user.id):

        return ConversationHandler.END

    await update.message.reply_text(
        "🏆 Nome nuova season?"
    )

    return NEW_SEASON


async def salva_season(update: Update, context: ContextTypes.DEFAULT_TYPE):

    global classifica

    nuova_season = update.message.text

    # TROVA CAMPIONE
    campione = "Nessuno"

    if len(classifica) > 0:

        classifica_ordinata = sorted(
            classifica.items(),
            key=lambda x: x[1],
            reverse=True
        )

        campione = classifica_ordinata[0][0]

    # SALVA HALL OF FAME
    seasons["hall_of_fame"].append({

        "season": seasons["attiva"],
        "campione": campione

    })

    # CAMBIA SEASON
    seasons["attiva"] = nuova_season

    save_json(SEASONS_FILE, seasons)

    # RESET CLASSIFICA
    classifica = {}

    save_json(CLASSIFICA_FILE, classifica)

    await update.message.reply_text(
        f'🔥 Nuova season creata!\n\n'
        f'🏆 Season: {nuova_season}'
    )

    return ConversationHandler.END

# ==========================================
# HALL OF FAME
# ==========================================

async def halloffame(update: Update, context: ContextTypes.DEFAULT_TYPE):

    testo = "👑 HALL OF FAME\n\n"

    if len(seasons["hall_of_fame"]) == 0:

        testo += "Nessuna season conclusa."

    else:

        for voce in seasons["hall_of_fame"]:

            testo += (
                f'🏆 {voce["season"]}\n'
                f'👑 Campione: {voce["campione"]}\n\n'
            )

    await update.message.reply_text(testo)


# ==========================================
# APP
# ==========================================

app = ApplicationBuilder().token(TOKEN).build()

create_card_handler = ConversationHandler(
    entry_points=[CommandHandler("crea_card", crea_card)],
    states={
        CARD_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_card_name)],
        NUM_MATCHES: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_num_matches)],
        OPEN_TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_open_time)],
        CLOSE_TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_close_time)],
        MATCH_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_match_name)],
        QUESTION_1: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_question1)],
        ANSWERS_1: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_answers1)],
        QUESTION_2: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_question2)],
        ANSWERS_2: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_answers2)]
    },
    fallbacks=[]
)

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("fantawrestling", fantawrestling))
app.add_handler(CommandHandler("classifica", classifica_cmd))
app.add_handler(CommandHandler("season", season))
app.add_handler(CommandHandler("halloffame", halloffame))
app.add_handler(CommandHandler("profilo", profilo))
app.add_handler(CommandHandler("lista_card", lista_card))
app.add_handler(CommandHandler("reset_classifica", reset_classifica))

app.add_handler(create_card_handler)


app.add_handler(CallbackQueryHandler(open_card, pattern="^card_"))
app.add_handler(CallbackQueryHandler(open_match, pattern="^match_"))
app.add_handler(CallbackQueryHandler(risposta1, pattern="^r1_"))
app.add_handler(CallbackQueryHandler(risposta2, pattern="^r2_"))
app.add_handler(CallbackQueryHandler(bonus, pattern="^bonus_"))

result_handler = ConversationHandler(

    entry_points=[
        CommandHandler(
            "inserisci_risultati",
            inserisci_risultati
        )
    ],

    states={

        RESULT_CARD: [
            CallbackQueryHandler(
                result_card_callback,
                pattern="^resultcard_"
            )
        ],

        RESULT_MATCH: [
            CallbackQueryHandler(
                result_match_callback,
                pattern="^resultmatch_"
            )
        ],

        RESULT_1: [
            CallbackQueryHandler(
                result_1_callback,
                pattern="^real1_"
            )
        ],

        RESULT_2: [
            CallbackQueryHandler(
                result_2_callback,
                pattern="^real2_"
            )
        ]
    },

    fallbacks=[]
)
app.add_handler(result_handler)

percent_handler = ConversationHandler(

    entry_points=[
        CommandHandler(
            "percentuali",
            percentuali
        )
    ],

    states={

        PERCENT_CARD: [
            CallbackQueryHandler(
                percent_card_callback,
                pattern="^percentcard_"
            )
        ],

        PERCENT_MATCH: [
            CallbackQueryHandler(
                percent_match_callback,
                pattern="^percentmatch_"
            )
        ]
    },

    fallbacks=[]
)
app.add_handler(percent_handler)

job_queue = app.job_queue

job_queue.run_repeating(
    controlla_card,
    interval=60,
    first=10
)


close_handler = ConversationHandler(

    entry_points=[
        CommandHandler(
            "chiudi_card",
            chiudi_card
        )
    ],

    states={

        CLOSE_CARD: [
            CallbackQueryHandler(
                close_card_callback,
                pattern="^closecard_"
            )
        ]
    },

    fallbacks=[]
)

app.add_handler(close_handler)

season_handler = ConversationHandler(

    entry_points=[
        CommandHandler(
            "crea_season",
            crea_season
        )
    ],

    states={

        NEW_SEASON: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                salva_season
            )
        ]
    },

    fallbacks=[]
)

app.add_handler(season_handler)


print("BOT ONLINE")

app.run_polling()