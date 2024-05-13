from fastapi import FastAPI, Request

from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

import uvicorn
import os

from models import Response_bot, Response_chat_database
from connect_database import supabase

from dotenv import load_dotenv
load_dotenv()

import google.generativeai as genai

genai.configure(api_key=os.environ.get("API_KEY"))


generation_config = {
    "temperature": 0.75,
    "top_p": 0.95,
    "top_k": 0,
    "max_output_tokens": 4096,
}

safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_NONE"
    },
]


response = supabase.table('inseminações_database').select('*').execute()
response_dict = dict(response)

chat_instructions = ["A seguir, você vai receber, em formato de json, um banco de dados acerca sobre inseminações artificiais, você responderá qualquer tipo de pergunta baseando-se somente nesses dados. Você será um chatbot que assumirá 3 perfis, e usará o perfil certo de acordo com o contexto: Assistente de vendas, Veterinário e Poeta. O Assistente de vendas deverá ajudar a impulsionar o desempenho na parte financeira. já o Veterinário, deverá analisar e dar conselhos acerca das inseminações contidas na base de dados.", response_dict['data']]


model = genai.GenerativeModel(
    model_name="gemini-pro",
    generation_config=generation_config,
    safety_settings=safety_settings
)


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


def get_supabase_data(table: str):
    response = supabase.table(f"{table}").select("*").execute()
    response_dict = dict(response)
    data = response_dict['data']
    return data


@app.get("/", response_class=HTMLResponse)
async def get_index_page(request: Request):
    return templates.TemplateResponse(
        request=request, name="index.html"
    )
    
    
@app.get("/get-database")
async def get_databased():
    response = supabase.table('inseminações_database').select('*').execute()
    response_dict = dict(response)
    return response_dict['data']


@app.get("/get-chat-history")
async def get_chat_history():
    chat_database = get_supabase_data("chats_history") 
    return chat_database


@app.post("/send-chats")
async def send_chats(response: Response_chat_database):
    response_dict = response.model_dump()
    supabase.table("chats_history").insert({"chat_name": response_dict['chat_name'], "chat_history": response_dict['chat_history']}).execute()
    return None


@app.post("/send-response")
async def generate_response(response: Response_bot):
    response_dict = response.model_dump()
    chat_list = []
    chat_list.append({"role": "user", "parts": [str(chat_instructions)]})
    chat_list.append({"role": "model", "parts": ["None"]})
    for prompt in response_dict["history"]:
       chat_list.append(prompt)
    response_bot = model.generate_content(chat_list)
    print(chat_list)
    chat_list.clear()
    return response_bot.text


HOST = '0.0.0.0'
PORT = int(os.getenv("PORT", 8000))

if __name__ == "__main__":
    uvicorn.run("main:app", host=HOST, port=PORT, reload=True)
