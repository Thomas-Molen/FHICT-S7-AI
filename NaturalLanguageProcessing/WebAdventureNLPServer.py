import os
import getpass

from langchain.memory import ConversationBufferWindowMemory

# Get OpenAI API key
os.environ["OPENAI_API_KEY"] = getpass.getpass("OpenAI API Key:")

# Create the LLM model
dungeon_template = """
A player inside a dungeon performed an action

The dungeon responded with: {event}

This could be said in a more intriguing manner by saying instead:"""

from langchain import PromptTemplate
dungeon_prompt = PromptTemplate(template=dungeon_template, input_variables=["event"])

from langchain.chat_models import ChatOpenAI
from langchain import LLMChain
chatgpt_dungeon_chain = LLMChain(
    llm=ChatOpenAI(model_name = "gpt-3.5-turbo", temperature=0.5),
    prompt=dungeon_prompt
)


from fastapi import FastAPI, Response
from fastapi.responses import PlainTextResponse

app = FastAPI()
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/{input}")
def process_input(input: str):
    return Response(content=chatgpt_dungeon_chain.predict(event=input), media_type="text/plain")