def format_message(text_dict):
    # Определяем иконки для трендов
    trend = text_dict.get("Trand", "").upper()
    trend_icon1 = "🟢" if trend == "LONG" else "🔴"
    trend_icon2 = "⏬" if trend == "SHORT" else "⏫"

    # Определяем значения для форматирования
    changed = "{changed}"
    channel_id = text_dict.get("channel_id", "")
    channel_name = text_dict.get("channel_name", "")
    coin = text_dict.get("Coin", "")
    leverage = text_dict.get("Leverage", "")
    margin = text_dict.get("Margin_type", "")
    entry = text_dict.get("Entrance_point_lvh", "")
    tp = ", ".join(map(str, text_dict.get("Take_profit", [])))
    stop = text_dict.get("Stop_loss", "")

    # Форматируем строку
    formatted_text = (
        f"{trend_icon1} ID: <b>{channel_id}</b>\n"
        f"<i>{channel_name}</i>\n\n"
        f"{trend_icon2} Trend: {trend}      |     💵 COIN: {coin}\n"
        f"🔘 Leverage: {leverage}     |     🔘 Margin: {margin}\n\n"
        f"💰 Entry:      {entry}\n"
        f"✅ Target:      {tp}\n"
        f"❌ Stop:        {stop}"
    )

    return formatted_text
