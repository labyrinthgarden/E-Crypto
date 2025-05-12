from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_methods=["POST", "OPTIONS"],
    allow_headers=["Content-Type"],
    allow_credentials=True,
    expose_headers=["*"]
)

tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-medium")
model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-medium")

@app.post("/api/chat")
async def chat(request: Request):
    data = await request.json()
    message = data.get("message", "")
    inputs = tokenizer(message, return_tensors="pt")
    outputs = model.generate(
        **inputs,
        max_new_tokens=50,
        num_return_sequences=1,
        pad_token_id=tokenizer.eos_token_id,
        do_sample=True,
        temperature=0.7,
        no_repeat_ngram_size=2,
        early_stopping=True
    )
    return {"response": tokenizer.decode(outputs[0][inputs.input_ids.shape[-1]:], skip_special_tokens=True)}
