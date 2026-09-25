from telegram import (
    Update,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

import asyncio


# ==================================================
# TOKEN
# ==================================================

TOKEN = "BU_YERGA_TOKEN_QOYILMAYDI"


# ==================================================
# ADMIN
# ==================================================

ADMIN_CHAT_ID = 8963058386


# ==================================================
# CITY FOOD LOKATSIYASI
# ==================================================

CITY_FOOD_LAT = 40.947874
CITY_FOOD_LON = 70.770122

CITY_FOOD_ADDRESS = "Chodak markazi (bozor)"


# ==================================================
# BUYURTMA RAQAMI
# ==================================================

ORDER_NUMBER = 1000


# ==================================================
# STATISTIKA
# ==================================================

TOTAL_ORDERS = 0
TOTAL_RATING = 0
RATING_COUNT = 0


# ==================================================
# BUYURTMALAR
# ==================================================

ORDERS = {}

order_lock = asyncio.Lock()


# ==================================================
# MENYU
# ==================================================

MENU = {

    "🍗 Chicken combo": 36000,
    "🍔 Gamburger combo": 37000,
    "🧀 Chizburger combo": 39000,
    "🌯 Lavash combo": 42000,

    "🌭 Hot-dog kichkina": 10000,
    "🌭 Hot-dog oddiy": 13000,
    "🌭 Hot-dog dabl": 16000,
    "🌭 Hot-dog tovuqli": 19000,
    "🌭 Hot-dog go‘shtli": 22000,
    "🌭 Hot-doog shashlikli": 23000,

    "🌯 Lavash kichkina": 27000,
    "🌯 Lavash katta": 31000,
    "🌯 Lavash chesnochniy": 32000,
    "🌯 Lavash sirli": 35000,
    "🌯 Lavash tandir": 36000,
    "🌯 Lavash achchiq": 36000,

    "🍔 Chicken burger": 24000,
    "🍔 Gamburger": 26000,
    "🧀 Chizburger": 28000,

    "🥙 Non kabob": 32000,
    "🥟 Olot somsa": 7000,

    "🍗 Strips pors": 18000,
    "🍗 Strips 1 kg": 85000,

    "🥪 Clap sandwich": 32000,

    "🍢 Qiyma shashlik": 16000,
    "🍢 Qiyma 1 kg": 110000,

    "🌯 Mini roll": 26000,
    "🍟 Kartoshka fri": 14000,

    "🍕 Pizza Pepperoni": 55000,
    "🍕 Pizza Tovuqli": 57000,
    "🍕 Pizza Combo": 62000,
    "🍕 Pizza Go‘shtli": 67000,
    "🍕 Pizza Mix": 70000
}


# ==================================================
# BOSH MENU
# ==================================================

def main_keyboard():

    keyboard = [
        ["🍔 Menyu", "🛒 Buyurtma berish"],
        ["🛒 Savat", "📍 Manzil"],
        ["📞 Aloqa", "⭐ Baho"]
    ]

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )


# ==================================================
# START
# ==================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data.clear()

    await update.message.reply_text(
        "🍔 CITY FOOD ga xush kelibsiz!\n\n"
        "Kerakli bo‘limni tanlang 👇",
        reply_markup=main_keyboard()
    )


# ==================================================
# MENYU
# ==================================================

async def show_menu(update, context):

    text = "🍔 CITY FOOD MENYU\n\n"

    for product, price in MENU.items():
        text += f"{product} — {price:,} so‘m\n"

    await update.message.reply_text(text)


# ==================================================
# MAHSULOT TANLASH
# ==================================================

async def product_buttons(update, context):

    buttons = []

    products = list(MENU.keys())

    for i in range(0, len(products), 2):
        buttons.append(products[i:i + 2])

    buttons.append(["🛒 Savat"])
    buttons.append(["⬅️ Bosh menu"])

    await update.message.reply_text(
        "🍔 Mahsulotni tanlang:",
        reply_markup=ReplyKeyboardMarkup(
            buttons,
            resize_keyboard=True
        )
    )


# ==================================================
# SAVAT
# ==================================================

