"""
Main CLI Application

Command-line interface for the Travel A2A Agent System
"""

import os
from datetime import datetime
from dotenv import load_dotenv

from agents import (
    TravelAgent,
    FlightAgent,
    HotelAgent,
    ActivityAgent,
    GuideAgent
)
from a2a_runtime import start_a2a_servers


def print_banner():
    """Print welcome banner"""
    print("\n" + "="*70)
    print("✈️  TRAVEL A2A AGENT SYSTEM - Command Line Interface")
    print("="*70)
    print("Multi-agent travel planning using Agent-to-Agent protocol")
    print("="*70 + "\n")


def initialize_agents():
    """Initialize all agents in the system"""
    print("🚀 Initializing agents...\n")
    
    # Create all agents
    travel_agent = TravelAgent()
    flight_agent = FlightAgent()
    hotel_agent = HotelAgent()
    activity_agent = ActivityAgent()
    guide_agent = GuideAgent()
    
    # Start A2A servers for specialized agents and connect travel agent
    a2a_urls = start_a2a_servers(
        flight_agent=flight_agent,
        hotel_agent=hotel_agent,
        activity_agent=activity_agent,
        guide_agent=guide_agent
    )
    travel_agent.connect_to_agents(
        flight_agent_url=a2a_urls["flight"],
        hotel_agent_url=a2a_urls["hotel"],
        activity_agent_url=a2a_urls["activity"],
        guide_agent_url=a2a_urls["guide"]
    )
    
    print("\n✅ All agents initialized and connected!\n")
    
    return travel_agent, flight_agent, hotel_agent, activity_agent, guide_agent


def print_menu():
    """Print main menu"""
    print("\n" + "-"*70)
    print("MAIN MENU")
    print("-"*70)
    print("1. Plan a Complete Trip")
    print("2. Search Flights Only")
    print("3. Search Hotels Only")
    print("4. Find Activities")
    print("5. Get Local Guide Information")
    print("6. Ask a Travel Question")
    print("7. View All Agents")
    print("8. Exit")
    print("-"*70)


def plan_complete_trip(travel_agent):
    """Interactive trip planning"""
    print("\n🌍 PLAN YOUR TRIP")
    print("-"*70)
    
    destination = input("Destination: ")
    departure_date = None
    while not departure_date:
        date_input = input("Start date (YYYY-MM-DD): ").strip()
        try:
            datetime.strptime(date_input, "%Y-%m-%d")
            departure_date = date_input
        except ValueError:
            print("âŒ Invalid date format. Please use YYYY-MM-DD.")
    
    duration = int(input("Duration (days): "))
    budget = input("Budget (low/medium/high): ").lower()
    
    interests_input = input("Interests (comma-separated, e.g., culture,food,adventure): ")
    interests = [i.strip() for i in interests_input.split(",")] if interests_input else ["culture"]
    
    origin = input("Departure city (optional, press Enter to skip): ").strip()
    
    print("\n⏳ Planning your trip... This may take a moment.\n")
    
    # Plan the trip
    plan = travel_agent.plan_trip(
        destination=destination,
        duration=duration,
        budget=budget,
        interests=interests,
        origin=origin if origin else None,
        departure_date=departure_date
    )
    
    # Display results
    print("\n" + "="*70)
    print("YOUR TRAVEL PLAN")
    print("="*70)
    
    if "summary" in plan:
        print("\n📋 SUMMARY:")
        print(plan["summary"])
    
    if "flights" in plan and plan["flights"].get("flights"):
        print("\n✈️  TOP FLIGHTS:")
        for i, flight in enumerate(plan["flights"]["flights"][:3], 1):
            print(f"{i}. {flight['airline']} {flight['flight_id']} - ${flight['price']}")
            print(f"   {flight['departure_time']} - {flight['duration']} - {flight['stops']} stops")
    
    if "hotels" in plan and plan["hotels"].get("hotels"):
        print("\n🏨 TOP HOTELS:")
        for i, hotel in enumerate(plan["hotels"]["hotels"][:3], 1):
            print(f"{i}. {hotel['name']} ({'⭐'*hotel['stars']})")
            print(f"   ${hotel['price_per_night']}/night - Rating: {hotel['rating']}/5.0")
    
    if "activities" in plan and plan["activities"].get("activities"):
        print("\n🎭 SUGGESTED ACTIVITIES:")
        for i, activity in enumerate(plan["activities"]["activities"][:5], 1):
            print(f"{i}. {activity['name']} - ${activity['price']}")
            print(f"   {activity['duration']} - {activity['category']}")
    
    print("\n" + "="*70)


def search_flights(flight_agent):
    """Search for flights"""
    print("\n✈️  FLIGHT SEARCH")
    print("-"*70)
    
    origin = input("From: ")
    destination = input("To: ")
    date = input("Date (YYYY-MM-DD): ")
    
    result = flight_agent.search_flights(
        origin=origin,
        destination=destination,
        date=date
    )
    
    print("\n📋 SEARCH RESULTS:")
    print(result.get("recommendation", ""))
    
    print("\n✈️  AVAILABLE FLIGHTS:")
    for i, flight in enumerate(result["flights"], 1):
        print(f"\n{i}. {flight['airline']} {flight['flight_id']}")
        print(f"   Price: ${flight['price']}")
        print(f"   Departure: {flight['departure_time']} | Arrival: {flight['arrival_time']}")
        print(f"   Duration: {flight['duration']} | Stops: {flight['stops']}")


