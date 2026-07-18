import os
from dotenv import load_dotenv
from groq import Groq


# Load environment variables
load_dotenv()


# Groq client
client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)



# -----------------------------
# AI Hint Generator
# -----------------------------

def get_ai_hint(question):

    prompt = f"""
You are an AI Escape Room Guide.

The player is solving this puzzle:

{question}

Rules:
- Give only ONE helpful hint.
- Never reveal the answer.
- Keep the hint under 25 words.
"""


    try:

        response = client.chat.completions.create(

            model="llama-3.3-70b-versatile",

            messages=[
                {
                    "role": "system",
                    "content": "You are an AI puzzle assistant."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],

            temperature=0.8
        )


        return response.choices[0].message.content


    except Exception as e:

        return f"Error: {str(e)}"




# -----------------------------
# AI Puzzle Generator
# -----------------------------

def generate_puzzle(previous_questions=[]):


    prompt = f"""
Generate ONE new escape room puzzle for school students.

Difficulty level:
- medium
- Fun
- Suitable for students aged 10-18
- Answerable within 30 seconds

Rules:
- Never repeat previous questions.
- Do not ask advanced science questions.
- Avoid difficult textbook terms.
- Use simple concepts students already know.

Topics:
- AI
- Computers
- Internet
- Mathematics
- General Knowledge
- Logic puzzles

Question rules:
- Question should be short and clear.
- Answer should be one word or a simple phrase.
- The answer should be commonly known by school and college students.

Examples of difficulty:

Good:
Question: Which device is used to type on a computer?
Answer: Keyboard

Good:
Question: How many sides does a triangle have?
Answer: Three


Previous questions to avoid:

{previous_questions}


Return ONLY valid JSON:

{{
    "question":"",
    "answer":"",
    "hint":""
}}
"""


    try:

        response = client.chat.completions.create(

            model="llama-3.3-70b-versatile",

            messages=[
                {
                    "role": "system",
                    "content": "You generate unique educational escape room puzzles."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],

            temperature=1.2,
            max_tokens=300
        )


        return response.choices[0].message.content

        print("========== AI RESPONSE ==========")
        print(result)
        print("=================================")

        return result


    except Exception as e:

        return f'''
{{
    "question":"AI failed to generate puzzle",
    "answer":"error",
    "hint":"Try again"
}}
'''