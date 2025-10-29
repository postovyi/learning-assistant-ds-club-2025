import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()

PROMPT_MIND_MAP_SYSTEM = """
Ти — Експерт-візуалізатор Знань. Твоє завдання — перетворити наданий 'Навчальний Матеріал' на чітку, структуровану ментальну карту (Mind Map).
Вивід: Використовуй лише ієрархічний список Markdown (з відступами).
Обмеження: Кожна гілка/пункт має містити не більше 5 ключових слів. Жодних вступних чи заключних слів.
"""

def generate_mind_map(material: str, model_name: str="gpt-4.1-nano") -> str:
    messages = [
        {"role": "system", "content": PROMPT_MIND_MAP_SYSTEM},
        {"role": "user", "content": f"НАВЧАЛЬНИЙ МАТЕРІАЛ: \n\n{material}"}
    ]
    
    try:
        response = client.chat.completions.create(
            model = model_name,
            messages = messages,
            temperature = 0.3,
            max_tokens = 1000,
        )
        return response.choices[0].message.content
    
    except Exception as e:
        return f"Помилка при виклику API: {str(e)}"

sample_prompt_mind_map = """
ООП — це парадигма програмування, заснована на концепції 'об'єктів', які можуть містити
дані у вигляді полів (атрибутів) та код у вигляді процедур (методів).
Основні принципи ООП: інкапсуляція (приховування даних), наслідування (створення нових класів на основі існуючих)
та поліморфізм (здатність об'єктів приймати різні форми). Це робить код більш гнучким та легким для підтримки.
"""

mind_map_structure = generate_mind_map(sample_prompt_mind_map)

print("Згенерована ментальна карта (Mind Map):")
print(mind_map_structure)