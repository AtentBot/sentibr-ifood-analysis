"""
SentiBR API - Main Application
FastAPI para análise de sentimentos em reviews de restaurantes
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
from datetime import datetime

# Inicializar FastAPI
app = FastAPI(
    title="SentiBR API",
    description="API de Análise de Sentimentos para Reviews de Restaurantes",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Schemas
class ReviewInput(BaseModel):
    text: str
    
class ReviewBatch(BaseModel):
    reviews: List[str]

class SentimentResult(BaseModel):
    text: str
    sentiment: str
    confidence: float
    scores: dict
    
class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str

# Modelo BERT (carregado globalmente)
model = None
tokenizer = None

@app.on_event("startup")
async def startup_event():
    """Carregar modelo BERT na inicialização"""
    global model, tokenizer
    
    try:
        from transformers import AutoTokenizer, AutoModelForSequenceClassification
        import torch
        
        print("🔄 Carregando modelo BERT...")
        
        model_name = "neuralmind/bert-base-portuguese-cased"
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSequenceClassification.from_pretrained(
            model_name,
            num_labels=3
        )
        model.eval()
        
        print("✅ Modelo BERT carregado com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro ao carregar modelo: {e}")
        # Não falhar, apenas logar

@app.get("/")
def read_root():
    """Endpoint raiz"""
    return {
        "message": "SentiBR API - Análise de Sentimentos",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/api/v1/health", response_model=HealthResponse)
def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        version="1.0.0"
    )

@app.post("/api/v1/predict", response_model=SentimentResult)
async def predict_sentiment(review: ReviewInput):
    """Predição de sentimento para um único review"""
    
    if model is None or tokenizer is None:
        raise HTTPException(
            status_code=503,
            detail="Modelo não carregado. Tente novamente em alguns segundos."
        )
    
    try:
        import torch
        
        # Tokenizar
        inputs = tokenizer(
            review.text,
            return_tensors="pt",
            truncation=True,
            max_length=512,
            padding=True
        )
        
        # Predição
        with torch.no_grad():
            outputs = model(**inputs)
            logits = outputs.logits
            probs = torch.nn.functional.softmax(logits, dim=-1)
            predicted_class = torch.argmax(probs, dim=-1).item()
            confidence = probs[0][predicted_class].item()
        
        # Mapear classe para sentimento
        sentiment_map = {
            0: "negative",
            1: "neutral",
            2: "positive"
        }
        
        sentiment = sentiment_map[predicted_class]
        
        # Scores detalhados
        scores = {
            "negative": float(probs[0][0]),
            "neutral": float(probs[0][1]),
            "positive": float(probs[0][2])
        }
        
        return SentimentResult(
            text=review.text,
            sentiment=sentiment,
            confidence=confidence,
            scores=scores
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro na predição: {str(e)}"
        )

@app.post("/api/v1/predict/batch")
async def predict_batch(batch: ReviewBatch):
    """Predição em lote"""
    
    if model is None or tokenizer is None:
        raise HTTPException(
            status_code=503,
            detail="Modelo não carregado."
        )
    
    try:
        results = []
        
        for text in batch.reviews:
            review = ReviewInput(text=text)
            result = await predict_sentiment(review)
            results.append(result)
        
        return {
            "total": len(results),
            "results": results
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro na predição em lote: {str(e)}"
        )

@app.get("/api/v1/model/info")
def model_info():
    """Informações do modelo"""
    
    if model is None:
        return {
            "loaded": False,
            "message": "Modelo não carregado"
        }
    
    return {
        "loaded": True,
        "model_name": "neuralmind/bert-base-portuguese-cased",
        "num_labels": 3,
        "labels": ["negative", "neutral", "positive"]
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