def search_hotels(hotel_agent):
    """Search for hotels"""
    print("\n🏨 HOTEL SEARCH")
    print("-"*70)
    
    location = input("Location: ")
    check_in = input("Check-in (YYYY-MM-DD): ")
    check_out = input("Check-out (YYYY-MM-DD): ")
    
    result = hotel_agent.search_hotels(
        location=location,
        check_in=check_in,
        check_out=check_out
    )
    
    print("\n📋 SEARCH RESULTS:")
    print(result.get("recommendation", ""))
    
    print("\n🏨 AVAILABLE HOTELS:")
    for i, hotel in enumerate(result["hotels"], 1):
        print(f"\n{i}. {hotel['name']} ({'⭐'*hotel['stars']})")
        print(f"   Price: ${hotel['price_per_night']}/night")
        print(f"   Rating: {hotel['rating']}/5.0 ({hotel['reviews_count']} reviews)")
        print(f"   Distance: {hotel['distance_to_center']} from center")
        print(f"   Amenities: {', '.join(hotel['amenities'][:4])}")


def find_activities(activity_agent):
    """Find activities"""
    print("\n🎭 ACTIVITY SEARCH")
    print("-"*70)
    
    location = input("Location: ")
    interests_input = input("Interests (comma-separated): ")
    interests = [i.strip() for i in interests_input.split(",")]
    
    result = activity_agent.search_activities(
        location=location,
        interests=interests
    )
    
    print("\n📋 RECOMMENDATIONS:")
    print(result.get("recommendation", ""))
    
    print("\n🎭 AVAILABLE ACTIVITIES:")
    for i, activity in enumerate(result["activities"], 1):
        print(f"\n{i}. {activity['name']}")
        print(f"   Price: ${activity['price']} | Duration: {activity['duration']}")
        print(f"   Rating: {activity['rating']}/5.0 | Difficulty: {activity['difficulty']}")


def get_guide_info(guide_agent):
    """Get local guide information"""
    print("\n📍 LOCAL GUIDE")
    print("-"*70)
    
    location = input("Location: ")
    
    result = guide_agent.get_local_info(
        location=location,
        topics=["culture", "food", "transportation", "safety"]
    )
    
    print(f"\n📖 LOCAL GUIDE FOR {location.upper()}")
    print("="*70)
    print(result.get("information", ""))
    print("="*70)


def ask_question(travel_agent):
    """Ask a travel question"""
    print("\n💬 ASK A QUESTION")
    print("-"*70)
    
    question = input("Your question: ")
    
    print("\n⏳ Processing your question...\n")
    
    result = travel_agent.answer_query(query=question)
    
    print("\n📝 ANSWER:")
    print("="*70)
    print(result.get("answer", ""))
    print("="*70)


def view_agents(travel_agent, flight_agent, hotel_agent, activity_agent, guide_agent):
    """View all registered agents"""
    agents = [
        travel_agent,
        flight_agent,
        hotel_agent,
        activity_agent,
        guide_agent
    ]
    
    print(" REGISTERED AGENTS")
    print("="*70)
    for agent in agents:
        print(f"{agent.name}")
        print(f"  Type: {agent.agent_type}")
        print("  Status: active")
        print(f"  Capabilities: {', '.join([cap.name for cap in agent.capabilities])}")
    print("="*70)



def main():
    """Main application loop"""
    # Load environment variables
    load_dotenv()
    
    # Check for OpenAI API key
    if not os.getenv('OPENAI_API_KEY'):
        print("\n⚠️  WARNING: No OpenAI API key found!")
        print("The system will work with mock data, but AI features will be limited.")
        print("To enable full AI features:")
        print("1. Create a .env file in the project root")
        print("2. Add: OPENAI_API_KEY=your_key_here\n")
        input("Press Enter to continue...")
    
    print_banner()
    
    # Initialize agents
    travel_agent, flight_agent, hotel_agent, activity_agent, guide_agent = initialize_agents()
    
    # Main loop
    while True:
        print_menu()
        choice = input("\nSelect an option (1-8): ").strip()
        
        try:
            if choice == "1":
                plan_complete_trip(travel_agent)
            elif choice == "2":
                search_flights(flight_agent)
            elif choice == "3":
                search_hotels(hotel_agent)
            elif choice == "4":
                find_activities(activity_agent)
            elif choice == "5":
                get_guide_info(guide_agent)
            elif choice == "6":
                ask_question(travel_agent)
            elif choice == "7":
                view_agents(travel_agent, flight_agent, hotel_agent, activity_agent, guide_agent)
            elif choice == "8":
                print("\n👋 Thank you for using Travel A2A! Safe travels!")
                break
            else:
                print("\n❌ Invalid option. Please try again.")
        except KeyboardInterrupt:
            print("\n\n👋 Exiting... Safe travels!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("Please try again.")
        
        input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()
