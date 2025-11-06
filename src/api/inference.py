"""
Inference service for sentiment prediction
Implements singleton pattern for model caching
"""
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from typing import List, Dict, Tuple, Optional
import json
import logging
from pathlib import Path
import time
from functools import lru_cache
import numpy as np

logger = logging.getLogger(__name__)


class SentimentPredictor:
    """
    Singleton class for sentiment prediction
    Loads model once and caches it for subsequent requests
    """
    _instance = None
    _model = None
    _tokenizer = None
    _device = None
    _model_version = None
    _label_map = {0: "negative", 1: "neutral", 2: "positive"}
    _loaded = False
    
    def __new__(cls):
        """Singleton pattern implementation"""
        if cls._instance is None:
            cls._instance = super(SentimentPredictor, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize predictor (only once due to singleton)"""
        if not self._loaded:
            self._load_model()
    
    def _load_model(self):
        """Load model and tokenizer from disk"""
        try:
            logger.info("Loading model and tokenizer...")
            start_time = time.time()
            
            # Determine device
            self._device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            logger.info(f"Using device: {self._device}")
            
            # Model path - try multiple locations
            possible_paths = [
                Path(__file__).parent.parent.parent / "models" / "bert_finetuned",
                Path("models/bert_finetuned"),
                Path("../models/bert_finetuned"),
                Path(__file__).parent.parent.parent.parent / "models" / "bert_finetuned",
            ]
            
            model_path = None
            for path in possible_paths:
                if path.exists():
                    model_path = path
                    break
            
            if not model_path:
                raise FileNotFoundError(
                    f"Model not found. Tried locations:\n" +
                    "\n".join([f"  - {p}" for p in possible_paths]) +
                    "\n\nPlease ensure the model is trained and accessible."
                )
            
            # Load tokenizer
            self._tokenizer = AutoTokenizer.from_pretrained(str(model_path))
            logger.info("Tokenizer loaded successfully")
            
            # Load model
            self._model = AutoModelForSequenceClassification.from_pretrained(
                str(model_path)
            )
            self._model.to(self._device)
            self._model.eval()
            logger.info("Model loaded successfully")
            
            # Load model info if available
            model_info_path = model_path / "model_info.json"
            if model_info_path.exists():
                with open(model_info_path, 'r') as f:
                    model_info = json.load(f)
                    self._model_version = model_info.get("version", "unknown")
            else:
                self._model_version = "v1.0"
            
            load_time = time.time() - start_time
            logger.info(f"Model loaded in {load_time:.2f} seconds")
            logger.info(f"Model version: {self._model_version}")
            
            self._loaded = True
            
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            raise
    
    def _preprocess(self, text: str) -> Dict[str, torch.Tensor]:
        """
        Preprocess text for model input
        
        Args:
            text: Input text
            
        Returns:
            Tokenized inputs as tensors
        """
        # Clean text
        text = text.strip()
        
        # Tokenize
        inputs = self._tokenizer(
            text,
            padding=True,
            truncation=True,
            max_length=512,
            return_tensors="pt"
        )
        
        # Move to device
        inputs = {key: val.to(self._device) for key, val in inputs.items()}
        
        return inputs
    
    def _postprocess(
        self,
        logits: torch.Tensor,
        return_probabilities: bool = False
    ) -> Tuple[str, float, Optional[Dict[str, float]]]:
        """
        Postprocess model outputs
        
        Args:
            logits: Model output logits
            return_probabilities: Whether to return all class probabilities
            
        Returns:
            Tuple of (predicted_label, confidence_score, probabilities_dict)
        """
        # Apply softmax to get probabilities
        probabilities = torch.nn.functional.softmax(logits, dim=-1)
        
        # Get predicted class
        predicted_class = torch.argmax(probabilities, dim=-1).item()
        confidence_score = probabilities[0, predicted_class].item()
        
        # Get label
        predicted_label = self._label_map.get(predicted_class, "unknown")
        
        # Get all probabilities if requested
        probs_dict = None
        if return_probabilities:
            probs_dict = {
                self._label_map[i]: float(probabilities[0, i].item())
                for i in range(len(self._label_map))
            }
        
        return predicted_label, confidence_score, probs_dict
    
    @torch.no_grad()
    def predict(
        self,
        text: str,
        return_probabilities: bool = False
    ) -> Dict[str, any]:
        """
        Predict sentiment for a single text
        
        Args:
            text: Input text
            return_probabilities: Whether to return all class probabilities
            
        Returns:
            Dictionary with prediction results
        """
        if not self._loaded:
            raise RuntimeError("Model not loaded")
        
        start_time = time.time()
        
        try:
            # Preprocess
            inputs = self._preprocess(text)
            
            # Forward pass
            outputs = self._model(**inputs)
            logits = outputs.logits
            
            # Postprocess
            label, score, probs = self._postprocess(logits, return_probabilities)
            
            processing_time = (time.time() - start_time) * 1000  # Convert to ms
            
            result = {
                "sentiment": label,
                "score": score,
                "probabilities": probs,
                "processing_time_ms": processing_time,
                "model_version": self._model_version
            }
            
            logger.debug(f"Prediction: {label} (score: {score:.3f}, time: {processing_time:.2f}ms)")
            
            return result
            
        except Exception as e:
            logger.error(f"Error during prediction: {str(e)}")
            raise
    
    @torch.no_grad()
    def predict_batch(
        self,
        texts: List[str],
        return_probabilities: bool = False,
        batch_size: int = 32
    ) -> List[Dict[str, any]]:
        """
        Predict sentiment for multiple texts in batches
        
        Args:
            texts: List of input texts
            return_probabilities: Whether to return all class probabilities
            batch_size: Batch size for processing
            
        Returns:
            List of prediction dictionaries
        """
        if not self._loaded:
            raise RuntimeError("Model not loaded")
        
        start_time = time.time()
        results = []
        
        try:
            # Process in batches
            for i in range(0, len(texts), batch_size):
                batch_texts = texts[i:i + batch_size]
                batch_start = time.time()
                
                # Tokenize batch
                inputs = self._tokenizer(
                    batch_texts,
                    padding=True,
                    truncation=True,
                    max_length=512,
                    return_tensors="pt"
                )
                
                # Move to device
                inputs = {key: val.to(self._device) for key, val in inputs.items()}
                
                # Forward pass
                outputs = self._model(**inputs)
                logits = outputs.logits
                
                # Process each prediction in batch
                for j in range(len(batch_texts)):
                    label, score, probs = self._postprocess(
                        logits[j:j+1],
                        return_probabilities
                    )
                    
                    batch_time = (time.time() - batch_start) * 1000 / len(batch_texts)
                    
                    results.append({
                        "sentiment": label,
                        "score": score,
                        "probabilities": probs,
                        "processing_time_ms": batch_time,
                        "model_version": self._model_version
                    })
            
            total_time = (time.time() - start_time) * 1000
            logger.info(
                f"Batch prediction completed: {len(texts)} texts in {total_time:.2f}ms "
                f"({total_time/len(texts):.2f}ms per text)"
            )
            
            return results
            
        except Exception as e:
            logger.error(f"Error during batch prediction: {str(e)}")
            raise
    
    def get_attention_weights(self, text: str) -> Dict[str, any]:
        """
        Get attention weights for explainability
        
        Args:
            text: Input text
            
        Returns:
            Dictionary with attention weights and tokens
        """
        if not self._loaded:
            raise RuntimeError("Model not loaded")
        
        try:
            # Preprocess
            inputs = self._preprocess(text)
            
            # Forward pass with attention output
            outputs = self._model(**inputs, output_attentions=True)
            
            # Get attention weights from last layer
            attention = outputs.attentions[-1]  # Last layer
            attention = attention[0].mean(dim=0)  # Average over attention heads
            
            # Get tokens
            tokens = self._tokenizer.convert_ids_to_tokens(inputs["input_ids"][0])
            
            # Get prediction
            logits = outputs.logits
            label, score, _ = self._postprocess(logits)
            
            # Create attention map
            attention_map = {}
            for i, token in enumerate(tokens):
                if token not in ["[CLS]", "[SEP]", "[PAD]"]:
                    # Get attention weight for this token
                    att_weight = float(attention[i].sum().item())
                    attention_map[token] = att_weight
            
            # Normalize attention weights
            total_attention = sum(attention_map.values())
            if total_attention > 0:
                attention_map = {
                    k: v/total_attention 
                    for k, v in attention_map.items()
                }
            
            # Sort by importance
            attention_map = dict(
                sorted(attention_map.items(), key=lambda x: x[1], reverse=True)
            )
            
            return {
                "sentiment": label,
                "score": score,
                "tokens": tokens,
                "attention_weights": attention_map,
                "top_tokens": dict(list(attention_map.items())[:10])
            }
            
        except Exception as e:
            logger.error(f"Error getting attention weights: {str(e)}")
            raise
    
    def get_model_info(self) -> Dict[str, any]:
        """
        Get model information
        
        Returns:
            Dictionary with model metadata
        """
        if not self._loaded:
            raise RuntimeError("Model not loaded")
        
        # Count parameters
        num_params = sum(p.numel() for p in self._model.parameters())
        
        return {
            "model_name": "BERT Sentiment Classifier",
            "model_version": self._model_version,
            "model_type": self._model.config.model_type,
            "num_parameters": num_params,
            "classes": list(self._label_map.values()),
            "device": str(self._device),
            "max_length": 512,
            "vocab_size": self._tokenizer.vocab_size
        }
    
    @property
    def is_loaded(self) -> bool:
        """Check if model is loaded"""
        return self._loaded
    
    @property
    def model_version(self) -> str:
        """Get model version"""
        return self._model_version
    
    @property
    def device(self) -> str:
        """Get device"""
        return str(self._device) if self._device else "unknown"


# Global singleton instance
_predictor_instance = None


def get_predictor() -> SentimentPredictor:
    """
    Get or create the global predictor instance
    
    Returns:
        SentimentPredictor instance
    """
    global _predictor_instance
    if _predictor_instance is None:
        _predictor_instance = SentimentPredictor()
    return _predictor_instance
