"""
Flight Agent

Specialized agent for handling flight searches and bookings
"""

from typing import Dict, Any, Optional
import random
from datetime import datetime, timedelta
import re
import requests

from .base_agent import BaseAgent


class FlightAgent(BaseAgent):
    """
    Flight Agent - Handles flight searches and bookings
    
    Capabilities:
    - Search for flights
    - Get flight details
    - Provide flight recommendations
    """
    
    def __init__(self):
        capabilities = [
            {
                "name": "search_flights",
                "description": "Search for available flights",
                "parameters": {
                    "origin": "str",
                    "destination": "str",
                    "date": "str",
                    "passengers": "int"
                }
            },
            {
                "name": "get_flight_details",
                "description": "Get details of a specific flight",
                "parameters": {"flight_id": "str"}
            }
        ]
        
        system_prompt = """You are a Flight Agent specialized in finding and booking flights.
                            You have access to flight databases and can provide:
                            - Flight searches based on origin, destination, and dates
                            - Flight recommendations based on price, duration, and convenience
                            - Real-time availability and pricing
                            - Alternative flight options

                            Always provide helpful, accurate information about flights. Consider factors like:
                            - Price competitiveness
                            - Travel duration
                            - Number of stops
                            - Airline reputation
                            - Departure and arrival times"""
        
        super().__init__(
            name="Flight Agent",
            agent_type="flight",
            capabilities=capabilities,
            system_prompt=system_prompt
        )
        
        # Mock flight data
        self.airlines = ["United", "Delta", "American", "Emirates", "Lufthansa", "Air France"]
        self.aircraft = ["Boeing 737", "Boeing 777", "Airbus A320", "Airbus A380"]
        self._location_cache = {}
    
    def process_request(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Process flight-related requests"""
        
        if action == "search_flights":
            return self.search_flights(**parameters)
        elif action == "get_flight_details":
            return self.get_flight_details(**parameters)
        elif action == "recommend_flights":
            return self.recommend_flights(**parameters)
        else:
            raise ValueError(f"Unknown action: {action}")
    
    def search_flights(
        self,
        origin: str,
        destination: str,
        date: str,
        passengers: int = 1,
        class_type: str = "economy"
    ) -> Dict[str, Any]:
        """
        Search for flights
        
        Returns mock flight data or AI-generated recommendations
        """
        print(f"🛫 Searching flights: {origin} → {destination} on {date}")
        
        flights = []
        serpapi_data = None
        if self.serpapi_key:
            departure_id = self._resolve_location_id(origin)
            arrival_id = self._resolve_location_id(destination)
            if self._is_valid_flight_location_id(departure_id) and self._is_valid_flight_location_id(arrival_id):
                serpapi_data = self._serpapi_search({
                    "engine": "google_flights",
                    "departure_id": departure_id,
                    "arrival_id": arrival_id,
                    "outbound_date": date,
                    "type": 2,
                    "travel_class": self._map_travel_class(class_type),
                    "adults": passengers,
                    "hl": "en",
                    "gl": "us",
                    "currency": "USD"
                })
                flights = self._parse_serpapi_flights(serpapi_data, origin, destination, date, class_type)
            else:
                print("Skipping SerpApi flights: invalid location IDs. "
                      "Use IATA airport codes or /m/ location IDs for real-time results.")
        
        if not flights:
            # Generate mock flight data
            flights = self._generate_mock_flights(origin, destination, date, passengers, class_type)
        
        # Use OpenAI for recommendations if available
        if self.use_openai:
            prompt = f"""Find the best flights from {origin} to {destination} on {date} for {passengers} passengers.
                        Consider price, duration, and convenience. Here are the available options:

                        {self._format_flights_for_ai(flights)}

                        Provide a brief recommendation highlighting the best value option.
                        Return Markdown only (no HTML)."""
            
            recommendation = self.call_openai(prompt, temperature=0.5)
        else:
            recommendation = f"Found {len(flights)} flights from {origin} to {destination}"
        
        return {
            "flights": flights,
            "count": len(flights),
            "recommendation": recommendation,
            "search_params": {
                "origin": origin,
                "destination": destination,
                "date": date,
                "passengers": passengers,
                "class": class_type
            }
        }
    
    def get_flight_details(self, flight_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific flight"""
        # Mock implementation
        return {
            "flight_id": flight_id,
            "details": "Flight details would be fetched from a real API",
            "status": "available"
        }
    
    def recommend_flights(
        self,
        origin: str,
        destination: str,
        budget: str = "medium"
    ) -> Dict[str, Any]:
        """Get AI-powered flight recommendations"""
        
        if self.use_openai:
            prompt = f"""Recommend the best flights from {origin} to {destination} 
                        for a {budget} budget. Consider:
                        - Best time to fly
                        - Airlines to consider
                        - Tips for getting good deals
                        - What to expect on this route"""
            
            recommendation = self.call_openai(prompt)
        else:
            recommendation = f"Flights from {origin} to {destination} typically range from $300-$1200"
        
        return {
            "recommendation": recommendation,
            "budget": budget
        }

    def _map_travel_class(self, class_type: str) -> int:
        """Map class name to SerpApi travel_class values."""
        mapping = {
            "economy": 1,
            "premium_economy": 2,
            "business": 3,
            "first": 4
        }
        return mapping.get(class_type, 1)

    def _resolve_location_id(self, value: str) -> str:
        """Resolve a city/airport input to IATA or location kgmid if possible."""
        if not value:
            return value
        if value in self._location_cache:
            return self._location_cache[value]
        trimmed = value.strip()
        if trimmed.startswith("/m/"):
            self._location_cache[value] = trimmed
            return trimmed
        if re.fullmatch(r"[A-Za-z]{3}", trimmed):
            resolved = trimmed.upper()
            self._location_cache[value] = resolved
            return resolved
        self._location_cache[value] = trimmed
        return trimmed

    def _wikidata_freebase_id(self, query: str) -> Optional[str]:
        """Look up Wikidata Freebase ID (kgmid) for a location name."""
        try:
            search_resp = requests.get(
                "https://www.wikidata.org/w/api.php",
                params={
                    "action": "wbsearchentities",
                    "search": query,
                    "language": "en",
                    "format": "json"
                },
                timeout=15
            )
            search_resp.raise_for_status()
            search_data = search_resp.json()
            results = search_data.get("search") or []
            if not results:
                return None
            qid = results[0].get("id")
            if not qid:
                return None

            entity_resp = requests.get(
                f"https://www.wikidata.org/wiki/Special:EntityData/{qid}.json",
                timeout=15
            )
            entity_resp.raise_for_status()
            entity_data = entity_resp.json()
            entity = entity_data.get("entities", {}).get(qid, {})
            claims = entity.get("claims", {})
            freebase_claims = claims.get("P646") or []
            if not freebase_claims:
                return None
            mainsnak = freebase_claims[0].get("mainsnak", {})
            datavalue = mainsnak.get("datavalue", {})
            value = datavalue.get("value")
            if isinstance(value, str) and value.startswith("/m/"):
                return value
        except Exception as exc:
            print(f"âš ï¸ Wikidata lookup failed for {query}: {exc}")
        return None

    def _is_valid_flight_location_id(self, value: str) -> bool:
        if not value:
            return False
        trimmed = value.strip()
        if trimmed.startswith("/m/"):
            return True
        if re.fullmatch(r"[A-Z]{3}", trimmed):
            return True
        return False

    def _parse_serpapi_flights(
        self,
        data: Dict[str, Any],
        origin: str,
        destination: str,
        date: str,
        class_type: str
    ) -> list:
        """Parse SerpApi Google Flights results into internal format."""
        if not data or not isinstance(data, dict):
            return []
        
        options = []
        for key in ["best_flights", "other_flights"]:
            if isinstance(data.get(key), list):
                options.extend(data[key])
        
        flights = []
        currency = data.get("search_parameters", {}).get("currency", "USD")
        
        for idx, option in enumerate(options, 1):
            segments = option.get("flights") or []
            if not segments:
                continue
            
            price = option.get("price")
            total_duration = option.get("total_duration")
            duration_minutes = total_duration
            if duration_minutes is None:
                duration_minutes = sum(
                    seg.get("duration", 0) for seg in segments if isinstance(seg.get("duration"), int)
                )
            
            airline = segments[0].get("airline") or "Unknown"
            flight_number = segments[0].get("flight_number")
            departure_time = self._extract_time(segments[0].get("departure_airport", {}).get("time"))
            arrival_time = self._extract_time(segments[-1].get("arrival_airport", {}).get("time"))
            stops = max(len(segments) - 1, 0)
            
            flights.append({
                "flight_id": flight_number or f"SERP-{idx:03d}",
                "airline": airline,
                "aircraft": segments[0].get("airplane", ""),
                "origin": origin,
                "destination": destination,
                "departure_time": departure_time,
                "arrival_time": arrival_time,
                "duration": self._format_duration(duration_minutes),
                "stops": stops,
                "price": price if price is not None else 0,
                "currency": currency,
                "class": segments[0].get("travel_class", class_type),
                "seats_available": "N/A",
                "date": date
            })
        
        return flights

    def _extract_time(self, value: str) -> str:
        if not value:
            return "N/A"
        if " " in value:
            return value.split(" ")[-1]
        return value

    def _format_duration(self, minutes: int) -> str:
        if not isinstance(minutes, int) or minutes <= 0:
            return "N/A"
        hours = minutes // 60
        mins = minutes % 60
        return f"{hours}h {mins}m"
    
    def _generate_mock_flights(
        self,
        origin: str,
        destination: str,
        date: str,
        passengers: int,
        class_type: str
    ) -> list:
        """Generate mock flight data"""
        flights = []
        
        base_price = {
            "economy": 450,
            "business": 1500,
            "first": 3500
        }.get(class_type, 450)
        
        for i in range(3):
            airline = random.choice(self.airlines)
            aircraft = random.choice(self.aircraft)
            duration_hours = random.randint(2, 12)
            stops = random.randint(0, 2)
            
            price_variation = random.uniform(0.8, 1.4)
            price = int(base_price * price_variation * passengers)
            
            flights.append({
                "flight_id": f"FL{random.randint(1000, 9999)}",
                "airline": airline,
                "aircraft": aircraft,
                "origin": origin,
                "destination": destination,
                "departure_time": f"{random.randint(6, 20):02d}:{random.choice(['00', '15', '30', '45'])}",
                "arrival_time": f"{random.randint(8, 22):02d}:{random.choice(['00', '15', '30', '45'])}",
                "duration": f"{duration_hours}h {random.randint(0, 59)}m",
                "stops": stops,
                "price": price,
                "currency": "USD",
                "class": class_type,
                "seats_available": random.randint(10, 150),
                "date": date
            })
        
        # Sort by price
        flights.sort(key=lambda x: x['price'])
        
        return flights
    
    def _format_flights_for_ai(self, flights: list) -> str:
        """Format flight data for AI prompt"""
        formatted = []
        for i, flight in enumerate(flights, 1):
            formatted.append(
                f"{i}. {flight['airline']} {flight['flight_id']} - "
                f"${flight['price']} - {flight['duration']} - "
                f"{flight['stops']} stops - "
                f"Departs {flight['departure_time']}"
            )
        return "\n".join(formatted)
