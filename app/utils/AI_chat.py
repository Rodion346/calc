import ast
import asyncio
import os
from mistralai import Mistral
import json

api_key = "4nLSiw4wE9hV3zju2lSKl7yF0FhOLjb9"
model = "codestral-latest"

client = Mistral(api_key=api_key)


def parse_dict_string(dict_string):
    # Находим индексы начала и конца словаря
    start_index = dict_string.find("{")
    end_index = dict_string.rfind("}")

    # Проверяем, что оба индекса найдены
    if start_index == -1 or end_index == -1:
        raise ValueError("Строка не содержит корректный словарь.")

    # Обрезка строки до начала и после конца словаря
    cleaned_string = dict_string[start_index : end_index + 1]

    # Преобразуем строку в словарь
    data = cleaned_string

    return data


async def AI(mess):
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
    data = parse_dict_string(resp)
    return data
