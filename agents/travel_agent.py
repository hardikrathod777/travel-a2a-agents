"""
Travel Agent

Main coordinator agent that orchestrates all other agents
"""

from typing import Dict, Any, List, Optional
import json
from datetime import datetime, timedelta, date

from strands.agent.a2a_agent import A2AAgent

from .base_agent import BaseAgent


class TravelAgent(BaseAgent):
    """
    Travel Agent - Main coordinator that orchestrates all specialized agents
    
    This is the primary interface for users. It:
    - Understands user requests
    - Delegates tasks to specialized agents
    - Aggregates responses
    - Provides comprehensive travel plans
    """
    
    def __init__(self):
        capabilities = [
            {
                "name": "plan_trip",
                "description": "Create a complete travel plan",
                "parameters": {
                    "destination": "str",
                    "duration": "int",
                    "budget": "str",
                    "interests": "list"
                }
            },
            {
                "name": "answer_query",
                "description": "Answer general travel questions",
                "parameters": {
                    "query": "str"
                }
            }
        ]
        
        system_prompt = """You are a Travel Agent Coordinator - the main point of contact for travelers.
                            Your role is to:
                            - Understand traveler needs and preferences
                            - Coordinate with specialized agents (Flight, Hotel, Activity, Guide)
                            - Create comprehensive, personalized travel plans
                            - Provide expert travel advice
                            - Handle complex, multi-faceted travel requests

                            You work with a team of specialized agents:
                            - Flight Agent: Handles flights and air travel
                            - Hotel Agent: Manages accommodation
                            - Activity Agent: Plans activities and tours
                            - Guide Agent: Provides local information and tips

                            When you receive requests, analyze what's needed and delegate to the appropriate agents.
                            Then synthesize their responses into a cohesive, helpful travel plan.

                            Be friendly, professional, and focused on creating amazing travel experiences."""
        
        super().__init__(
            name="Travel Agent",
            agent_type="travel_coordinator",
            capabilities=capabilities,
            system_prompt=system_prompt
        )
        
        # Store A2A endpoints for specialized agents (set during initialization)
        self.flight_agent_url: Optional[str] = None
        self.hotel_agent_url: Optional[str] = None
        self.activity_agent_url: Optional[str] = None
        self.guide_agent_url: Optional[str] = None
    
    def connect_to_agents(
        self,
        flight_agent_url: str,
        hotel_agent_url: str,
        activity_agent_url: str,
        guide_agent_url: str
    ):
        """Connect to other agents in the system via A2A endpoints."""
        self.flight_agent_url = flight_agent_url
        self.hotel_agent_url = hotel_agent_url
        self.activity_agent_url = activity_agent_url
        self.guide_agent_url = guide_agent_url
        print(f"✅ {self.name} connected to all specialized agents (A2A)")
    
    def _parse_departure_date(self, departure_date: str) -> date:
        """Parse the departure date or default to tomorrow."""
        if not departure_date:
            return date.today() + timedelta(days=1)
        try:
            return datetime.strptime(departure_date, "%Y-%m-%d").date()
        except ValueError as exc:
            raise ValueError("Invalid departure_date. Use YYYY-MM-DD.") from exc

    def _extract_a2a_text(self, result) -> str:
        if result is None:
            return ""
        if hasattr(result, "output_text") and isinstance(result.output_text, str):
            return result.output_text
        if hasattr(result, "text") and isinstance(result.text, str):
            return result.text
        if hasattr(result, "content") and isinstance(result.content, list):
            texts = []
            for block in result.content:
                if isinstance(block, dict) and "text" in block:
                    texts.append(block["text"])
            if texts:
                return "\n".join(texts)
        return str(result)

    def _a2a_send(self, base_url: str, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        payload = json.dumps({"action": action, "parameters": parameters})
        agent = A2AAgent(endpoint=base_url)
        result = agent(payload)
        text = self._extract_a2a_text(result)
        try:
            return json.loads(text) if text else {}
        except Exception:
            return {"raw": text}

    def process_request(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Process travel coordination requests"""
        
        if action == "plan_trip":
            return self.plan_trip(**parameters)
        elif action == "answer_query":
            return self.answer_query(**parameters)
        elif action == "get_recommendations":
            return self.get_recommendations(**parameters)
        else:
            raise ValueError(f"Unknown action: {action}")
    
    def plan_trip(
        self,
        destination: str,
        duration: int,
        budget: str = "medium",
        interests: List[str] = None,
        origin: str = None,
        departure_date: str = None,
        progress_callback=None
    ) -> Dict[str, Any]:
        """
        Create a complete travel plan by coordinating all agents
        
        Args:
            destination: Where to go
            duration: How many days
            budget: low, medium, or high
            interests: List of interests
            origin: Departure city (optional)
            departure_date: When to leave (optional)
            
        Returns:
            Complete travel plan with flights, hotels, activities, and tips
        """
        interests = interests or ["culture", "food"]
        start_date = self._parse_departure_date(departure_date)
        start_date_str = start_date.strftime("%Y-%m-%d")
        end_date_str = (start_date + timedelta(days=duration)).strftime("%Y-%m-%d")
        print(f"\n{'='*60}")
        print(f"🌍 Planning {duration}-day trip to {destination}")
        print(f"   Start Date: {start_date_str}")
        print(f"   Budget: {budget} | Interests: {', '.join(interests)}")
        print(f"{'='*60}\n")
        
        travel_plan = {
            "destination": destination,
            "duration": duration,
            "budget": budget,
            "interests": interests,
            "departure_date": start_date_str
        }
        
        # Step 1: Get flights (if origin provided)
        if origin and self.flight_agent_url:
            if progress_callback:
                progress_callback("status", "Searching flights...")
            print("Step 1: Searching flights...")
            try:
                flights_data = self._a2a_send(
                    self.flight_agent_url,
                    "search_flights",
                    {
                        "origin": origin,
                        "destination": destination,
                        "date": start_date_str,
                        "passengers": 1
                    }
                )
                travel_plan["flights"] = flights_data
                print(f"   ✓ Found {flights_data.get('count', 0)} flights\n")
                if progress_callback:
                    progress_callback("flights", flights_data)
            except Exception as exc:
                print(f"   ✗ Flight search failed: {exc}\n")
                if progress_callback:
                    progress_callback("error", f"Flight search failed: {exc}")
        
        # Step 2: Get hotels
        if self.hotel_agent_url:
            if progress_callback:
                progress_callback("status", "Searching hotels...")
            print("Step 2: Searching hotels...")
            try:
                hotels_data = self._a2a_send(
                    self.hotel_agent_url,
                    "search_hotels",
                    {
                        "location": destination,
                        "check_in": start_date_str,
                        "check_out": end_date_str,
                        "guests": 1,
                        "budget": budget
                    }
                )
                travel_plan["hotels"] = hotels_data
                print(f"   ✓ Found {hotels_data.get('count', 0)} hotels\n")
                if progress_callback:
                    progress_callback("hotels", hotels_data)
            except Exception as exc:
                print(f"   ✗ Hotel search failed: {exc}\n")
                if progress_callback:
                    progress_callback("error", f"Hotel search failed: {exc}")
        
        # Step 3: Get activities
        if self.activity_agent_url:
            if progress_callback:
                progress_callback("status", "Finding activities...")
            print("Step 3: Planning activities...")
            try:
                activities_data = self._a2a_send(
                    self.activity_agent_url,
                    "search_activities",
                    {
                        "location": destination,
                        "date": start_date_str,
                        "interests": interests,
                        "budget": budget
                    }
                )
                travel_plan["activities"] = activities_data
                print(f"   ✓ Found {activities_data.get('count', 0)} activities\n")
                if progress_callback:
                    progress_callback("activities", activities_data)
            except Exception as exc:
                print(f"   ✗ Activity search failed: {exc}\n")
                if progress_callback:
                    progress_callback("error", f"Activity search failed: {exc}")
        
        # Step 4: Get local guide information
        if self.guide_agent_url:
            if progress_callback:
                progress_callback("status", "Getting local guide info...")
            print("Step 4: Getting local tips...")
            try:
                guide_data = self._a2a_send(
                    self.guide_agent_url,
                    "get_local_info",
                    {
                        "location": destination,
                        "topics": ["culture", "food", "transportation", "safety"]
                    }
                )
                travel_plan["local_guide"] = guide_data
                print(f"   ✓ Received local guide information\n")
                if progress_callback:
                    progress_callback("guide", guide_data)
            except Exception as exc:
                print(f"   ✗ Guide info failed: {exc}\n")
                if progress_callback:
                    progress_callback("error", f"Guide info failed: {exc}")

        # Step 5: Create comprehensive summary with AI
        if progress_callback:
            progress_callback("status", "Creating full itinerary...")
        print("Step 5: Creating comprehensive plan...")
        if self.use_openai:
            summary_prompt = f"""Create a comprehensive, well-organized travel summary for this trip:

                                Destination: {destination}
                                Start Date: {start_date_str}
                                Duration: {duration} days
                                Budget: {budget}
                                Interests: {', '.join(interests)}

                                Available Information:
                                - Flights: {len(travel_plan.get('flights', {}).get('flights', []))} options found
                                - Hotels: {len(travel_plan.get('hotels', {}).get('hotels', []))} options found
                                - Activities: {len(travel_plan.get('activities', {}).get('activities', []))} options found
                                - Local guide information available

                                Create a day-by-day itinerary that:
                                1. Maximizes the traveler's interests
                                2. Stays within budget
                                3. Includes practical tips
                                4. Flows logically

                                Return Markdown only (no HTML). Use headings, bullet lists, and short paragraphs."""
            
            travel_plan["summary"] = self.call_openai(
                summary_prompt,
                temperature=0.7,
                max_tokens=2000
            )
            print(f"   ✓ Travel plan completed!\n")
            if progress_callback:
                progress_callback("summary", travel_plan["summary"])
        else:
            travel_plan["summary"] = f"Complete {duration}-day travel plan for {destination}"
            if progress_callback:
                progress_callback("summary", travel_plan["summary"])
        
        print(f"{'='*60}")
        print(f"✅ Trip planning complete!")
        print(f"{'='*60}\n")
        
        return travel_plan
    
    def answer_query(
        self,
        query: str,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Answer a general travel question
        
        This method determines which agent(s) to consult based on the query
        """
        print(f"💬 Processing query: {query}")
        
        # Use AI to understand the query and route appropriately
        if self.use_openai:
            routing_prompt = f"""Analyze this travel query and determine which specialized agents should handle it:

                                Query: {query}

                                Available agents:
                                - flight: For flight-related questions
                                - hotel: For accommodation questions
                                - activity: For things to do and activities
                                - guide: For local information, tips, and general travel advice

                                Respond with ONLY a JSON object in this format:
                                {{"agents": ["agent1", "agent2"], "reasoning": "brief explanation"}}"""
            
            routing = self.call_openai(routing_prompt, temperature=0.3, max_tokens=200)
            
            try:
                # Extract JSON from response
                routing = routing.strip()
                if routing.startswith("```"):
                    routing = routing.split("```")[1].replace("json", "").strip()
                routing_data = json.loads(routing)
                agents_to_query = routing_data.get("agents", ["guide"])
            except:
                # Default to guide agent if parsing fails
                agents_to_query = ["guide"]
            
            # Query the relevant agents
            responses = {}
            for agent_type in agents_to_query:
                agent_url = getattr(self, f"{agent_type}_agent_url", None)
                if agent_url:
                    # Determine appropriate action based on agent type
                    action_map = {
                        "guide": ("answer_question", {"location": "general", "question": query}),
                        "flight": ("recommend_flights", {"origin": "user_location", "destination": "query_location"}),
                        "hotel": ("recommend_hotels", {"location": "query_location"}),
                        "activity": ("recommend_activities", {"location": "query_location"})
                    }
                    
                    action, params = action_map.get(agent_type, ("answer_question", {"question": query}))
                    try:
                        responses[agent_type] = self._a2a_send(agent_url, action, params)
                    except Exception:
                        pass
            
            # Synthesize all responses
            synthesis_prompt = f"""Synthesize these responses into a helpful, comprehensive answer:

                                    Original query: {query}

                                    Agent responses:
                                    {json.dumps(responses, indent=2, default=str)}

                                    Provide a clear, helpful answer that addresses the user's question."""
            
            final_answer = self.call_openai(synthesis_prompt, temperature=0.6, max_tokens=1000)
        else:
            final_answer = f"Answer to: {query}"
        
        return {
            "query": query,
            "answer": final_answer,
            "sources": list(responses.keys()) if 'responses' in locals() else []
        }
    
    def get_recommendations(
        self,
        destination: str,
        category: str = "all"
    ) -> Dict[str, Any]:
        """Get recommendations for a specific category"""
        
        recommendations = {}
        
        if category in ["all", "flights"] and self.flight_agent_url:
            try:
                recommendations["flights"] = self._a2a_send(
                    self.flight_agent_url,
                    "recommend_flights",
                    {"destination": destination}
                )
            except Exception:
                pass
        
        if category in ["all", "hotels"] and self.hotel_agent_url:
            try:
                recommendations["hotels"] = self._a2a_send(
                    self.hotel_agent_url,
                    "recommend_hotels",
                    {"location": destination}
                )
            except Exception:
                pass
        
        return recommendations
