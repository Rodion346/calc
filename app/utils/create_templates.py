def format_message(text_dict):
    # Определяем иконки для трендов
    trend = text_dict.get("Trand", "").upper()
    trend_icon1 = "🟢" if trend == "LONG" else "🔴"
    trend_icon2 = "⏬" if trend == "SHORT" else "⏫"

    # Определяем значения для форматирования
    channel_id = text_dict.get("channel_id", "")
    channel_name = text_dict.get("channel_name", "")
    coin = text_dict.get("Coin", "")
    leverage = text_dict.get("Leverage", "")
    margin = text_dict.get("Margin_type", "")
    entry_lvh = text_dict.get("Entrance_point_lvh", "")
    entry_tvh = text_dict.get("Entrance_point_tvh", "")
    entry_rvh = text_dict.get("Entrance_point_rvh", "")
    tp = text_dict.get("Take_profit", "")
    stop = text_dict.get("Stop_loss", "")

    # Форматируем строку
    formatted_text = (
        f"{trend_icon1} ID: <b>{channel_id}</b>\n"
        f"<i>{channel_name}</i>\n\n"
        f"{trend_icon2} Trend: {trend}      |     💵 COIN: {coin}\n"
        f"🔘 Leverage: {leverage}     |     🔘 Margin: {margin}\n\n"
    )

    # Добавляем строки для entry, если они не пустые
    formatted_text += f"💰 Entry:\n"
    if entry_tvh:
        formatted_text += f"                tvh: {entry_tvh}\n"
    if entry_lvh:
        formatted_text += f"                lvh: {entry_lvh}\n"
    if entry_rvh:
        formatted_text += f"                rvh: {entry_rvh}\n"

    # Добавляем строки для target и stop, если они не пустые
    if tp:
        formatted_text += f"✅ Target:      {tp}\n"
    if stop:
        formatted_text += f"❌ Stop:        {stop}"

    return formatted_text
