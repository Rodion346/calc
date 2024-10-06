import ccxt, json, os

from core.models.db_helper import db_helper
from core.repositories.channel import ChannelRepository


"""
    Данный файл ищет в диалогах новые сигналы
"""

channelRepo = ChannelRepository(db_helper.session_getter)

cr_conf = {
    "ID": 2043093596,
    "Channel_name": "ZERO TEST",
    "Channel_link": "https://t.me/+tX9FjzvJNBI2NjVi",
    "Admin": "NONE",
    "Workspace": "none",
    "Rate": 50,
    "Confidence_rate": 50,
    "Signal_rate": 50,
    "Coin": None,
    "Trand_long": None,
    "Trand_short": None,
    "Leverage": None,
    "Margin_type": None,
    "Entrance_point_tvh": None,
    "Entrance_point_lvh": None,
    "Entrance_point_rvh": None,
    "Take_profit": None,
    "Stop_loss": None,
    "def_Coin": None,
    "def_Trand": None,
    "def_Leverage": None,
    "def_Margin_type": None,
    "def_Entrance_point": None,
    "def_Take_profit": None,
    "def_Stop_loss": None,
}


async def parser(message, markets, channel):
    try:
        """
        Данная функция получает и выводит всю информацию об каналах активных папок
        """

        """
        РАБОТА С КОНФИГ ФАЙЛАМИ
        по умолчанию используется конфигурация канала, если конфигурация отсутствует, то используется общий конфиг
        """

        # Разметка для папки с конфигами
        channels_configs_path = os.path.join(os.getcwd(), "channels_configs")

        # Получить список ключ-значение из общего конфига
        general_config_path = os.path.join(channels_configs_path, "config.json")
        if not os.path.exists(general_config_path):
            raise FileNotFoundError(
                f"General config file not found at {general_config_path}"
            )

        with open(general_config_path, "r") as f:
            channel_data = json.load(f)

        # Получить список ключ-значение из конфига для канала с id "channel_id"
        channel_config_path = os.path.join(
            channels_configs_path, str(channel.id), "config.json"
        )
        channel_path = os.path.join(channels_configs_path, str(channel.id))

        # Создаем папку, если она не существует
        if not os.path.exists(channel_path):
            os.makedirs(channel_path)

        # Создаем файл конфигурации с заданным содержимым, если его нет
        if not os.path.exists(channel_config_path):
            with open(channel_config_path, "w") as f:
                cr_conf["ID"] = channel.id
                cr_conf["Channel_name"] = channel.title
                cr_conf["Channel_link"] = None
                json.dump(cr_conf, f, indent=4)

        with open(channel_config_path, "r") as f:
            key_words = json.load(f)
            # Перебор значений конфига
            for key, value in key_words.items():
                # Если значение по умолчанию не установлено и ключ есть в общем конфиге, то берем его значение
                if value is None and key in channel_data:
                    key_words[key] = channel_data[key]

        message_lowercase = message.lower()

        coin = ""
        splited_market = []

        # Проверка есть ли коин в сообщении
        for market in markets:
            # Получить коин из базы
            splited_market.append(market.split("/")[0].lower())

        # Проверяем, если полученный коин из базы не usdt и равен ли коин с тем что получаем при удалении ненужного из слова
        for word in message_lowercase.split():
            # Удаляем все кроме букв
            r_word = ""
            for char in word:
                if char.isalpha():
                    r_word += char

            # Проверяем является ли полученное слово коином
            if r_word.lower().replace("usdt", "") in splited_market:
                coin = r_word.lower().replace("usdt", "").upper()
        if coin == "":
            return  # Если коина не было найдено, то пропустить это сообщение

        """    ПОИСК ТРЕНДА    """
        trand = ""

        for long in key_words[
            "Trand_long"
        ]:  # Получаем из словаря ключевые слова для ТРЕНДА ЛОНГ
            if (
                long in message_lowercase
            ):  # Проверка есть ли ключевые слова long в сообщении
                trand = "LONG"  # Назначаем переменной тренд ЛОНГ
                break

        for short in key_words[
            "Trand_short"
        ]:  # Получаем из словаря ключевые слова для ТРЕНДА ШОРТ
            if (
                short in message_lowercase
            ):  # Проверка есть ли ключевые слова short в сообщении
                trand = "SHORT"  # Назначаем переменной тренд ШОРТ
                break

        if trand == "":
            return  # Если не было найдено ни того ни другого, то пропустить

        tvh_result = await tvh_checker(message_lowercase, key_words)
        if not tvh_result:
            return  # Если вернуло фалс значит это уже не сигнал
        else:
            # Если все данные нормальные и это явялется сигналом, то ищем второстепенные данные
            # Добавляем словарь для удаления ненужного для тейк поинта
            if tvh_result["rvh"] and not tvh_result["tvh"]:
                tvh_result["rvh"] = False

                exchange = ccxt.binance()
                ticker = exchange.fetch_ticker(f"{coin}/USDT")
                price = ticker["last"]
                tvh_result["tvh"] = price

            delete_words = []
            for key in key_words["Stop_loss"]:
                delete_words.append(key)
            for key in key_words["Leverage"]:
                delete_words.append(key)
            for key in key_words["Margin_type"]:
                delete_words.append(key)
            for key in key_words["Entrance_point_tvh"]:
                delete_words.append(key)
            for key in key_words["Entrance_point_lvh"]:
                delete_words.append(key)
            for key in key_words["Entrance_point_rvh"]:
                delete_words.append(key)

            take_profits = await tp_checker(
                message_lowercase, key_words["Take_profit"], delete_words
            )
            stop_less = await stop_point_checker(
                message_lowercase, key_words["Stop_loss"]
            )
            leverage = await leverage_checker(message_lowercase, key_words["Leverage"])
            margin = await margin_checker(message_lowercase, key_words["Margin_type"])

            signal = {
                "Coin": coin,
                "Trand": trand,
                "Entrance_point_tvh": tvh_result["tvh"],
                "Entrance_point_rvh": tvh_result["rvh"],
                "Entrance_point_lvh": tvh_result["lvh"],
                "Take_profit": take_profits,
                "Stop_loss": stop_less,
                "Leverage": leverage,
                "Margin_type": margin,
            }

        print(signal)
        return signal
    except Exception as e:
        print(e)
        print("PARSER")
        print("___1_________E_R_R_O_R________1___")