async def show_cart(update, context):

    cart = context.user_data.get("cart", {})

    if not cart:

        await update.message.reply_text(
            "🛒 Savatingiz hozircha bo‘sh."
        )

        return

    text = "🛒 SAVATINGIZ\n\n"

    total = 0

    for product, quantity in cart.items():

        price = MENU[product]
        summa = price * quantity

        total += summa

        text += (
            f"{product}\n"
            f"   {quantity} x {price:,} = "
            f"{summa:,} so‘m\n\n"
        )

    text += f"💰 JAMI: {total:,} so‘m"

    keyboard = [
        ["➕ Mahsulot qo‘shish"],
        ["🗑 Savatni tozalash"],
        ["✅ Buyurtmani rasmiylashtirish"],
        ["⬅️ Bosh menu"]
    ]

    await update.message.reply_text(
        text,
        reply_markup=ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True
        )
    )


# ==================================================
# BUYURTMANI RASMIYLASHTIRISH
# ==================================================

async def checkout(update, context):

    cart = context.user_data.get("cart", {})

    if not cart:

        await update.message.reply_text(
            "🛒 Savatingiz bo‘sh."
        )

        return

    context.user_data["waiting_phone"] = True

    phone_button = KeyboardButton(
        "📱 Telefon raqamimni yuborish",
        request_contact=True
    )

    await update.message.reply_text(
        "📱 Buyurtmani rasmiylashtirish uchun "
        "telefon raqamingizni yuboring 👇",
        reply_markup=ReplyKeyboardMarkup(
            [[phone_button]],
            resize_keyboard=True,
            one_time_keyboard=True
        )
    )


# ==================================================
# TELEFON
# ==================================================

async def contact_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not context.user_data.get("waiting_phone"):
        return

    phone = update.message.contact.phone_number

    context.user_data["phone"] = phone
    context.user_data["waiting_phone"] = False

    keyboard = [
        ["🚚 Yetkazib berish"],
        ["🏃 O‘zim olib ketaman"]
    ]

    await update.message.reply_text(
        "🚚 Buyurtmani qanday olasiz?",
        reply_markup=ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True
        )
    )


# ==================================================
# MIJOZ LOKATSIYASI
# ==================================================

async def location_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not context.user_data.get("waiting_location"):
        return

    location = update.message.location

    context.user_data["customer_lat"] = location.latitude
    context.user_data["customer_lon"] = location.longitude

    context.user_data["waiting_location"] = False

    await create_order(update, context)


# ==================================================
# BUYURTMA YARATISH
# ==================================================

async def create_order(update, context):

    global ORDER_NUMBER
    global TOTAL_ORDERS

    async with order_lock:

        cart = context.user_data.get("cart", {})

        if not cart:
            return

        ORDER_NUMBER += 1
        TOTAL_ORDERS += 1

        order_number = ORDER_NUMBER

        customer = update.effective_user

        phone = context.user_data.get(
            "phone",
            "Ko‘rsatilmagan"
        )

        delivery = context.user_data.get(
            "delivery",
            "Ko‘rsatilmagan"
        )

        total = 0
        order_text = ""

        for product, quantity in cart.items():

            price = MENU[product]
            summa = price * quantity

            total += summa

            order_text += (
                f"• {product}\n"
                f"  {quantity} x {price:,} = "
                f"{summa:,} so‘m\n"
            )

        admin_text = (
            f"🛎 YANGI BUYURTMA #{order_number}\n\n"
            f"👤 Mijoz: {customer.full_name}\n"
            f"🆔 Telegram ID: {customer.id}\n"
            f"📞 Telefon: {phone}\n\n"
            f"📦 BUYURTMA:\n"
            f"{order_text}\n"
            f"💰 JAMI: {total:,} so‘m\n\n"
            f"🚚 Olish turi: {delivery}\n\n"
            f"📍 CITY FOOD:\n"
            f"{CITY_FOOD_ADDRESS}\n\n"
            f"🟡 Holat: Qabul qilindi"
        )

        ORDERS[order_number] = {
            "customer_id": customer.id,
            "total": total,
            "status": "🟡 Qabul qilindi"
        }

        status_keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "🟡 Qabul qilindi",
                    callback_data=f"status_{order_number}_accepted"
                )
            ],
            [
                InlineKeyboardButton(
                    "👨‍🍳 Tayyorlanmoqda",
                    callback_data=f"status_{order_number}_cooking"
                )
            ],
            [
                InlineKeyboardButton(
                    "🚚 Yo‘lda",
                    callback_data=f"status_{order_number}_delivery"
                )
            ],
            [
                InlineKeyboardButton(
                    "✅ Yetkazildi",
                    callback_data=f"status_{order_number}_done"
                )
            ]
        ])

        # FAQAT ADMINGA
        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=admin_text,
            reply_markup=status_keyboard
        )

        # MIJOZ LOKATSIYASI
        if delivery == "🚚 Yetkazib berish":

            lat = context.user_data.get("customer_lat")
            lon = context.user_data.get("customer_lon")

            if lat is not None and lon is not None:

                await context.bot.send_location(
                    chat_id=ADMIN_CHAT_ID,
                    latitude=lat,
                    longitude=lon
                )

        # MIJOZGA
        await update.message.reply_text(
            f"✅ Buyurtmangiz qabul qilindi!\n\n"
            f"🔢 Buyurtma: #{order_number}\n"
            f"💰 Jami: {total:,} so‘m\n"
            f"🚚 {delivery}\n\n"
            f"Tez orada siz bilan bog‘lanamiz. 🍔",
            reply_markup=main_keyboard()
        )

        context.user_data["cart"] = {}


