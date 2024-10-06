import ast
import asyncio
import os
from mistralai import Mistral
import json

api_key = "4nLSiw4wE9hV3zju2lSKl7yF0FhOLjb9"


client = Mistral(api_key=api_key)
promt = ""


def clean_json_string(json_string):
    start_index = json_string.find("{")
    end_index = json_string.rfind("}")
    print("SEND 1")
    print(json_string)
    # Проверяем, что оба индекса найдены
    if start_index == -1 or end_index == -1:
        return "False"

    # Обрезка строки до начала и после конца JSON-объекта
    cleaned_string = json_string[start_index : end_index + 1]
    print("SEND 2")
    print(cleaned_string)
    return cleaned_string


def string_to_dict(json_string):
    try:
        # Очистка строки
        cleaned_json_string = clean_json_string(json_string)
        if cleaned_json_string == "False":
            return "False"
        # Преобразование строки в словарь
        data = json.loads(cleaned_json_string)
        return data
    except json.JSONDecodeError as e:
        print(f"Ошибка преобразования JSON: {e}")
    except ValueError as e:
        print(f"Ошибка: {e}")


mes = (
    "🎈** **#SNX** **/USDT** - SHORT"
    "🟢 Открытие - 1.419"
    "✅ Цели - 1.395, 1.376, 1.355"
    "♾ - Плечо - х20(Cross)"
    " 🔴 Стоп - 1.497"
    "**➡️****Рекомендую приложение для торговли - ****BITGET** | **MEXC**"
    "(скидки на комиссии, бонусы до 5000$, акции, розыгрыши, раздачи)"
    "__Дайте реакций __****❤️****👍****🔥**"
)


def AI(mess):
    chat_response = client.agents.complete(
        agent_id="ag:55c24037:20240929:untitled-agent:472eca29",
        messages=[
            {
                "role": "user",
                "content": f"{mess}",
            },
        ],
    )

    resp = chat_response.choices[0].message.content
    data = string_to_dict(resp)
    return data
