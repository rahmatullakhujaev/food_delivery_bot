from db import Database
from translator import text
from datetime import datetime
from telegram import (Update, KeyboardButton, ReplyKeyboardMarkup,
                      InlineKeyboardButton, InlineKeyboardMarkup, Bot)
from telegram.ext import (ApplicationBuilder, CommandHandler, ContextTypes,
                          MessageHandler, filters, CallbackQueryHandler)
db = Database()
async def main_menu(update, context, id, message):
    lang = int(db.get_user(id)['lang'])
    db.add_log(chat_id=id, log=4)
    main_buttons = [
        [
            KeyboardButton(text=f"{text['main_btn']['order'][lang]}")
        ],
        [
            KeyboardButton(text=f"{text['main_btn']['history'][lang]}")
        ],
        [
            KeyboardButton(text=f"{text['main_btn']['about'][lang]}"),
            KeyboardButton(text=f"{text['main_btn']['settings'][lang]}")
        ]
    ]
    await update.message.reply_text(message, reply_markup=ReplyKeyboardMarkup(main_buttons, resize_keyboard=True,
                                                                              one_time_keyboard=True))
async def start(update, context):
    user_data = update.message.from_user
    print(user_data)
    id = user_data.id
    today = datetime.now()
    user = db.get_user(id)
    db.add_bucket(id)
    bucket_id = db.get_bucket(id)["id"]
    db.clear_bucket(bucket_id)
    if not user:
        db.add_user(chat_id=id, tg_firstname=user_data.first_name, tg_username=user_data.username,
                    joined_date=str(today))
    if not db.get_user(user_data.id)['lang']:
        db.add_log(chat_id=id, log=1)
        lang_button = [
            [
                InlineKeyboardButton(text="O'zbek🇺🇿", callback_data="lang_1"),
                InlineKeyboardButton(text="Русскый🇷🇺", callback_data='lang_2'),
                InlineKeyboardButton(text="English🇬🇧", callback_data="lang_3")
            ]
        ]
        await update.message.reply_text(
            f'''Assalomu aleykum, {user_data.first_name}! \nO'zingizga qulay tilni tanlang: 
             \nЗдравствуйте, {user_data.first_name}! \nВыберите предпочитаемый язык:
             \nHello, {user_data.first_name}! \nChoose your preferred language:
             ''',
            reply_markup=InlineKeyboardMarkup(lang_button))

    elif not db.get_user(user_data.id)['fullname']:
        lang = int(db.get_user(id)['lang'])
        db.add_log(chat_id=user_data.id, log=2)
        await update.message.reply_text(f'{text['fullname'][lang]}')
    elif not db.get_user(user_data.id)['phone_number']:
        lang = int(db.get_user(id)['lang'])
        phone_button = [
            [KeyboardButton(text=f'{text['contact_btn'][lang]}', request_contact=True)]
        ]
        db.add_log(chat_id=id, log=3)
        await update.message.reply_text(f'{text["contact_text"][lang]}',
                                        reply_markup=ReplyKeyboardMarkup(phone_button, resize_keyboard=True))
    else:
        lang = int(db.get_user(id)['lang'])
        message = text['welcome'][lang]
        await main_menu(update, context, id, message)
