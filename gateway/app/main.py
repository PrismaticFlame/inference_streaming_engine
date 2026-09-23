import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from pydantic import BaseModel
from kafka import KafkaProducer
from transformers import AutoTokenizer

from inference_engine.schemas import InferenceRequest

KAFKA_BROKERS = os.getenv("KAFKA_BROKERS", "localhost:19092")
MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-0.5B-Instruct")
TOPIC = "requests"

class GenerateBody(BaseModel):
    prompt: str
    max_new_tokens: int = 64
    temperature: float = 1.0
    top_p: float = 1.0


def bucket_for(n_tokens: int) -> str:
    if n_tokens > 5_000:
        return "long"
    elif n_tokens > 2_500:
        return "medium"
    else:
        return "short"

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    app.state.producer = KafkaProducer(bootstrap_servers=KAFKA_BROKERS)
    yield
    app.state.producer.close()

app = FastAPI(lifespan=lifespan)

@app.post("/generate", status_code=202)
def generate(body: GenerateBody):
    tokens = app.state.tokenizer.encode(body.prompt)
    req = InferenceRequest(
        prompt_tokens=tokens,
        max_new_tokens=body.max_new_tokens,
        temperature=body.temperature,
        top_p=body.top_p,
        seq_len_bucket=bucket_for(len(tokens)),
    )
    app.state.producer.send(TOPIC, value=req.to_json()).get(timeout=10)
    return {"request_id": req.request_id}
