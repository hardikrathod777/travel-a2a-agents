"""
Hotel Agent

Specialized agent for handling hotel searches and bookings
"""

from typing import Dict, Any
from datetime import datetime
import re
import random

from .base_agent import BaseAgent


class HotelAgent(BaseAgent):
    """
    Hotel Agent - Handles hotel searches and reservations
    
    Capabilities:
    - Search for hotels
    - Get hotel details
    - Provide hotel recommendations
    """
    
    def __init__(self):
        capabilities = [
            {
                "name": "search_hotels",
                "description": "Search for available hotels",
                "parameters": {
                    "location": "str",
                    "check_in": "str",
                    "check_out": "str",
                    "guests": "int",
                    "budget": "str"
                }
            },
            {
                "name": "get_hotel_details",
                "description": "Get details of a specific hotel",
                "parameters": {"hotel_id": "str"}
            }
        ]
        
        system_prompt = """You are a Hotel Agent specialized in finding and booking accommodations.
                            You have access to hotel databases and can provide:
                            - Hotel searches based on location, dates, and preferences
                            - Hotel recommendations based on price, amenities, and location
                            - Real-time availability and rates
                            - Alternative accommodation options

                            Always provide helpful, accurate information about hotels. Consider factors like:
                            - Price range and value for money
                            - Location convenience
                            - Amenities (WiFi, parking, breakfast, pool, gym)
                            - Guest ratings and reviews
                            - Cancellation policies"""
        
        super().__init__(
            name="Hotel Agent",
            agent_type="hotel",
            capabilities=capabilities,
            system_prompt=system_prompt
        )
        
        # Mock hotel data
        self.hotel_chains = [
            "Marriott", "Hilton", "Hyatt", "InterContinental",
            "Radisson", "Holiday Inn", "Best Western", "Sheraton"
        ]
        self.amenities = [
            "Free WiFi", "Pool", "Gym", "Restaurant",
            "Bar", "Spa", "Room Service", "Parking",
            "Business Center", "Airport Shuttle"
        ]
    
    def process_request(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Process hotel-related requests"""
        
        if action == "search_hotels":
            return self.search_hotels(**parameters)
        elif action == "get_hotel_details":
            return self.get_hotel_details(**parameters)
        elif action == "recommend_hotels":
            return self.recommend_hotels(**parameters)
        else:
            raise ValueError(f"Unknown action: {action}")
    
    def search_hotels(
        self,
        location: str,
        check_in: str,
        check_out: str,
        guests: int = 1,
        rooms: int = 1,
        budget: str = "medium"
    ) -> Dict[str, Any]:
        """
        Search for hotels
        
        Returns mock hotel data or AI-generated recommendations
        """
        print(f"🏨 Searching hotels in {location} ({check_in} to {check_out})")
        
        hotels = []
        serpapi_data = None
        if self.serpapi_key:
            serpapi_data = self._serpapi_search({
                "engine": "google_hotels",
                "q": location,
                "check_in_date": check_in,
                "check_out_date": check_out,
                "adults": guests,
                "hl": "en",
                "gl": "us",
                "currency": "USD"
            })
            hotels = self._parse_serpapi_hotels(serpapi_data, location, check_in, check_out, budget)
        
        if not hotels:
            # Generate mock hotel data
            hotels = self._generate_mock_hotels(location, budget, guests, rooms)
        
        # Use OpenAI for recommendations if available
        if self.use_openai:
            prompt = f"""Find the best hotels in {location} for {guests} guests checking in {check_in} and out {check_out}.
                        Budget level: {budget}. Here are the available options:

                        {self._format_hotels_for_ai(hotels)}

                        Provide a brief recommendation highlighting the best value option for this budget.
                        Return Markdown only (no HTML)."""
            
            recommendation = self.call_openai(prompt, temperature=0.5)
        else:
            recommendation = f"Found {len(hotels)} hotels in {location} matching your criteria"
        
        return {
            "hotels": hotels,
            "count": len(hotels),
            "recommendation": recommendation,
            "search_params": {
                "location": location,
                "check_in": check_in,
                "check_out": check_out,
                "guests": guests,
                "rooms": rooms,
                "budget": budget
            }
        }
    
    def get_hotel_details(self, hotel_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific hotel"""
        return {
            "hotel_id": hotel_id,
            "details": "Full hotel details would be fetched from a real API",
            "available": True
        }
    
    def recommend_hotels(
        self,
        location: str,
        purpose: str = "leisure"
    ) -> Dict[str, Any]:
        """Get AI-powered hotel recommendations"""
        
        if self.use_openai:
            prompt = f"""Recommend the best hotels in {location} for {purpose} travel.
                        Consider:
                        - Best neighborhoods to stay in
                        - What type of accommodation suits this purpose
                        - Average prices to expect
                        - Special tips for finding good hotels in this area"""
            
            recommendation = self.call_openai(prompt)
        else:
            recommendation = f"Hotels in {location} for {purpose} typically range from $80-$300 per night"
        
        return {
            "recommendation": recommendation,
            "location": location,
            "purpose": purpose
        }

    def _parse_serpapi_hotels(
        self,
        data: Dict[str, Any],
        location: str,
        check_in: str,
        check_out: str,
        budget: str
    ) -> list:
        if not data or not isinstance(data, dict):
            return []
        
        properties = data.get("properties") or []
        nights = self._calculate_nights(check_in, check_out)
        hotels = []
        
        for idx, prop in enumerate(properties, 1):
            name = prop.get("name") or f"Hotel {idx}"
            rating = prop.get("overall_rating") or prop.get("rating") or 0
            reviews = prop.get("reviews") or prop.get("reviews_count") or 0
            stars = prop.get("hotel_class") or prop.get("stars") or 0
            price_per_night = self._extract_price(prop.get("rate_per_night"))
            total_price = self._extract_price(prop.get("total_rate"))
            
            if total_price is None and price_per_night is not None and nights:
                total_price = price_per_night * nights
            
            hotels.append({
                "hotel_id": prop.get("property_token") or f"SERP-H{idx:03d}",
                "name": name,
                "stars": int(stars) if str(stars).isdigit() else stars or 0,
                "rating": rating,
                "reviews_count": reviews,
                "price_per_night": price_per_night if price_per_night is not None else 0,
                "total_price": total_price if total_price is not None else 0,
                "currency": data.get("search_parameters", {}).get("currency", "USD"),
                "location": location,
                "distance_to_center": prop.get("distance_to_center") or "",
                "amenities": prop.get("amenities") or [],
                "rooms_available": prop.get("rooms_available"),
                "free_cancellation": bool(prop.get("free_cancellation", False))
            })
        
        hotels.sort(key=lambda x: x.get("rating", 0), reverse=True)
        return hotels

    def _calculate_nights(self, check_in: str, check_out: str) -> int:
        try:
            in_date = datetime.strptime(check_in, "%Y-%m-%d")
            out_date = datetime.strptime(check_out, "%Y-%m-%d")
            nights = (out_date - in_date).days
            return max(nights, 1)
        except Exception:
            return 0

    def _extract_price(self, value) -> int:
        if value is None:
            return None
        if isinstance(value, dict):
            extracted = value.get("extracted_lowest") or value.get("extracted")
            if extracted is not None:
                return int(extracted)
            value = value.get("lowest") or value.get("price") or ""
        if isinstance(value, (int, float)):
            return int(value)
        if isinstance(value, str):
            match = re.search(r"(\\d+[\\d,]*)", value)
            if match:
                return int(match.group(1).replace(",", ""))
        return None
    
    def _generate_mock_hotels(
        self,
        location: str,
        budget: str,
        guests: int,
        rooms: int
    ) -> list:
        """Generate mock hotel data"""
        hotels = []
        
        price_ranges = {
            "low": (50, 120),
            "medium": (100, 250),
            "high": (200, 500)
        }
        
        min_price, max_price = price_ranges.get(budget, (100, 250))
        
        for i in range(4):
            hotel_name = f"{random.choice(self.hotel_chains)} {location}"
            stars = random.randint(3, 5)
            rating = round(random.uniform(3.5, 4.9), 1)
            price_per_night = random.randint(min_price, max_price)
            
            # Select random amenities
            num_amenities = random.randint(4, 8)
            selected_amenities = random.sample(self.amenities, num_amenities)
            
            hotels.append({
                "hotel_id": f"HTL{random.randint(1000, 9999)}",
                "name": hotel_name,
                "stars": stars,
                "rating": rating,
                "reviews_count": random.randint(100, 2000),
                "price_per_night": price_per_night,
                "total_price": price_per_night * 3,  # Assuming 3 nights
                "currency": "USD",
                "location": location,
                "distance_to_center": f"{random.uniform(0.5, 5.0):.1f} km",
                "amenities": selected_amenities,
                "rooms_available": random.randint(1, 20),
                "free_cancellation": random.choice([True, False])
            })
        
        # Sort by rating
        hotels.sort(key=lambda x: x['rating'], reverse=True)
        
        return hotels
    
    def _format_hotels_for_ai(self, hotels: list) -> str:
        """Format hotel data for AI prompt"""
        formatted = []
        for i, hotel in enumerate(hotels, 1):
            formatted.append(
                f"{i}. {hotel['name']} ({hotel['stars']}★) - "
                f"${hotel['price_per_night']}/night - "
                f"Rating: {hotel['rating']} ({hotel['reviews_count']} reviews) - "
                f"{hotel['distance_to_center']} from center"
            )
        return "\n".join(formatted)