async def message(update, context):
    id = update.message.from_user.id
    msg = update.message.text
    log = db.get_log(chat_id=id)['log']
    lang = int(db.get_user(id)['lang'])
    if log == 2:
        db.add_user(chat_id=id, fullname=msg)
        db.add_log(chat_id=id, log=3)
        phone_button = [
            [KeyboardButton(text=f"{text['contact_btn'][lang]}", request_contact=True)]
        ]
        db.add_log(chat_id=id, log=3)
        await update.message.reply_text(f'{text["contact_text"][lang]}',
                                        reply_markup=ReplyKeyboardMarkup(phone_button, resize_keyboard=True))
    elif log == 3:
        isTrue = False
        for i in msg[4:]:
            if ord(i) not in range(48, 58):
                isTrue = True
                break
        if len(msg) != 13 or msg[:4] != "+998" or isTrue:
            await update.message.reply_text(f'{text['contact_change'][lang][3]}')
        else:
            db.add_user(chat_id=id, phone_number=msg)
            message = text['success'][lang]
            await main_menu(update, context, id, message)
    elif log == 4:
        if msg == f'{text['main_btn']['settings'][lang]}':
            await update.message.reply_text(f'{text['settings'][lang]}')
        elif msg == f'{text['main_btn']['about'][lang]}':
            await update.message.reply_text(f'{text['about'][lang]}')
        elif msg == f'{text['main_btn']['order'][lang]}':
            db.add_log(chat_id=id, log=100)
            categories = db.get_category()
            category_buttons = []
            temp_button = []
            for category in categories:
                temp_button.append(
                    InlineKeyboardButton(text=category["name"], callback_data=f'category_{category["id"]}'))
                if len(temp_button) == 2:
                    category_buttons.append(temp_button)
                    temp_button = []
            if temp_button:
                category_buttons.append(temp_button)

            bucket_id = db.get_bucket(id)['id']
            items = db.get_bucket_item(bucket_id)
            if not items:
                category_buttons.append(
                    [InlineKeyboardButton(text=f"{text["back_btn"][lang]}", callback_data="category_back")])
                await update.message.reply_photo(photo=open("Photos/main_menu.jpg", 'rb'),
                                             caption=f"{text["category_choose"][lang]}",
                                             reply_markup=InlineKeyboardMarkup(category_buttons))
            else:
                category_buttons.append(
                    [InlineKeyboardButton(text=f"{text["bucket_btn"][lang]}", callback_data=f"bucket_user_{bucket_id}")])
                category_buttons.append(
                    [InlineKeyboardButton(text=f"{text["back_btn"][lang]}", callback_data="category_back")])
                msg = f"{text["bucket_items"][lang][0]}\n\n"
                price_deliveery = 10000
                price_total = 10000
                for item in items:
                    msg += f"\t\t🟡{item["count"]}x {item["product_name"]}\n"
                    price_total += item['price'] * item["count"]
                msg += "\n"
                msg += f"{text["bucket_items"][lang][1]} {price_total - price_deliveery} {text["bucket_items"][lang][-1]}\n{text["bucket_items"][lang][2]} {price_deliveery} {text["bucket_items"][lang][-1]}\n{text["bucket_items"][lang][3]} {price_total}{text["bucket_items"][lang][-1]}"
                await update.message.reply_text(text=msg,
                                                 reply_markup=InlineKeyboardMarkup(category_buttons))
        elif msg == f"{text["main_btn"]["history"][lang]}":
            orders = db.get_orders(id)
            if not orders:
                await update.message.reply_text(text=f"{text["history"][lang][0]}")
            else:
                for order in orders:
                    order_id = order["id"]
                    order_items = db.get_order_item(order_id)
                    msg = f'{text["history"][lang][1]} {order_id}\n\n'
                    delivery_price = 10000
                    total_price = 0
                    for order_item in order_items:
                        msg += f"🟡<b>{order_item["product_name"]}</b>\n\t\t{order_item["count"]} x {order_item["price"]} = {order_item["count"]*order_item["price"]} {text["bucket_items"][lang][-1]}\n"
                        total_price += order_item["price"] * order_item["count"]
                    msg += f"\n\n\n{text["bucket_items"][lang][1]} {total_price} {text["bucket_items"][lang][-1]}\n{text["bucket_items"][lang][2]} {delivery_price} {text["bucket_items"][lang][-1]}\n{text["bucket_items"][lang][3]} {total_price + delivery_price}{text["bucket_items"][lang][-1]}"
                    cancel_btn = [
                        [InlineKeyboardButton(text=f"{text["cancel"][lang]}", callback_data="cancel")]
                    ]
                    await update.message.reply_text(text = msg, reply_markup= InlineKeyboardMarkup(cancel_btn), parse_mode="HTML")
    elif log == 6:
        isTrue = False
        for i in msg[4:]:
            if ord(i) not in range(48, 58):
                isTrue = True
                break
        if len(msg) != 13 or msg[:4] != "+998" or isTrue:
            await update.message.reply_text(f'{text['contact_change'][lang][3]}')
        else:
            db.add_user(chat_id=id, phone_number=msg)
            message = text['contact_change'][lang][2]
            await main_menu(update, context, id)
    elif log == 7:
        db.add_user(chat_id=id, fullname=msg)
        message = text['fullname_change'][lang][2]
        await main_menu(update, context, id)
