import json
import random
import re
from typing import Dict, List, Optional, Tuple, Any

from app.utils.helpers import load_json_data, get_data_file_path

class ChatbotService:
    """Service for handling chatbot interactions."""
    
    def __init__(self):
        """Initialize the chatbot service with training data."""
        self.training_data = load_json_data(get_data_file_path("chatbot_training_data.json"))
        self.intents = self.training_data.get("intents", [])
        self.skills_data = load_json_data(get_data_file_path("skills.json"))
        self.projects_data = load_json_data(get_data_file_path("projects.json"))
    
    def get_response(self, message: str) -> Dict[str, Any]:
        """
        Generate a response based on the user's message.
        
        Args:
            message: The user's message
            
        Returns:
            Dictionary containing the response and context
        """
        intent, confidence = self._recognize_intent(message)
        
        if confidence < 0.4:
            # Use fallback response if confidence is low
            intent = "fallback"
        
        # Get a random response for the recognized intent
        intent_data = next((i for i in self.intents if i.get("tag") == intent), None)
        
        if not intent_data:
            # Use fallback if intent not found
            intent_data = next((i for i in self.intents if i.get("tag") == "fallback"), None)
        
        responses = intent_data.get("responses", ["I'm not sure how to respond to that."])
        response = random.choice(responses)
        
        # Get context if available
        context = intent_data.get("context", {})
        
        # Enhance response with data if context is available
        if context:
            context_type = context.get("type")
            if context_type == "skills":
                context["data"] = self._get_skills_context()
            elif context_type == "projects":
                context["data"] = self._get_projects_context()
        
        return {
            "response": response,
            "context": context
        }
    
    def _recognize_intent(self, message: str) -> Tuple[str, float]:
        """
        Recognize the intent of a message.
        
        Args:
            message: The user's message
            
        Returns:
            Tuple of (intent_tag, confidence)
        """
        message = message.lower()
        
        best_match = ("fallback", 0.0)
        
        for intent in self.intents:
            patterns = intent.get("patterns", [])
            
            for pattern in patterns:
                pattern = pattern.lower()
                
                # Simple pattern matching
                if pattern in message:
                    return intent.get("tag"), 1.0
                
                # Calculate similarity
                similarity = self._calculate_similarity(pattern, message)
                
                if similarity > best_match[1]:
                    best_match = (intent.get("tag"), similarity)
        
        return best_match
    
    def _calculate_similarity(self, pattern: str, message: str) -> float:
        """
        Calculate similarity between pattern and message.
        
        Args:
            pattern: The pattern to match
            message: The user's message
            
        Returns:
            Similarity score between 0 and 1
        """
        # Simple word overlap similarity
        pattern_words = set(pattern.lower().split())
        message_words = set(message.lower().split())
        
        if not pattern_words or not message_words:
            return 0.0
        
        common_words = pattern_words.intersection(message_words)
        
        return len(common_words) / max(len(pattern_words), len(message_words))
    
    def _get_skills_context(self) -> Dict[str, Any]:
        """Get context data for skills intent."""
        skills = self.skills_data.get("skills", [])
        top_skills = sorted(skills, key=lambda x: x.get("proficiency", 0), reverse=True)[:5]
        
        return {
            "top_skills": [{"name": skill.get("name"), "proficiency": skill.get("proficiency")} for skill in top_skills],
            "total_skills": len(skills),
            "categories": list(set(skill.get("category") for skill in skills))
        }
    
    def _get_projects_context(self) -> Dict[str, Any]:
        """Get context data for projects intent."""
        projects = self.projects_data.get("projects", [])
        featured_projects = [p for p in projects if p.get("featured", False)]
        
        return {
            "total_projects": len(projects),
            "featured_projects": [{"title": p.get("title"), "description": p.get("description")} for p in featured_projects],
            "technologies": list(set(tech for p in projects for tech in p.get("technologies", [])))
        } 