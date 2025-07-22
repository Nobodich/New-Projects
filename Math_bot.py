import telebot
import Math_bot_token
from telebot.types import *
bot = telebot.TeleBot(Math_bot_token.token)
sum_icon = "https://cdn-icons-png.flaticon.com/512/32/32306.png"
temp = {}


@bot.inline_handler(func=lambda query: len(query.query) >= 1)
def que(query: InlineQuery):
    if query.query == "Кот":
        img = InlineQueryResultPhoto('1', 'https://raw.githubusercontent.com/eternnoir/pyTelegramBotAPI/'
                                         'master/examples/detailed_example/kitten.jpg',
                              "https://raw.githubusercontent.com/eternnoir/pyTelegramBotAPI/"
                                         "master/examples/detailed_example/kitten.jpg",
                                          input_message_content=InputTextMessageContent("https://raw.githubusercontent."
                                                                                       "com/eternnoir/pyTelegramBotAPI/"
                                                                         "master/examples/detailed_example/kitten.jpg"))
        bot.answer_inline_query(query.id, [img])
        return
    text = query.query.split(" ")
    ur = None
    if "x" in text:
        if text[1] == "+":
            ur = int(text[4]) - int(text[2])
        elif text[1] == "-":
            ur = int(text[4]) + int(text[2])
        elif text[1] == "*":
            ur = int(text[4]) / int(text[2])
        elif text[1] == "/":
            ur = int(text[4]) * int(text[2])
        answ = InlineQueryResultArticle("4", "Уравнение", description=f"Ответ: {ur}",
                                        input_message_content=
                                        InputTextMessageContent
                                        (f"{text[0]} = {ur}"))
        bot.answer_inline_query(query.id, [answ])
        return
    text = tuple(map(float, text))
    summ = sum(text)
    diff = text[0]
    for el in text[1:]:
        diff -= el
    mult = text[0]
    for el in text[1:]:
        mult *= el
    quo = text[0]
    for el in text[1:]:
        quo /= el
    ext = text[0]
    for el in text[1:]:
        ext **= el
    root = text[0]
    root **= 0.5
    answ_1 = InlineQueryResultArticle("1", "Сумма", description=f"Ответ: {summ}",
                                      input_message_content=
                                      InputTextMessageContent
                                      (f"{text[0]} {"".join([f" + {i}" for i in text[1:]])} = {summ}"),
                                      thumbnail_url=sum_icon)
    answ_2 = InlineQueryResultArticle('2', "Разность", description=f"Результат: {diff}",
                                           input_message_content=InputTextMessageContent(
                                               f"{text[0]} {''.join([f' - {i}' for i in text[1:]])} = {diff}"),
                                      thumbnail_url="https://cdn-icons-png.flaticon.com/512/6660/6660207.png")
    answ_3 = InlineQueryResultArticle('3', "Произведение", description=f"Результат: {mult}",
                                           input_message_content=InputTextMessageContent(
                                               f"{text[0]} {''.join([f' * {i}' for i in text[1:]])} = {mult}"),
                                      thumbnail_url="https://cdn-icons-png.flaticon.com/512/43/43165.png")
    answ_4 = InlineQueryResultArticle('4', "Частное", description=f"Результат: {quo}",
                                           input_message_content=InputTextMessageContent(
                                               f"{text[0]} {''.join([f' / {i}' for i in text[1:]])} = {quo}"),
                                      thumbnail_url="https://img.freepik.com/premium-vector/"
                                                    "division-symbol-basic-mathematical-symbols-sign-calculator-button-"
                                                    "icon-business-finance-concept_949349-35.jpg")
    answ_5 = InlineQueryResultArticle('5', "Степень", description=f"Результат: {ext}",
                                      input_message_content=InputTextMessageContent(
                                          f"{text[0]} {''.join([f' / {i}' for i in text[1:]])} = {ext}"),
                                      thumbnail_url="https://encrypted-tbn0.gstatic.com/"
                                                    "images?q=tbn:ANd9GcRSLdvJbLjiMRZcDUS7nBWtZ_NXQAuyyxHaeg&s")
    answ_6 = InlineQueryResultArticle('6', "Корень", description=f"Результат: {root}",
                                      input_message_content=InputTextMessageContent(
                                          f"√{text[0]} = {root}"),
                                      thumbnail_url="https://cdn-icons-png.flaticon.com/512/2/2223.png")
    bot.answer_inline_query(query.id, [answ_1, answ_2, answ_3, answ_4, answ_5, answ_6])


@bot.message_handler(["start"])
def start(msg: Message):
    bot.send_message(msg.chat.id, f"Пользователь {msg.from_user.id} отправил сообщение в группу {msg.chat.id}")


@bot.message_handler(content_types=['text'])
def math(msg: Message, repeat=False):
    global temp
    if msg.text.lower().startswith("mathbot"):
        temp["математик"] = msg.from_user.id
        bot.send_message(msg.chat.id, "Чем помочь?")
        bot.register_next_step_handler(msg, math_handler)
    if repeat:
        bot.register_next_step_handler(msg, math_handler)


def math_handler(msg: Message):
    global temp
    if temp["математик"] != msg.from_user.id:
        math(msg, True)
        return
    bot.send_message(msg.chat.id, f"{eval(msg.text)}")


bot.infinity_polling()