async def contact(update, context):
    phone_number = update.message.contact.phone_number
    id = update.message.chat.id
    log = db.get_log(id)["log"]
    lang = int(db.get_user(id)['lang'])
    db.add_user(chat_id=id, phone_number=str(phone_number))
    if log == 3:
        message = text['success'][lang]
    elif log == 6:
        message = text['contact_change'][lang][2]
    await main_menu(update, context, id, message)
async def callback(update, context):
    update = update.callback_query
    id = update.from_user.id
    query = update.data.split('_')
    message_id = update.message.message_id
    if query[0] == 'lang':
        db.add_log(chat_id=id, log=2)
        await context.bot.delete_message(chat_id=id, message_id=message_id)
        db.add_user(chat_id=id, lang=int(query[1]))
        lang = int(db.get_user(id)['lang'])
        await update.message.reply_text(f'{text['fullname'][lang]}')
    elif query[0] == 'langChange':
        await context.bot.delete_message(chat_id=id, message_id=message_id)
        db.add_user(chat_id=id, lang=int(query[1]))
        lang = int(db.get_user(id)['lang'])
        message = text['set_lang'][lang]
        await main_menu(update, context, id, message)
    elif query[0] == "category":
        lang = int(db.get_user(id)['lang'])
        if query[1] != "back":
            db.add_log(chat_id=id, log=101)
            await context.bot.delete_message(chat_id=id, message_id=message_id)
            products = db.get_products(int(query[1]))
            category_photo = products[0]["category_photo"]
            products_buttons = []
            temp_button = []
            for product in products:
                temp_button.append(
                    InlineKeyboardButton(text=product["product_name"], callback_data=f'products_{product["id"]}'))
                if len(temp_button) == 2:
                    products_buttons.append(temp_button)
                    temp_button = []
            if temp_button:
                products_buttons.append(temp_button)
            products_buttons.append(
                [InlineKeyboardButton(text=f"{text["back_btn"][lang]}", callback_data="products_back")])
            await update.message.reply_photo(photo=open(f"{category_photo}", 'rb'),
                                                 caption=f"{text["products_choose"][lang]}",
                                                 reply_markup=InlineKeyboardMarkup(products_buttons))


        else:
            message = f'{text["menu_choose"][lang]}'
            await context.bot.delete_message(chat_id=id, message_id=message_id)
            db.add_log(chat_id=id, log=4)
            await main_menu(update, context, id, message)
    elif query[0] == 'products':
        lang = int(db.get_user(id)['lang'])
        if query[1] != 'back':
            db.add_log(chat_id=id, log=102)
            product_id = int(query[1])
            await context.bot.delete_message(chat_id=id, message_id=message_id)
            product = db.get_product(product_id)
            quantity = 1
            d_button = [
                [
                    InlineKeyboardButton(text="➖", callback_data=f"product_detail_desc_{product_id}_{quantity}"),
                    InlineKeyboardButton(text=f"{quantity}", callback_data="product_quantity"),
                    InlineKeyboardButton(text="➕", callback_data=f"product_detail_asc_{product_id}_{quantity}")
                ],
                [
                    InlineKeyboardButton(text=f"{text["add_bucket"][lang]}",
                                         callback_data=f"product_bucket_{db.get_bucket(id)["id"]}_{product_id}_{quantity}")
                ],
                [
                    InlineKeyboardButton(text=f"{text["back_btn"][lang]}",
                                         callback_data=f"product_back_{product["category_id"]}")
                ]
            ]

            await update.message.reply_photo(photo=open(f"{product["photo"]}", 'rb'),
                                             caption=f"{product["name"]}\n{text["product_info"][lang][0]} {product["price"]}\n{text["product_info"][lang][1]}{product["description"]}\n{text["product_info"][lang][2]}",
                                             reply_markup=InlineKeyboardMarkup(d_button))
        else:
            db.add_log(chat_id=id, log=100)
            await context.bot.delete_message(chat_id=id, message_id=message_id)
            categories = db.get_category()
            category_buttons = []
            temp_button = []
            for category in categories:
                temp_button.append(
                    InlineKeyboardButton(text=category["name"], callback_data=f'category_{category["id"]}'))
                if len(temp_button) == 2:
                    category_buttons.append(temp_button)
                    temp_button = []
            if temp_button:
                category_buttons.append(temp_button)

            bucket_id = db.get_bucket(id)['id']
            items = db.get_bucket_item(bucket_id)
            if not items:
                category_buttons.append(
                    [InlineKeyboardButton(text=f"{text["back_btn"][lang]}", callback_data="category_back")])
                await update.message.reply_photo(photo=open("Photos/main_menu.jpg", 'rb'),
                                                 caption=f"{text["category_choose"][lang]}",
                                                 reply_markup=InlineKeyboardMarkup(category_buttons))
            else:
                category_buttons.append(
                    [InlineKeyboardButton(text=f"{text["bucket_btn"][lang]}", callback_data=f"bucket_user_{bucket_id}")])
                category_buttons.append(
                    [InlineKeyboardButton(text=f"{text["back_btn"][lang]}", callback_data="category_back")])
                msg = f"{text["bucket_items"][lang][0]}\n\n"
                price_deliveery = 10000
                price_total = 10000
                for item in items:
                    msg += f"\t\t🟡{item["count"]}x {item["product_name"]}\n"
                    price_total += item['price'] * item["count"]
                msg += "\n"
                msg += f"{text["bucket_items"][lang][1]} {price_total - price_deliveery} {text["bucket_items"][lang][-1]}\n{text["bucket_items"][lang][2]} {price_deliveery} {text["bucket_items"][lang][-1]}\n{text["bucket_items"][lang][3]} {price_total}{text["bucket_items"][lang][-1]}"
                await update.message.reply_text(text=msg,
                                                reply_markup=InlineKeyboardMarkup(category_buttons))
    elif query[0] == "product":
        lang = int(db.get_user(id)['lang'])
        if query[1] == "back":
            db.add_log(chat_id=id, log=101)
            await context.bot.delete_message(chat_id=id, message_id=message_id)
            products = db.get_products(int(query[2]))
            category_photo = products[0]["category_photo"]
            products_buttons = []
            temp_button = []
            for product in products:
                temp_button.append(
                    InlineKeyboardButton(text=product["product_name"], callback_data=f'products_{product["id"]}'))
                if len(temp_button) == 2:
                    products_buttons.append(temp_button)
                    temp_button = []
            if temp_button:
                products_buttons.append(temp_button)
            products_buttons.append(
                [InlineKeyboardButton(text=f"{text["back_btn"][lang]}", callback_data="products_back")])

            await update.message.reply_photo(photo=open(f"{category_photo}", 'rb'),
                                                 caption=f"{text["products_choose"][lang]}",
                                                 reply_markup=InlineKeyboardMarkup(products_buttons))

        elif query[1] == "detail":
            if query[2] == "asc":
                product = db.get_product(int(query[3]))
                quantity = int(query[4]) + 1
                d_button = [
                    [
                        InlineKeyboardButton(text="➖", callback_data=f"product_detail_desc_{query[3]}_{quantity}"),
                        InlineKeyboardButton(text=f"{quantity}", callback_data="product_quantity"),
                        InlineKeyboardButton(text="➕", callback_data=f"product_detail_asc_{query[3]}_{quantity}")
                    ],
                    [
                        InlineKeyboardButton(text=f"{text["add_bucket"][lang]}",
                                             callback_data=f"product_bucket_{db.get_bucket(id)["id"]}_{product["id"]}_{quantity}")
                    ],
                    [
                        InlineKeyboardButton(text=f"{text["back_btn"][lang]}",
                                             callback_data=f"product_back_{product["category_id"]}")
                    ]
                ]
                await context.bot.edit_message_reply_markup(chat_id=id, message_id=message_id,
                                                            reply_markup=InlineKeyboardMarkup(d_button))
                await context.bot.edit_message_caption(chat_id=id, message_id=message_id,
                                                       caption=f"{product["name"]} {quantity}x\n{text["product_info"][lang][0]} {product["price"]} x {quantity} = {product["price"] * quantity}\n{text["product_info"][lang][1]}{product["description"]}\n{text["product_info"][lang][2]}",
                                                       reply_markup=InlineKeyboardMarkup(d_button))
            else:
                product = db.get_product(int(query[3]))
                quantity = int(query[4])
                if int(query[4]) > 1:
                    quantity = int(query[4]) - 1
                d_button = [
                    [
                        InlineKeyboardButton(text="➖", callback_data=f"product_detail_desc_{query[3]}_{quantity}"),
                        InlineKeyboardButton(text=f"{quantity}", callback_data="product_quantity"),
                        InlineKeyboardButton(text="➕", callback_data=f"product_detail_asc_{query[3]}_{quantity}")
                    ],
                    [
                        InlineKeyboardButton(text=f"{text["add_bucket"][lang]}",
                                             callback_data=f"product_bucket_{db.get_bucket(id)["id"]}_{product["id"]}_{quantity}")
                    ],
                    [
                        InlineKeyboardButton(text=f"{text["back_btn"][lang]}",
                                             callback_data=f"product_back_{product["category_id"]}")
                    ]
                ]

                await context.bot.edit_message_reply_markup(chat_id=id, message_id=message_id,
                                                            reply_markup=InlineKeyboardMarkup(d_button))
                if quantity > 1:
                    await context.bot.edit_message_caption(chat_id=id, message_id=message_id,
                                                           caption=f"{product["name"]} {quantity}x\n{text["product_info"][lang][0]} {product["price"]} x {quantity} = {product["price"] * quantity}\n{text["product_info"][lang][1]}{product["description"]}\n{text["product_info"][lang][2]}",
                                                           reply_markup=InlineKeyboardMarkup(d_button))
                else:
                    await context.bot.edit_message_caption(chat_id=id, message_id=message_id,
                                                           caption=f"{product["name"]}\n{text["product_info"][lang][0]} {product["price"]}\n{text["product_info"][lang][1]}{product["description"]}\n{text["product_info"][lang][2]}",
                                                           reply_markup=InlineKeyboardMarkup(d_button))
        elif query[1] == "bucket":
            print("log worked....")
            bucket_id = int(query[2])
            db.add_bucket_item(bucket_id, int(query[3]), int(query[4]))
            db.add_log(chat_id=id, log=100)
            await context.bot.delete_message(chat_id=id, message_id=message_id)
            categories = db.get_category()
            category_buttons = []
            temp_button = []
            for category in categories:
                temp_button.append(
                    InlineKeyboardButton(text=category["name"], callback_data=f'category_{category["id"]}'))
                if len(temp_button) == 2:
                    category_buttons.append(temp_button)
                    temp_button = []
            if temp_button:
                category_buttons.append(temp_button)

            bucket_id = db.get_bucket(id)['id']
            items = db.get_bucket_item(bucket_id)
            if not items:
                category_buttons.append(
                    [InlineKeyboardButton(text=f"{text["back_btn"][lang]}", callback_data="category_back")])
                await update.message.reply_photo(photo=open("Photos/main_menu.jpg", 'rb'),
                                                 caption=f"{text["category_choose"][lang]}",
                                                 reply_markup=InlineKeyboardMarkup(category_buttons))
            else:
                category_buttons.append(
                    [InlineKeyboardButton(text=f"{text["bucket_btn"][lang]}", callback_data=f"bucket_user_{bucket_id}")])
                category_buttons.append(
                    [InlineKeyboardButton(text=f"{text["back_btn"][lang]}", callback_data="category_back")])
                msg = f"{text["bucket_items"][lang][0]}\n\n"
                price_deliveery = 10000
                price_total = 10000
                for item in items:
                    msg += f"\t\t🟡{item["count"]}x {item["product_name"]}\n"
                    price_total += item['price'] * item["count"]
                msg += "\n"
                msg += f"{text["bucket_items"][lang][1]} {price_total - price_deliveery} {text["bucket_items"][lang][-1]}\n{text["bucket_items"][lang][2]} {price_deliveery} {text["bucket_items"][lang][-1]}\n{text["bucket_items"][lang][3]} {price_total}{text["bucket_items"][lang][-1]}"
                await update.message.reply_text(text=msg,
                                                reply_markup=InlineKeyboardMarkup(category_buttons))
    elif query[0] == "bucket":
        if query[1] == "user":
            lang = int(db.get_user(id)['lang'])
            bucket_id = int(query[2])
            items = db.get_bucket_item(bucket_id)
            await context.bot.delete_message(chat_id=id, message_id=message_id)
            items_btn = []

            items_btn.append(
                [
                    InlineKeyboardButton(text=f"{text["back_btn"][lang]}", callback_data="products_back"),
                    InlineKeyboardButton(text=f"{text["bucket_inside_btn"][lang][0]}", callback_data=f"order_{id}_{bucket_id}")
                ]
            )
            items_btn.append(
                [
                    InlineKeyboardButton(text=f"{text["bucket_inside_btn"][lang][1]}",
                                         callback_data=f"bucket_clear_{bucket_id}")
                ]
            )
            msg = f"{text["bucket_items"][lang][0]}\n\n"
            price_delivery = 10000
            price_total = 10000
            for item in items:
                temp_btn = [
                    InlineKeyboardButton(text = "➖", callback_data=f'bucket_item_desc_{item["id"]}_{item["count"]}_{bucket_id}'),
                    InlineKeyboardButton(text = f"{item["product_name"]}", callback_data= f"bucket_product_{item["product_id"]}"),
                    InlineKeyboardButton(text = "➕", callback_data= f'bucket_item_asc_{item["id"]}_{item["count"]}_{bucket_id}')
                ]
                items_btn.append(temp_btn)
                msg += f"\t\t🟡{item["count"]}x {item["product_name"]}\n"
                price_total += item['price'] * item["count"]
            msg += "\n"
            msg += f"{text["bucket_items"][lang][1]} {price_total - price_delivery} {text["bucket_items"][lang][-1]}\n{text["bucket_items"][lang][2]} {price_delivery} {text["bucket_items"][lang][-1]}\n{text["bucket_items"][lang][3]} {price_total}{text["bucket_items"][lang][-1]}"
            await update.message.reply_text(text=msg,
                                            reply_markup=InlineKeyboardMarkup(items_btn))
        elif query[1] == "clear":
            lang = int(db.get_user(id)['lang'])
            await context.bot.delete_message(chat_id=id, message_id=message_id)
            db.clear_bucket(int(query[2]))
            db.add_log(chat_id=id, log=100)
            categories = db.get_category()
            category_buttons = []
            temp_button = []
            for category in categories:
                temp_button.append(
                    InlineKeyboardButton(text=category["name"], callback_data=f'category_{category["id"]}'))
                if len(temp_button) == 2:
                    category_buttons.append(temp_button)
                    temp_button = []
            if temp_button:
                category_buttons.append(temp_button)

            bucket_id = db.get_bucket(id)['id']
            items = db.get_bucket_item(bucket_id)
            if not items:
                category_buttons.append(
                    [InlineKeyboardButton(text=f"{text["back_btn"][lang]}", callback_data="category_back")])
                await update.message.reply_photo(photo=open("Photos/main_menu.jpg", 'rb'),
                                                 caption=f"{text["category_choose"][lang]}",
                                                 reply_markup=InlineKeyboardMarkup(category_buttons))
            else:
                category_buttons.append(
                    [InlineKeyboardButton(text=f"{text["bucket_btn"][lang]}",
                                          callback_data=f"bucket_user_{bucket_id}")])
                category_buttons.append(
                    [InlineKeyboardButton(text=f"{text["back_btn"][lang]}", callback_data="category_back")])
                msg = f"{text["bucket_items"][lang][0]}\n\n"
                price_deliveery = 10000
                price_total = 10000
                for item in items:
                    msg += f"\t\t🟡{item["count"]}x {item["product_name"]}\n"
                    price_total += item['price'] * item["count"]
                msg += "\n"
                msg += f"{text["bucket_items"][lang][1]} {price_total - price_deliveery} {text["bucket_items"][lang][-1]}\n{text["bucket_items"][lang][2]} {price_deliveery} {text["bucket_items"][lang][-1]}\n{text["bucket_items"][lang][3]} {price_total}{text["bucket_items"][lang][-1]}"
                await update.message.reply_text(text=msg,
                                                reply_markup=InlineKeyboardMarkup(category_buttons))
        elif query[1] == "item":
            item_id = int(query[3])
            count = int(query[4])
            if query[2] == "asc":
                db.update_item(item_id,count + 1)
            else:
                if count == 1:
                    db.clear_item(item_id)
                else:
                    db.update_item(item_id, count - 1)
            lang = int(db.get_user(id)['lang'])
            bucket_id = int(query[5])
            items = db.get_bucket_item(bucket_id)
            items_btn = []

            items_btn.append(
                [
                    InlineKeyboardButton(text=f"{text["back_btn"][lang]}", callback_data="products_back"),
                    InlineKeyboardButton(text=f"{text["bucket_inside_btn"][lang][0]}",
                                         callback_data=f"order_{id}_{bucket_id}")
                ]
            )
            items_btn.append(
                [
                    InlineKeyboardButton(text=f"{text["bucket_inside_btn"][lang][1]}",
                                         callback_data=f"bucket_clear_{bucket_id}")
                ]
            )
            msg = f"{text["bucket_items"][lang][0]}\n\n"
            price_delivery = 10000
            price_total = 10000
            for item in items:
                temp_btn = [
                    InlineKeyboardButton(text="➖",
                                         callback_data=f'bucket_item_desc_{item["id"]}_{item["count"]}_{bucket_id}'),
                    InlineKeyboardButton(text=f"{item["product_name"]}",
                                         callback_data=f"bucket_product_{item["product_id"]}"),
                    InlineKeyboardButton(text="➕",
                                         callback_data=f'bucket_item_asc_{item["id"]}_{item["count"]}_{bucket_id}')
                ]
                items_btn.append(temp_btn)
                msg += f"\t\t🟡{item["count"]}x {item["product_name"]}\n"
                price_total += item['price'] * item["count"]
            msg += "\n"
            msg += f"{text["bucket_items"][lang][1]} {price_total - price_delivery} {text["bucket_items"][lang][-1]}\n{text["bucket_items"][lang][2]} {price_delivery} {text["bucket_items"][lang][-1]}\n{text["bucket_items"][lang][3]} {price_total}{text["bucket_items"][lang][-1]}"
            await context.bot.edit_message_text(chat_id=id, message_id=message_id,
                                                   text=msg,
                                                   reply_markup=InlineKeyboardMarkup(items_btn))
    elif query[0] == "order":
        lang = int(db.get_user(id)['lang'])
        await context.bot.delete_message(chat_id=id, message_id=message_id)
        bucket_id = int(query[2])
        items = db.get_bucket_item(bucket_id)
        price = 0
        for item in items:
            price += item["price"] * item["count"]
        today = str(datetime.now())
        order_id = db.add_order(id,price,today)

        for item in items:

            db.add_order_item(order_id["id"],item["product_id"],item["count"])

        msg = f"{text["order_success"][lang]}"
        db.clear_bucket(bucket_id)
        await main_menu(update, context, id, msg)
    elif query[0] == "cancel":
        await context.bot.delete_message(chat_id=id, message_id=message_id)
