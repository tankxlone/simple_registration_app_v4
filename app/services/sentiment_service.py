from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from typing import Tuple, Dict, Any
import re
from config import Config

class SentimentService:
    """Service for analyzing sentiment of feedback text"""
    
    def __init__(self):
        self.analyzer = SentimentIntensityAnalyzer()
        self.banned_words = set(Config.BANNED_WORDS)
    
    def analyze_sentiment(self, text: str) -> Tuple[str, float, Dict[str, Any]]:
        """
        Analyze sentiment of text using VADER
        
        Args:
            text: Input text to analyze
            
        Returns:
            Tuple of (label, confidence_score, full_analysis)
        """
        # Check for banned words
        if self._contains_banned_words(text):
            return 'negative', 1.0, {'banned_words_detected': True}
        
        # Get VADER sentiment scores
        scores = self.analyzer.polarity_scores(text)
        
        # Determine label and confidence
        compound_score = scores['compound']
        
        if compound_score >= 0.05:
            label = 'positive'
            confidence = compound_score
        elif compound_score <= -0.05:
            label = 'negative'
            confidence = abs(compound_score)
        else:
            label = 'neutral'
            confidence = 1.0 - abs(compound_score)
        
        # Normalize confidence to 0-1 range
        confidence = max(0.0, min(1.0, confidence))
        
        analysis = {
            'compound': compound_score,
            'positive': scores['pos'],
            'negative': scores['neg'],
            'neutral': scores['neu'],
            'label': label,
            'confidence': confidence,
            'banned_words_detected': False
        }
        
        return label, confidence, analysis
    
    def _contains_banned_words(self, text: str) -> bool:
        """Check if text contains any banned words"""
        text_lower = text.lower()
        return any(word.lower() in text_lower for word in self.banned_words)
    
    def get_sentiment_label(self, compound_score: float) -> str:
        """Convert VADER compound score to label"""
        if compound_score >= 0.05:
            return 'positive'
        elif compound_score <= -0.05:
            return 'negative'
        else:
            return 'neutral'
    
    def update_banned_words(self, new_banned_words: list):
        """Update the list of banned words"""
        self.banned_words = set(new_banned_words)

# Alternative sentiment service using Hugging Face Transformers
class HuggingFaceSentimentService:
    """Alternative sentiment service using Hugging Face Transformers"""
    
    def __init__(self, model_name: str = "cardiffnlp/twitter-roberta-base-sentiment-latest"):
        try:
            from transformers import pipeline
            self.classifier = pipeline("sentiment-analysis", model=model_name)
            self.available = True
        except ImportError:
            self.available = False
            print("Warning: transformers not available. Install with: pip install transformers torch")
    
    def analyze_sentiment(self, text: str) -> Tuple[str, float, Dict[str, Any]]:
        """
        Analyze sentiment using Hugging Face model
        
        Args:
            text: Input text to analyze
            
        Returns:
            Tuple of (label, confidence_score, full_analysis)
        """
        if not self.available:
            raise RuntimeError("Hugging Face sentiment service not available")
        
        # Check for banned words first
        if self._contains_banned_words(text):
            return 'negative', 1.0, {'banned_words_detected': True}
        
        # Get prediction
        result = self.classifier(text)[0]
        label = result['label'].lower()
        confidence = result['score']
        
        # Map labels to standard format
        if label in ['positive', 'pos']:
            label = 'positive'
        elif label in ['negative', 'neg']:
            label = 'negative'
        else:
            label = 'neutral'
        
        analysis = {
            'label': label,
            'confidence': confidence,
            'banned_words_detected': False
        }
        
        return label, confidence, analysis
    
    def _contains_banned_words(self, text: str) -> bool:
        """Check if text contains any banned words"""
        text_lower = text.lower()
        return any(word.lower() in text_lower for word in Config.BANNED_WORDS)

# Factory function to get sentiment service
def get_sentiment_service(service_type: str = 'vader') -> SentimentService:
    """
    Factory function to get sentiment service
    
    Args:
        service_type: 'vader' or 'huggingface'
        
    Returns:
        SentimentService instance
    """
    if service_type == 'huggingface':
        return HuggingFaceSentimentService()
    else:
        return SentimentService()
