"""
Activity Agent

Specialized agent for handling activity and tour planning
"""

from typing import Dict, Any, List
import random

from .base_agent import BaseAgent


class ActivityAgent(BaseAgent):
    """
    Activity Agent - Handles activity searches and tour planning
    
    Capabilities:
    - Search for activities
    - Get activity details
    - Provide activity recommendations
    """
    
    def __init__(self):
        capabilities = [
            {
                "name": "search_activities",
                "description": "Search for available activities and tours",
                "parameters": {
                    "location": "str",
                    "date": "str",
                    "interests": "list",
                    "budget": "str"
                }
            },
            {
                "name": "get_activity_details",
                "description": "Get details of a specific activity",
                "parameters": {"activity_id": "str"}
            }
        ]
        
        system_prompt = """You are an Activity Agent specialized in finding tours and activities.
                            You have access to activity databases and can provide:
                            - Activity searches based on location, interests, and dates
                            - Tour recommendations based on preferences and budget
                            - Local experiences and unique activities
                            - Activity schedules and availability

                            Always provide helpful, accurate information about activities. Consider factors like:
                            - Activity type and duration
                            - Physical difficulty level
                            - Age appropriateness
                            - Group size limitations
                            - Weather dependencies
                            - Cultural significance"""
        
        super().__init__(
            name="Activity Agent",
            agent_type="activity",
            capabilities=capabilities,
            system_prompt=system_prompt
        )
        
        # Mock activity categories
        self.activity_types = {
            "culture": ["Museum Tour", "Historical Walk", "Art Gallery", "Theater Show"],
            "adventure": ["Hiking", "Zip-lining", "Rock Climbing", "Paragliding"],
            "food": ["Food Tour", "Cooking Class", "Wine Tasting", "Market Visit"],
            "relaxation": ["Spa Day", "Beach Visit", "Yoga Class", "Boat Cruise"],
            "entertainment": ["Concert", "Show", "Sports Event", "Nightlife Tour"],
            "nature": ["Wildlife Safari", "Nature Walk", "Bird Watching", "Botanical Garden"]
        }
    
    def process_request(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Process activity-related requests"""
        
        if action == "search_activities":
            return self.search_activities(**parameters)
        elif action == "get_activity_details":
            return self.get_activity_details(**parameters)
        elif action == "recommend_activities":
            return self.recommend_activities(**parameters)
        else:
            raise ValueError(f"Unknown action: {action}")
    
    def search_activities(
        self,
        location: str,
        date: str = None,
        interests: List[str] = None,
        budget: str = "medium"
    ) -> Dict[str, Any]:
        """
        Search for activities
        
        Returns mock activity data or AI-generated recommendations
        """
        interests = interests or ["culture", "food"]
        print(f"🎭 Searching activities in {location} (interests: {', '.join(interests)})")
        
        activities = []
        serpapi_data = None
        if self.serpapi_key:
            query = self._build_activity_query(location, interests)
            serpapi_data = self._serpapi_search({
                "engine": "google_maps",
                "type": "search",
                "q": query,
                "hl": "en",
                "gl": "us"
            })
            activities = self._parse_serpapi_activities(serpapi_data, location, interests, budget)
        
        if not activities:
            # Generate mock activity data
            activities = self._generate_mock_activities(location, interests, budget)
        
        # Use OpenAI for recommendations if available
        if self.use_openai:
            prompt = f"""Suggest the best activities in {location} for someone interested in {', '.join(interests)}.
                        Budget level: {budget}. Here are some available options:

                        {self._format_activities_for_ai(activities)}

                        Provide a brief recommendation and suggest a good itinerary for these activities.
                        Return Markdown only (no HTML)."""
            
            recommendation = self.call_openai(prompt, temperature=0.7)
        else:
            recommendation = f"Found {len(activities)} activities in {location} matching your interests"
        
        return {
            "activities": activities,
            "count": len(activities),
            "recommendation": recommendation,
            "search_params": {
                "location": location,
                "date": date,
                "interests": interests,
                "budget": budget
            }
        }
    
    def get_activity_details(self, activity_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific activity"""
        return {
            "activity_id": activity_id,
            "details": "Full activity details would be fetched from a real API",
            "available": True
        }
    
    def recommend_activities(
        self,
        location: str,
        days: int = 3
    ) -> Dict[str, Any]:
        """Get AI-powered activity recommendations"""
        
        if self.use_openai:
            prompt = f"""Create a {days}-day activity itinerary for {location}.
                        Include:
                        - Must-see attractions
                        - Hidden gems
                        - Local experiences
                        - Best times to visit each place
                        - Time management tips"""
            
            recommendation = self.call_openai(prompt, max_tokens=1500)
        else:
            recommendation = f"A {days}-day itinerary for {location} would include various cultural and recreational activities"
        
        return {
            "recommendation": recommendation,
            "location": location,
            "days": days
        }

    def _build_activity_query(self, location: str, interests: List[str]) -> str:
        interests = interests or ["things to do"]
        interests_text = ", ".join(interests)
        return f"{interests_text} things to do in {location}"

    def _parse_serpapi_activities(
        self,
        data: Dict[str, Any],
        location: str,
        interests: List[str],
        budget: str
    ) -> list:
        if not data or not isinstance(data, dict):
            return []
        
        results = data.get("local_results") or []
        activities = []
        for idx, item in enumerate(results, 1):
            price = None
            activities.append({
                "activity_id": item.get("place_id") or f"SERP-A{idx:03d}",
                "name": item.get("title") or f"Activity {idx}",
                "category": item.get("type") or (interests[0] if interests else "experience"),
                "duration": "N/A",
                "price": price,
                "currency": "USD",
                "rating": item.get("rating") or 0,
                "reviews_count": item.get("reviews") or 0,
                "location": location,
                "difficulty": "Easy",
                "group_size": "Varies",
                "included": [],
                "available_times": []
            })
        
        if not activities:
            return []
        
        activities.sort(key=lambda x: x.get("rating", 0), reverse=True)
        return activities
    
    def _generate_mock_activities(
        self,
        location: str,
        interests: List[str],
        budget: str
    ) -> list:
        """Generate mock activity data"""
        activities = []
        
        price_ranges = {
            "low": (10, 40),
            "medium": (30, 100),
            "high": (80, 250)
        }
        
        min_price, max_price = price_ranges.get(budget, (30, 100))
        
        # Generate activities based on interests
        for interest in interests:
            activity_list = self.activity_types.get(interest, self.activity_types["culture"])
            
            for _ in range(2):  # 2 activities per interest
                activity_name = random.choice(activity_list)
                duration_hours = random.randint(2, 8)
                rating = round(random.uniform(4.0, 5.0), 1)
                price = random.randint(min_price, max_price)
                
                activities.append({
                    "activity_id": f"ACT{random.randint(1000, 9999)}",
                    "name": f"{activity_name} in {location}",
                    "category": interest,
                    "duration": f"{duration_hours} hours",
                    "price": price,
                    "currency": "USD",
                    "rating": rating,
                    "reviews_count": random.randint(50, 1000),
                    "location": location,
                    "difficulty": random.choice(["Easy", "Moderate", "Challenging"]),
                    "group_size": f"Up to {random.randint(4, 20)} people",
                    "included": random.sample([
                        "Guide", "Entrance Fees", "Transportation",
                        "Lunch", "Equipment", "Photos"
                    ], random.randint(2, 4)),
                    "available_times": [
                        "09:00 AM", "11:00 AM", "2:00 PM", "4:00 PM"
                    ]
                })
        
        # Sort by rating
        activities.sort(key=lambda x: x['rating'], reverse=True)
        
        return activities
    
    def _format_activities_for_ai(self, activities: list) -> str:
        """Format activity data for AI prompt"""
        formatted = []
        for i, activity in enumerate(activities, 1):
            formatted.append(
                f"{i}. {activity['name']} ({activity['category']}) - "
                f"${activity['price']} - {activity['duration']} - "
                f"Rating: {activity['rating']} ({activity['reviews_count']} reviews) - "
                f"Difficulty: {activity['difficulty']}"
            )
        return "\n".join(formatted)