# ==================================================
# CITY FOOD MANZILI
# ==================================================

async def send_city_food_location(update, context):

    await update.message.reply_text(
        "📍 CITY FOOD\n\n"
        "Chodak markazi (bozor)"
    )

    await update.message.reply_location(
        latitude=CITY_FOOD_LAT,
        longitude=CITY_FOOD_LON
    )


# ==================================================
# BAHO
# ==================================================

async def show_rating(update, context):

    context.user_data["rating"] = True

    keyboard = [
        ["⭐"],
        ["⭐⭐"],
        ["⭐⭐⭐"],
        ["⭐⭐⭐⭐"],
        ["⭐⭐⭐⭐⭐"],
        ["⬅️ Bosh menu"]
    ]

    await update.message.reply_text(
        "⭐ CITY FOOD\n\n"
        "Buyurtmamizga necha baho berasiz?",
        reply_markup=ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True
        )
    )


# ==================================================
# BAHONI QABUL QILISH
# ==================================================

async def handle_rating(update, context):

    global TOTAL_RATING
    global RATING_COUNT

    text = update.message.text

    if not context.user_data.get("rating"):
        return False

    if text.startswith("⭐"):

        rating = len(text)

        TOTAL_RATING += rating
        RATING_COUNT += 1

        customer = update.effective_user

        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=(
                "⭐ YANGI BAHO\n\n"
                f"👤 Mijoz: {customer.full_name}\n"
                f"🆔 ID: {customer.id}\n"
                f"⭐ Baho: {rating}/5"
            )
        )

        context.user_data["rating"] = False

        await update.message.reply_text(
            "🙏 Bahoyingiz uchun rahmat!",
            reply_markup=main_keyboard()
        )

        return True

    return False


# ==================================================
# ADMIN STATISTIKA
# ==================================================

async def statistics(update, context):

    if update.effective_user.id != ADMIN_CHAT_ID:
        return

    average = 0

    if RATING_COUNT > 0:
        average = TOTAL_RATING / RATING_COUNT

    await update.message.reply_text(
        "📊 CITY FOOD STATISTIKA\n\n"
        f"🛎 Buyurtmalar: {TOTAL_ORDERS}\n"
        f"⭐ Baholar: {RATING_COUNT}\n"
        f"⭐ O‘rtacha: {average:.1f}/5"
    )


# ==================================================
# STATUS
# ==================================================

async def status_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()

    if update.effective_user.id != ADMIN_CHAT_ID:
        return

    parts = query.data.split("_")

    order_number = int(parts[1])
    status_code = parts[2]

    status_names = {
        "accepted": "🟡 Qabul qilindi",
        "cooking": "👨‍🍳 Tayyorlanmoqda",
        "delivery": "🚚 Yo‘lda",
        "done": "✅ Yetkazildi"
    }

    new_status = status_names.get(
        status_code,
        "🟡 Qabul qilindi"
    )

    if order_number in ORDERS:

        ORDERS[order_number]["status"] = new_status

        customer_id = ORDERS[order_number]["customer_id"]

        await context.bot.send_message(
            chat_id=customer_id,
            text=(
                f"🔔 Buyurtma #{order_number}\n\n"
                f"📦 Holat: {new_status}"
            )
        )

    await query.edit_message_reply_markup(
        reply_markup=None
    )