async def lang(update, context):
    user_data = update.message.from_user
    id = user_data.id
    lang = int(db.get_user(id)['lang'])
    lang_button = [
        [
            InlineKeyboardButton(text="O'zbek🇺🇿", callback_data="langChange_1"),
            InlineKeyboardButton(text="Русскый🇷🇺", callback_data='langChange_2'),
            InlineKeyboardButton(text="English🇬🇧", callback_data="langChange_3")
        ]
    ]
    await update.message.reply_text(
        f'''{text['set_lang_before'][lang]} {text['lang'][lang]} \n{text['change_lang'][lang]}''',
        reply_markup=InlineKeyboardMarkup(lang_button))
async def phone(update, context):
    user_data = update.message.from_user
    id = user_data.id
    lang = int(db.get_user(id)['lang'])
    phone_number = db.get_user(id)['phone_number']
    phone_button = [
        [KeyboardButton(text=f"{text['contact_btn'][lang]}", request_contact=True)]
    ]
    db.add_log(chat_id=id, log=6)
    await update.message.reply_text(
        f'{text["contact_change"][lang][0]} {phone_number} \n{text["contact_change"][lang][1]}',
        reply_markup=ReplyKeyboardMarkup(phone_button, resize_keyboard=True))
async def fullname(update, context):
    user_data = update.message.from_user
    id = user_data.id
    lang = int(db.get_user(id)['lang'])
    fullname = db.get_user(id)['fullname']
    db.add_log(chat_id=id, log=7)
    await update.message.reply_text(
        f'{text["fullname_change"][lang][0]} {fullname} \n{text["fullname_change"][lang][1]}')

app = ApplicationBuilder().token("6771328121:AAFGqcQ56QTszwWIQJjkJ8wtmRFUHk34irY").build()

app.add_handler(CommandHandler(command="start", callback=start))
app.add_handler(CommandHandler(command="lang", callback=lang))
app.add_handler(CommandHandler(command="phone", callback=phone))
app.add_handler(CommandHandler(command="fullname", callback=fullname))
app.add_handler(MessageHandler(filters=filters.TEXT, callback=message))
app.add_handler(MessageHandler(filters=filters.CONTACT, callback=contact))
app.add_handler(CallbackQueryHandler(callback))

app.run_polling()
