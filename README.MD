# 🌍 Travel A2A (Agent-to-Agent) Protocol Project

## 📋 Project Overview

This project demonstrates a **multi-agent travel planning system** using the Agent-to-Agent (A2A) protocol. Multiple specialized agents collaborate to help users plan complete travel itineraries.

### 🤖 Agents in the System

1. **Travel Agent (Coordinator)** - Main orchestrator that coordinates all other agents
2. **Flight Agent** - Handles flight bookings and searches
3. **Hotel Agent** - Manages hotel reservations
4. **Activity Agent** - Suggests and books activities
5. **Guide Agent** - Provides local tips and information

### 🏗️ Architecture

```
End User → Client → Travel Agent (Coordinator)
                         ↓
            ┌────────────┼────────────┐
            ↓            ↓            ↓
       Flight Agent  Hotel Agent  Activity Agent
                         ↓
                    Guide Agent
```

## 🚀 Getting Started

### Prerequisites

- Python 3.9 or higher
- OpenAI API Key
- SerpApi API Key (optional, for real-time flight/hotel/activity data)
- pip (Python package manager)

### Step 1: Clone or Download the Project

If you haven't already, navigate to the project directory:

```bash
cd travel-a2a-agents
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
py -3.12 -m venv .venv

# Activate it
# On Windows:
.venv\Scripts\Activate.ps1
# On Mac/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```
Or
```bash
python -m pip install -r requirements.txt
```

### Step 4: Set Up Environment Variables

Create a `.env` file in the project root:

```bash
# Create .env file
touch .env
```

Add your OpenAI & Serp API key:

```
OPENAI_API_KEY=your_openai_api_key_here
SERPAPI_API_KEY=your_serp_api_key_here
```

### Step 5: Run the Application

#### Option A: CLI Interface (Simple)
```bash
python main.py
```

#### Option B: Web UI (Recommended)
```bash
python app.py
```

Then open your browser to: `http://localhost:5000`

## 📁 Project Structure

```
travel-a2a-agents/
├── agents/
│   ├── __init__.py
│   ├── base_agent.py          # Base agent class with A2A protocol
│   ├── travel_agent.py        # Main coordinator agent
│   ├── flight_agent.py        # Flight booking agent
│   ├── hotel_agent.py         # Hotel reservation agent
│   ├── activity_agent.py      # Activity planning agent
│   └── guide_agent.py         # Local guide agent
├── a2a_protocol/
│   ├── __init__.py
│   ├── protocol.py            # A2A protocol implementation
│   └── message_types.py       # Message schemas
├── templates/
│   └── index.html             # Web UI interface
├── static/
│   ├── css/
│   │   └── style.css         # Styling
│   └── js/
│       └── app.js            # Frontend logic
├── main.py                    # CLI entry point
├── app.py                     # Web UI entry point
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables
└── README.md                  # This file
```

## 🔧 How It Works

### A2A Protocol Basics

The Agent-to-Agent protocol enables autonomous agents to:
1. **Discover** other agents in the network
2. **Communicate** using standardized messages
3. **Delegate** tasks to specialized agents
4. **Coordinate** complex workflows

### Message Flow Example

```
User: "Plan a trip to Paris for 3 days"
  ↓
Travel Agent: Analyzes request
  ↓
├→ Flight Agent: "Find flights to Paris"
├→ Hotel Agent: "Find hotels in Paris for 3 nights"
├→ Activity Agent: "Suggest activities in Paris"
└→ Guide Agent: "Get local tips for Paris"
  ↓
Travel Agent: Aggregates responses
  ↓
User: Receives complete itinerary
```

## 💻 Usage Examples

### Example 1: Complete Trip Planning

```python
# Using the Travel Agent
travel_agent = TravelAgent()

request = {
    "destination": "Paris",
    "duration": 3,
    "budget": "medium",
    "interests": ["museums", "food"]
}

result = travel_agent.plan_trip(request)
print(result)
```

### Example 2: Direct Agent Communication

```python
# Using specific agents
flight_agent = FlightAgent()

flights = flight_agent.search_flights(
    origin="New York",
    destination="Paris",
    date="2024-06-01"
)
```

## 🎯 Features

### ✅ Implemented Features

- **Multi-agent coordination** using A2A protocol
- **Strands Agents + OpenAI integration** for intelligent responses
- **Web UI** for easy interaction
- **CLI interface** for programmatic access
- **Mock data** for testing without external APIs
- **SerpApi integration** for live flight/hotel/activity search (when available)
- **Conversation history** tracking
- **Agent discovery** and registration
- **Task delegation** between agents

### 🔜 Future Enhancements

- Real API integrations (Amadeus, Booking.com)
- Database persistence
- User authentication
- Payment processing
- Multi-language support
- Mobile app

## 🧪 Testing

### Run Unit Tests
```bash
python -m pytest tests/
```

### Test Individual Agents
```bash
# Test Flight Agent
python -c "from agents.flight_agent import FlightAgent; agent = FlightAgent(); print(agent.search_flights('NYC', 'Paris', '2024-06-01'))"
```

## 🐛 Troubleshooting

### Issue: OpenAI API Key Error
**Solution**: Make sure your `.env` file contains a valid OpenAI API key

### Issue: Flights return mock data
**Solution**: Google Flights via SerpApi requires valid airport identifiers.  
Use **IATA airport codes** (e.g., `LAX`, `JFK`) or `/m/` location IDs instead of city names.

### Issue: Port Already in Use
**Solution**: Change the port in `app.py`:
```python
app.run(debug=True, port=5001)  # Change to different port
```

### Issue: Module Not Found
**Solution**: Make sure you're in the virtual environment and all packages are installed:
```bash
pip install -r requirements.txt
```

## 📚 Learning Resources

### A2A Protocol
- [A2A Protocol Specification](https://github.com/agent-to-agent/a2a-protocol)
- [Multi-Agent Systems Guide](https://www.microsoft.com/en-us/research/project/autogen/)

### Python Agent Development
- [OpenAI Python SDK](https://github.com/openai/openai-python)
- [LangChain Documentation](https://python.langchain.com/)

## 🤝 Contributing

Contributions are welcome.

For setup, workflow, quality expectations, and pull request guidance, see [CONTRIBUTING.md](CONTRIBUTING.md).

## 📝 License

MIT License - Feel free to use this for learning and development

## 👨‍💻 Support

If you have questions or run into issues:
1. Check the troubleshooting section
2. Review the code comments
3. Create an issue in the repository

## 🎓 Learning Path

### For Beginners:

1. **Start Here**: Run the CLI version (`main.py`)
2. **Understand**: Read through `base_agent.py` to understand the A2A protocol
3. **Explore**: Look at individual agent implementations
4. **Experiment**: Modify agent behaviors and add new capabilities
5. **Build**: Create your own specialized agent

### Next Steps:

- Learn about prompt engineering for better agent responses
- Study multi-agent coordination patterns
- Integrate real APIs for production use
- Deploy the application to a cloud service

---

**Happy Learning! 🚀**
