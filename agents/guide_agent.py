"""
Guide Agent

Specialized agent for providing local information and travel tips
"""

from typing import Dict, Any, List

from .base_agent import BaseAgent


class GuideAgent(BaseAgent):
    """
    Guide Agent - Provides local information, tips, and guidance
    
    Capabilities:
    - Provide local information
    - Share travel tips
    - Answer questions about destinations
    """
    
    def __init__(self):
        capabilities = [
            {
                "name": "get_local_info",
                "description": "Get local information about a destination",
                "parameters": {
                    "location": "str",
                    "topics": "list"
                }
            },
            {
                "name": "get_travel_tips",
                "description": "Get travel tips for a destination",
                "parameters": {
                    "location": "str",
                    "traveler_type": "str"
                }
            }
        ]
        
        system_prompt = """You are a Local Guide Agent - an expert travel guide with deep knowledge of destinations worldwide.
                            You provide:
                            - Local insights and insider tips
                            - Cultural information and customs
                            - Safety and health advice
                            - Transportation guidance
                            - Language tips and useful phrases
                            - Best times to visit attractions
                            - Local food and dining recommendations
                            - Money and payment information
                            - Emergency contacts and resources

                            You speak like a knowledgeable local friend who wants visitors to have the best experience.
                            Be specific, practical, and culturally sensitive in your recommendations."""
        
        super().__init__(
            name="Guide Agent",
            agent_type="guide",
            capabilities=capabilities,
            system_prompt=system_prompt
        )
    
    def process_request(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Process guide-related requests"""
        
        if action == "get_local_info":
            return self.get_local_info(**parameters)
        elif action == "get_travel_tips":
            return self.get_travel_tips(**parameters)
        elif action == "answer_question":
            return self.answer_question(**parameters)
        else:
            raise ValueError(f"Unknown action: {action}")
    
    def get_local_info(
        self,
        location: str,
        topics: List[str] = None
    ) -> Dict[str, Any]:
        """
        Get local information about a destination
        
        Returns AI-generated local insights
        """
        topics = topics or ["culture", "food", "transportation", "safety"]
        print(f"📍 Getting local info for {location} (topics: {', '.join(topics)})")
        
        if self.use_openai:
            prompt = f"""As a local guide, provide comprehensive information about {location} covering these topics:
                        {', '.join(topics)}

                        Include:
                        - Practical tips that tourists often miss
                        - Cultural customs and etiquette
                        - Local favorites vs tourist traps
                        - Money-saving tips
                        - Safety considerations
                        - Best ways to get around

                        Be specific and actionable.
                        Return Markdown only (no HTML)."""
            
            info = self.call_openai(prompt, temperature=0.6, max_tokens=1500)
        else:
            info = f"Local guide information for {location} covering {', '.join(topics)}"
        
        return {
            "location": location,
            "topics": topics,
            "information": info,
            "language": "en"
        }
    
    def get_travel_tips(
        self,
        location: str,
        traveler_type: str = "general"
    ) -> Dict[str, Any]:
        """
        Get travel tips for specific traveler types
        
        Args:
            location: Destination
            traveler_type: Type of traveler (solo, family, business, budget, luxury)
        """
        print(f"💡 Getting travel tips for {location} ({traveler_type} traveler)")
        
        if self.use_openai:
            prompt = f"""Provide expert travel tips for a {traveler_type} traveler visiting {location}.

                        Include:
                        - Accommodation recommendations
                        - Transportation advice
                        - Budgeting tips
                        - Safety considerations specific to {traveler_type} travelers
                        - Best neighborhoods or areas
                        - Things to avoid
                        - Insider secrets
                        - Packing suggestions

                        Make it practical and specific to {traveler_type} travel style.
                        Return Markdown only (no HTML)."""
            
            tips = self.call_openai(prompt, temperature=0.6, max_tokens=1500)
        else:
            tips = f"Travel tips for {traveler_type} travelers in {location}"
        
        return {
            "location": location,
            "traveler_type": traveler_type,
            "tips": tips
        }
    
    def answer_question(
        self,
        location: str,
        question: str
    ) -> Dict[str, Any]:
        """
        Answer specific questions about a destination
        """
        print(f"❓ Answering question about {location}")
        
        if self.use_openai:
            prompt = f"""As a local expert guide for {location}, answer this question:

                        {question}

                        Provide a detailed, helpful answer based on local knowledge. Be specific and practical.
                        Return Markdown only (no HTML)."""
            
            answer = self.call_openai(prompt, temperature=0.5)
        else:
            answer = f"To answer '{question}' about {location}, I would need more specific information."
        
        return {
            "location": location,
            "question": question,
            "answer": answer
        }
    
    def get_essential_phrases(
        self,
        location: str,
        language: str
    ) -> Dict[str, Any]:
        """Get essential phrases for the destination"""
        
        if self.use_openai:
            prompt = f"""Provide 15 essential phrases in {language} for travelers visiting {location}.
                        Include:
                        - Greetings
                        - Basic courtesy (please, thank you)
                        - Asking for help
                        - Ordering food
                        - Directions
                        - Emergencies

                        Format: English phrase | Local language | Pronunciation
                        Return Markdown only (no HTML)."""
            
            phrases = self.call_openai(prompt, temperature=0.3)
        else:
            phrases = f"Essential {language} phrases for {location}"
        
        return {
            "location": location,
            "language": language,
            "phrases": phrases
        }
