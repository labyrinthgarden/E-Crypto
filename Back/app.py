from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from llama_cpp import Llama
import os

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    expose_headers=["*"],
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
# wget https://huggingface.co/TheBloke/neural-chat-7b-v3-1-GGUF/resolve/main/neural-chat-7b-v3-1.Q4_K_M.gguf

llm = Llama(
    model_path="neural-chat-7b-v3-1.Q4_K_M.gguf",  # Archivo local
    n_ctx=2048,
    n_gpu_layers=40 if os.getenv("USE_GPU") == "1" else 0  # GPU opcional
)

@app.post("/api/chat")
async def chat(request: Request):
    data = await request.json()
    message = data.get("message", "").strip()

    if not message:
        raise HTTPException(status_code=400, detail="Mensaje vacío")

    response = llm.create_chat_completion(
        messages=[{"role": "user", "content": "Responde ÚNICAMENTE en español, de forma clara y concisa. "+message}],
        temperature=0.7,
        top_p=0.9,
        repeat_penalty=1.2,
        max_tokens=200
    )

    return {"response": response["choices"][0]["message"]["content"]}

# USE_GPU=1 uvicorn app:app --reload --port 5000