# ==================================================
# ASOSIY TEXT HANDLER
# ==================================================

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text

    # BAHO
    if await handle_rating(update, context):
        return

    # MENYU
    if text == "🍔 Menyu":

        await show_menu(update, context)
        return

    # BUYURTMA
    if text == "🛒 Buyurtma berish":

        await product_buttons(update, context)
        return

    # SAVAT
    if text == "🛒 Savat":

        await show_cart(update, context)
        return

    # MAHSULOT QO‘SHISH
    if text == "➕ Mahsulot qo‘shish":

        await product_buttons(update, context)
        return

    # MAHSULOT
    if text in MENU:

        cart = context.user_data.setdefault(
            "cart",
            {}
        )

        cart[text] = cart.get(text, 0) + 1

        await update.message.reply_text(
            f"✅ {text} savatga qo‘shildi.\n\n"
            f"📦 Soni: {cart[text]}\n"
            f"💰 Jami: {MENU[text] * cart[text]:,} so‘m"
        )

        return

    # RASMIYLASHTIRISH
    if text == "✅ Buyurtmani rasmiylashtirish":

        await checkout(update, context)
        return

    # SAVATNI TOZALASH
    if text == "🗑 Savatni tozalash":

        context.user_data["cart"] = {}

        await update.message.reply_text(
            "🗑 Savat tozalandi."
        )

        return

    # ==============================================
    # YETKAZIB BERISH
    # ==============================================

    if text == "🚚 Yetkazib berish":

        context.user_data["delivery"] = "🚚 Yetkazib berish"
        context.user_data["waiting_location"] = True

        location_button = KeyboardButton(
            "📍 Lokatsiyamni yuborish",
            request_location=True
        )

        keyboard = [
            [location_button],
            ["🏠 Keyinroq yuboraman"]
        ]

        await update.message.reply_text(
            "🚚 Yetkazib berish tanlandi.\n\n"
            "📌 Yetkazib berish narxi siz turgan "
            "joyingizga qarab o‘zgaradi.\n\n"
            "📍 Lokatsiyangizni yuboring 👇",
            reply_markup=ReplyKeyboardMarkup(
                keyboard,
                resize_keyboard=True
            )
        )

        return

    # ==============================================
    # O‘ZIM OLIB KETAMAN
    # ==============================================

    if text == "🏃 O‘zim olib ketaman":

        context.user_data["delivery"] = "🏃 O‘zim olib ketaman"

        await create_order(update, context)

        return

    # ==============================================
    # KEYINROQ
    # ==============================================

    if text == "🏠 Keyinroq yuboraman":

        context.user_data["customer_lat"] = None
        context.user_data["customer_lon"] = None
        context.user_data["waiting_location"] = False

        await create_order(update, context)

        return

    # ==============================================
    # CITY FOOD MANZILI
    # ==============================================

    if text == "📍 Manzil":

        await send_city_food_location(update, context)

        return

    # ==============================================
    # ALOQA
    # ==============================================

    if text == "📞 Aloqa":

        await update.message.reply_text(
            "📞 CITY FOOD\n\n"
            "Telefon: +998 50 525 23 38"
        )

        return

    # ==============================================
    # BAHO
    # ==============================================

    if text == "⭐ Baho":

        await show_rating(update, context)

        return

    # ==============================================
    # BOSH MENU
    # ==============================================

    if text == "⬅️ Bosh menu":

        await start(update, context)

        return

    await update.message.reply_text(
        "Iltimos, menyudagi tugmalardan birini tanlang 👇"
    )


# ==================================================
# BOTNI ISHGA TUSHIRISH
# ==================================================

app = Application.builder().token(TOKEN).build()


app.add_handler(
    CommandHandler("start", start)
)

app.add_handler(
    CommandHandler("stats", statistics)
)

app.add_handler(
    MessageHandler(
        filters.CONTACT,
        contact_handler
    )
)

app.add_handler(
    MessageHandler(
        filters.LOCATION,
        location_handler
    )
)

app.add_handler(
    CallbackQueryHandler(
        status_handler,
        pattern=r"^status_"
    )
)

app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        text_handler
    )
)


print("🍔 CITY FOOD BOT ISHGA TUSHDI...")


app.run_polling()