async def tvh_checker(message_lowercase, key_words):
    tvh = ""  # Первая цифра после точки входа
    lvh = []  # После слово лимитный ордер
    rvh = False  # по рынку
    """
            Этот метод проверяет следующие значения
        Если есть вход: цифра то это ТВХ 
        Если есть вход: по рынку и цифра то это тоже ТВХ
        Если где то написано ТВХ и цифра, то это тоже ТВХ
        Если есть Вход по рынку и нету цифры то это РВХ
        Если есть лимит или лвх то это ЛВХ отдельно.
    """
    splited_message = message_lowercase.split()
    tvh_keys = key_words["Entrance_point_tvh"]
    rvh_keys = key_words["Entrance_point_rvh"]
    lvh_keys = key_words["Entrance_point_lvh"]
    tp_keys = key_words["Take_profit"]
    stop_keys = key_words["Stop_loss"]

    # Удаляем все начиная с tp
    splited_message = message_lowercase.lower().split()
    deleting_index = -1
    tvh = "0"
    tvh_list = []
    rvh = False
    lvh = []

    def checker(keys, message):
        for key in keys:
            for word in message:
                if key in word:
                    return message.index(word)
        return -1

    # Находим ключевое слово тп
    # Найти index твх
    tvh_index = checker(tvh_keys, splited_message)

    # Если не найден твх попробовать рвх или лвх
    if tvh_index == -1:
        tvh_index = checker(lvh_keys, splited_message)
    if tvh_index == -1:
        tvh_index = checker(rvh_keys, splited_message)
    deleting_index = -1
    for key in tp_keys:
        for word in splited_message:
            if key in word:
                if (
                    deleting_index != -1
                    and deleting_index > splited_message.index(word)
                    and splited_message.index(word) > tvh_index
                ):
                    deleting_index = splited_message.index(word)
                elif deleting_index == -1:
                    deleting_index = splited_message.index(word)

    # Если не было тп, то найти стопы
    for key in stop_keys:
        for word in splited_message:
            if key in word:
                if (
                    deleting_index != -1
                    and deleting_index > splited_message.index(word)
                    and splited_message.index(word) > tvh_index
                ):
                    deleting_index = splited_message.index(word)
                elif deleting_index == -1:
                    deleting_index = splited_message.index(word)

    # Найти все слова для удаления
    deleting_words = []
    if tvh_index != -1:
        for i in range(0, tvh_index):
            deleting_words.append(splited_message[i])
    if deleting_index != -1:
        for i in range(deleting_index, len(splited_message)):
            deleting_words.append(splited_message[i])

    # Удалить все ненужное
    clear_message = []
    for word in splited_message:
        if word not in deleting_words:
            clear_message.append(word)

    # Найти ЛВХ и отделить
    lvh_list = []
    lvh_index = checker(lvh_keys, clear_message)
    if lvh_index != -1:
        for i in range(lvh_index, len(clear_message)):
            lvh_list.append(clear_message[i])
    for word in lvh_list:
        if word in clear_message:
            clear_message.remove(word)

    # Найти твх
    for word in clear_message:
        if set(word).issubset(
            {"$", "-", ",", ".", "~", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"}
        ):
            sl_word = word.split("$")[0]
            if "~" in sl_word:
                sl_word = sl_word.split("~")[1]
            tvh_list.append(sl_word)

    # Удаляем все ненужные знаки из tvh листа
    if "-" in tvh_list:
        tvh_list.remove("-")
    if "," in tvh_list:
        tvh_list.remove(".")
    if "." in tvh_list:
        tvh_list.remove(",")
    if "~" in tvh_list:
        tvh_list.remove("~")
    if "" in tvh_list:
        tvh_list.remove("")

    # Передаём нулевое значение твх потому что всегда 1ое значение это твх
    tvh_checker = "0"
    if len(tvh_list) != 0:
        tvh_checker = tvh_list[0]

    # Тк возможно твх-лвх написанное вместе, то твх разделяем на возможные варианты
    tvh_splited = tvh_checker.split("-")

    # Удаляем все ненужные знаки из tvh листа
    if "-" in tvh_splited:
        tvh_splited.remove("-")
    if "," in tvh_splited:
        tvh_splited.remove(".")
    if "." in tvh_splited:
        tvh_splited.remove(",")
    if "~" in tvh_splited:
        tvh_splited.remove("~")
    if "" in tvh_splited:
        tvh_splited.remove("")
    if tvh_checker in tvh_list:
        tvh_list.remove(tvh_checker)
    for tvh_s in tvh_splited:
        if tvh_splited.index(tvh_s) == 0:
            tvh_list = [tvh_s] + tvh_list
        else:
            tvh_list.append(tvh_s)

    # Передать очищенный твх и лвх  (лвх если есть)
    for el in tvh_list:
        if tvh_list.index(el) == 0:
            tvh = el
        else:
            lvh.append(el)

    # Найти лвх в отделенных лвх
    for word in lvh_list:
        if set(word).issubset(
            {"$", "-", ",", ".", "~", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"}
        ):
            lvh.append(word.split("$")[0])

    # Найти рвх если нету твх
    if tvh == "0":
        if checker(rvh_keys, clear_message) != -1:
            rvh = True
    if tvh == "0":
        tvh = False
    if not tvh and not rvh and lvh == []:
        return False
    else:
        return {"tvh": tvh, "rvh": rvh, "lvh": lvh}
    try:
        pass
    except Exception as e:
        print(e)
        print("ENTRY")
        print("___2_________E_R_R_O_R________2___")


async def tp_checker(message_lowercase, tp_words, delete_words):
    try:
        # Данная функция находит цели и возвращает в виде списка
        splited_message = message_lowercase.split()
        delete_index = -1
        for word in splited_message:
            for key in tp_words:
                if key in word:
                    delete_index = splited_message.index(word) - 1
                    break
            if delete_index != -1:
                break

        new_arr = []
        for word in splited_message:
            if splited_message.index(word) <= delete_index:
                new_arr.append(word)

        for word in new_arr:
            if word in splited_message:
                splited_message.remove(word)

        del_index = -1
        for word in splited_message:
            for key in delete_words:
                if key in word:
                    del_index = splited_message.index(word)
                    break
            if del_index != -1:
                break

        del_arra = []
        for word in splited_message:
            if splited_message.index(word) >= del_index:
                del_arra.append(word)

        for word in del_arra:
            if word in splited_message:
                splited_message.remove(word)

        tp_list = []
        for word in splited_message:
            if word not in ["-", "$", ".", ",", ";", ":"] and set(word).issubset(
                {
                    "$",
                    ":",
                    ";",
                    ",",
                    ".",
                    "-",
                    "0",
                    "1",
                    "2",
                    "3",
                    "4",
                    "5",
                    "6",
                    "7",
                    "8",
                    "9",
                }
            ):
                tp_list.append(word.split("$")[0])

        # Удаляем все пустые значения
        if "" in tp_list:
            tp_list.remove("")

        # Проверяем есть ли в конце ; , . : и удаляем их
        tp_list_check_arr = []
        for tp_en in tp_list:
            tp_last_point = ""
            if tp_en[len(tp_en) - 1] == ";":
                tp_last_point = ";"
            elif tp_en[len(tp_en) - 1] == ":":
                tp_last_point = ":"
            elif tp_en[len(tp_en) - 1] == ".":
                tp_last_point = "."
            elif tp_en[len(tp_en) - 1] == ",":
                tp_last_point = ","
            elif tp_en[len(tp_en) - 1] == "-":
                tp_last_point = "-"

            if tp_last_point != "":
                tp_list_check_arr.append(tp_en.split(tp_last_point)[0])
            else:
                tp_list_check_arr.append(tp_en)

        tp_list = tp_list_check_arr

        # Удаляем значения если вначале 1- 2- и тд
        tp_list_check_arr = []
        if len(tp_list) != 0:
            if "1" == tp_list[0][0] and "-" == tp_list[0][1]:
                for tp_en in tp_list:
                    tp_list_check_arr.append(tp_en.split("-")[1])

                tp_list = tp_list_check_arr

        # После всех проверок передаём все полученные значения
        if len(tp_list) != 0:
            return tp_list
        else:
            return ["Def"]

    except Exception as e:
        print(e)
        print("TARGET")
        print("___3_________E_R_R_O_R________3___")


async def stop_point_checker(message_lowercase, stop_keys):
    try:
        # Эта функция находит стоп лосс и возвращает его
        splited_message = message_lowercase.split()
        stop_less = "Def"
        stop_index = -1
        # Находим ключ стоп лесса
        for word in splited_message:
            #            print(word)
            for key in stop_keys:
                if key in word:
                    stop_index = splited_message.index(word)
                    break
            if stop_index != -1:
                break
        # Находим индекс после ключа стоп лесса
        if stop_index != -1:
            for word in splited_message:
                if splited_message.index(word) >= stop_index + 8:
                    break  # Закрываем цикл если после 4х слов не нашёл стоп лесс
                if splited_message.index(word) > stop_index:
                    if word not in ["-", "$", ".", ",", ";", ":"] and set(
                        word
                    ).issubset(
                        {
                            "$",
                            ":",
                            ";",
                            ",",
                            ".",
                            "-",
                            "0",
                            "1",
                            "2",
                            "3",
                            "4",
                            "5",
                            "6",
                            "7",
                            "8",
                            "9",
                        }
                    ):
                        if "$" in word:
                            split_word = word.split("$")
                            split_word = [part for part in split_word if part]
                            word = split_word[0]
                        stop_less = word
                        break
        return stop_less
    except Exception as e:
        print(e)
        print("STOP")
        print("___4_________E_R_R_O_R________4___")


async def leverage_checker(message_lowercase, leverage_keys):  # Функция поиска LEVERAGE
    try:
        splited_message = message_lowercase.lower().split()
        # Проверить слова на формат цифра X
        leverage = "Def"
        for (
            word
        ) in (
            splited_message
        ):  # запускаем цикл проверки наличия значение word в splited_message
            if "x" in word or "х" in word:  # проверяем наличие значения х в word
                index = False
                number = ""
                for char in word:
                    if not index and char in ["x", "х"]:
                        break
                    index = True
                    if char.isdigit() or char == "-":
                        number += char
                    elif char in ["x", "х", "(", ")"]:
                        continue
                    else:
                        number = ""
                        break
                if number != "":
                    leverage = number
                    break
        return leverage
    except Exception as e:
        print(e)
        print("LEVERAGE")
        print("___5_________E_R_R_O_R________5___")


async def margin_checker(message_lowercase, margin_keys):
    try:
        # Данная функция находит маржу по ключевым словам и отправляет обратно
        splited_message = message_lowercase.split()

        for word in splited_message:
            for key in margin_keys:
                if key in word:
                    if (
                        "cro" in word
                        or "кро" in word
                        or "сro" in word
                        or "crо" in word
                        or "сrо" in word
                    ):
                        return "Cross"
                    elif "iso" in word or "изо" in word:
                        return "Isolated"
                    else:
                        return word

        return "Def"  # Отправит деф только если до этого ничего не нашёлё
    except Exception as e:
        print(e)
        print("MARGIN")
        print("___6_________E_R_R_O_R________6___")
