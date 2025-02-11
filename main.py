from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import os
from dotenv import load_dotenv
from google.generativeai import text

app = FastAPI()

# Obter API Key do Gemini do ambiente
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")  # Nome da variável de ambiente alterado
if not api_key:
    raise ValueError("A chave da API Gemini não está definida. Configure a variável de ambiente GEMINI_API_KEY.")

# Configurar a API do Gemini
text.configure(api_key=api_key)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todas as origens (não recomendado para produção)
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos os métodos (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],  # Permite todos os cabeçalhos
)


# ... (resto do código igual, exceto a função generate_question)
import sqlite3

def create_db():
    try:
        conn = sqlite3.connect("quiz.db")
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT,
                option_a TEXT,
                option_b TEXT,
                option_c TEXT,
                option_d TEXT,
                answer TEXT
            )
        ''')
        conn.commit()
        print("Tabela 'questions' criada ou já existente.")  # Mensagem informativa
    except sqlite3.Error as e:
        print(f"Erro ao criar a tabela: {e}")
    finally:  # Garante que a conexão seja fechada mesmo em caso de erro
        if conn:
            conn.close()

create_db()  # Chama a função para criar o banco de dados
def save_to_db(question, options, answer):
    conn = sqlite3.connect("quiz.db")
    cursor = conn.cursor()

    cursor.execute("INSERT INTO questions (question, answer) VALUES (?, ?)", (question, answer))
    question_id = cursor.lastrowid  # Obtém o ID da pergunta inserida

    for option in options:
        cursor.execute("INSERT INTO options (question_id, option_text) VALUES (?, ?)", (question_id, option))

    conn.commit()
    conn.close()


# Modelo de dados para as respostas do usuário

class UserAnswers(BaseModel):
    answers: List[str]
@app.post("/generate_question")
def generate_question():
    prompt = "Crie uma pergunta de múltipla escolha sobre ciência com quatro opções e indique a resposta correta."

    response = text.generate_text(
        model="gemini-pro",  # Ou outro modelo Gemini disponível
        prompt=prompt,
        temperature=0.7,  # Ajuste a temperatura conforme necessário
        max_output_tokens=200  # Ajuste o número de tokens conforme necessário
    )

    generated_text = response.result.strip()

    # Supondo que o texto gerado tenha o formato correto (ajustar conforme necessário)
    try:
        lines = generated_text.split("\n")
        question = lines[0]
        options = lines[1:5]
        answer = lines[5]
    except Exception as e:  # Captura exceções gerais para tratamento
        print(f"Erro na geração de texto: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao gerar pergunta: {e}")  # Retorna erro 500

    save_to_db(question, options, answer)
    return {"question": question, "options": options, "answer": answer}

# ... (resto do código igual)

if __name__ == "__main__":
    create_db()
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) # Adicionado para facilitar a execução local