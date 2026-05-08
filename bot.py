import json
import os
from datetime import datetime

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
    filters
)

TOKEN = os.getenv("TOKEN")

ADMIN_IDS = [
    123456789
]

CARDS_FILE = "cards.json"
CLASSIFICA_FILE = "classifica.json"
PRONOSTICI_FILE = "pronostici.json"

(
    CARD_NAME,
    NUM_MATCHES,
    OPEN_TIME,
    CLOSE_TIME,
    MATCH_NAME,
    QUESTION_1,
    ANSWERS_1,
    QUESTION_2,
    ANSWERS_2
) = range(9)


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


def is_admin(user_id):

    return user_id in ADMIN_IDS


# ==========================================
# START
# ==========================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "Usa /fantawrestling"
    )


# ==========================================
# FANTAWRESTLING MENU
# ==========================================

async def fantawrestling(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = []

    now = datetime.now()

    for card_id, card in cards.items():

        apertura = datetime.strptime(
            card["apertura"],
            "%d/%m/%Y %H:%M"
        )

        chiusura = datetime.strptime(
            card["chiusura"],
            "%d/%m/%Y %H:%M"
        )

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

    await update.message.reply_text(
        "🏆 CARD DISPONIBILI",
        reply_markup=reply_markup
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

    testo = "✅ Pronostico salvato!\n\n"

    if bonus_attivo:

        testo += "🎰 BONUS ATTIVO"

    else:

        testo += "❌ BONUS NON ATTIVO"

    await query.message.reply_text(testo)


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
app.add_handler(CommandHandler("lista_card", lista_card))
app.add_handler(CommandHandler("reset_classifica", reset_classifica))

app.add_handler(create_card_handler)

app.add_handler(CallbackQueryHandler(open_card, pattern="^card_"))
app.add_handler(CallbackQueryHandler(open_match, pattern="^match_"))
app.add_handler(CallbackQueryHandler(risposta1, pattern="^r1_"))
app.add_handler(CallbackQueryHandler(risposta2, pattern="^r2_"))
app.add_handler(CallbackQueryHandler(bonus, pattern="^bonus_"))

print("BOT ONLINE")

app.run_polling()