"""
Flask Web Application

Web UI for the Travel A2A Agent System
"""

import os
import json
from flask import Flask, render_template, request, jsonify
from flask import Response, stream_with_context
from flask_cors import CORS
from dotenv import load_dotenv

from agents import (
    TravelAgent,
    FlightAgent,
    HotelAgent,
    ActivityAgent,
    GuideAgent
)
from a2a_runtime import start_a2a_servers, DEFAULT_HOST, DEFAULT_PORTS

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize agents
print("🚀 Initializing Travel A2A Agent System...")

travel_agent = TravelAgent()
flight_agent = FlightAgent()
hotel_agent = HotelAgent()
activity_agent = ActivityAgent()
guide_agent = GuideAgent()

# Start A2A servers for specialized agents and connect travel agent
_A2A_STARTED = False
if not _A2A_STARTED:
    a2a_urls = start_a2a_servers(
        flight_agent=flight_agent,
        hotel_agent=hotel_agent,
        activity_agent=activity_agent,
        guide_agent=guide_agent
    )
    _A2A_STARTED = True
else:
    a2a_urls = {
        "flight": f"http://{DEFAULT_HOST}:{DEFAULT_PORTS['flight']}/",
        "hotel": f"http://{DEFAULT_HOST}:{DEFAULT_PORTS['hotel']}/",
        "activity": f"http://{DEFAULT_HOST}:{DEFAULT_PORTS['activity']}/",
        "guide": f"http://{DEFAULT_HOST}:{DEFAULT_PORTS['guide']}/"
    }
travel_agent.connect_to_agents(
    flight_agent_url=a2a_urls["flight"],
    hotel_agent_url=a2a_urls["hotel"],
    activity_agent_url=a2a_urls["activity"],
    guide_agent_url=a2a_urls["guide"]
)

print("✅ All agents ready!")

# Store agents for easy access
agents = {
    'travel': travel_agent,
    'flight': flight_agent,
    'hotel': hotel_agent,
    'activity': activity_agent,
    'guide': guide_agent
}


@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')


@app.route('/api/agents', methods=['GET'])
def get_agents():
    """Get list of all agents"""
    agent_list = [
        {
            "id": travel_agent.agent_id,
            "name": travel_agent.name,
            "type": travel_agent.agent_type,
            "status": "active",
            "capabilities": [cap.name for cap in travel_agent.capabilities]
        },
        {
            "id": flight_agent.agent_id,
            "name": flight_agent.name,
            "type": flight_agent.agent_type,
            "status": "active",
            "capabilities": [cap.name for cap in flight_agent.capabilities]
        },
        {
            "id": hotel_agent.agent_id,
            "name": hotel_agent.name,
            "type": hotel_agent.agent_type,
            "status": "active",
            "capabilities": [cap.name for cap in hotel_agent.capabilities]
        },
        {
            "id": activity_agent.agent_id,
            "name": activity_agent.name,
            "type": activity_agent.agent_type,
            "status": "active",
            "capabilities": [cap.name for cap in activity_agent.capabilities]
        },
        {
            "id": guide_agent.agent_id,
            "name": guide_agent.name,
            "type": guide_agent.agent_type,
            "status": "active",
            "capabilities": [cap.name for cap in guide_agent.capabilities]
        }
    ]
    return jsonify({
        'success': True,
        'agents': agent_list
    })


@app.route('/api/plan-trip', methods=['POST'])
def plan_trip():
    """Plan a complete trip"""
    try:
        data = request.json
        
        result = travel_agent.plan_trip(
            destination=data.get('destination'),
            duration=int(data.get('duration', 3)),
            budget=data.get('budget', 'medium'),
            interests=data.get('interests', ['culture']),
            origin=data.get('origin'),
            departure_date=data.get('departure_date')
        )
        
        return jsonify({
            'success': True,
            'data': result
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/plan-trip-stream', methods=['POST'])
def plan_trip_stream():
    """Plan a complete trip with streaming updates"""
    data = request.json or {}
    from threading import Thread
    from queue import Queue, Empty
    import json

    q: Queue = Queue()
    done_flag = {"done": False}

    def progress_callback(event_type, payload):
        q.put({"type": event_type, "data": payload})

    def worker():
        try:
            result = travel_agent.plan_trip(
                destination=data.get('destination'),
                duration=int(data.get('duration', 3)),
                budget=data.get('budget', 'medium'),
                interests=data.get('interests', ['culture']),
                origin=data.get('origin'),
                departure_date=data.get('departure_date'),
                progress_callback=progress_callback
            )
            q.put({"type": "done", "data": result})
        except Exception as e:
            q.put({"type": "error", "data": str(e)})
        finally:
            done_flag["done"] = True

    Thread(target=worker, daemon=True).start()

    def generate():
        while True:
            try:
                event = q.get(timeout=0.5)
            except Empty:
                if done_flag["done"]:
                    break
                continue

            if event["type"] == "summary":
                text = event["data"] or ""
                chunk_size = 400
                for i in range(0, len(text), chunk_size):
                    chunk = text[i:i + chunk_size]
                    yield json.dumps({"type": "summary_chunk", "data": chunk}) + "\n"
                continue

            yield json.dumps(event) + "\n"

            if event["type"] in ("done", "error"):
                break

    resp = Response(stream_with_context(generate()), mimetype='application/x-ndjson')
    resp.headers["Cache-Control"] = "no-cache"
    resp.headers["X-Accel-Buffering"] = "no"
    return resp


@app.route('/api/search-flights', methods=['POST'])
def search_flights():
    """Search for flights"""
    try:
        data = request.json
        
        result = flight_agent.search_flights(
            origin=data.get('origin'),
            destination=data.get('destination'),
            date=data.get('date'),
            passengers=int(data.get('passengers', 1)),
            class_type=data.get('class_type', 'economy')
        )
        
        return jsonify({
            'success': True,
            'data': result
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/search-hotels', methods=['POST'])
def search_hotels():
    """Search for hotels"""
    try:
        data = request.json
        
        result = hotel_agent.search_hotels(
            location=data.get('location'),
            check_in=data.get('check_in'),
            check_out=data.get('check_out'),
            guests=int(data.get('guests', 1)),
            rooms=int(data.get('rooms', 1)),
            budget=data.get('budget', 'medium')
        )
        
        return jsonify({
            'success': True,
            'data': result
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/search-activities', methods=['POST'])
def search_activities():
    """Search for activities"""
    try:
        data = request.json
        
        result = activity_agent.search_activities(
            location=data.get('location'),
            date=data.get('date'),
            interests=data.get('interests', ['culture']),
            budget=data.get('budget', 'medium')
        )
        
        return jsonify({
            'success': True,
            'data': result
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/get-guide-info', methods=['POST'])
def get_guide_info():
    """Get local guide information"""
    try:
        data = request.json
        
        result = guide_agent.get_local_info(
            location=data.get('location'),
            topics=data.get('topics', ['culture', 'food', 'transportation', 'safety'])
        )
        
        return jsonify({
            'success': True,
            'data': result
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/ask-question', methods=['POST'])
def ask_question():
    """Ask a travel question"""
    try:
        data = request.json
        
        result = travel_agent.answer_query(
            query=data.get('question')
        )
        
        return jsonify({
            'success': True,
            'data': result
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/agent-status/<agent_type>', methods=['GET'])
def get_agent_status(agent_type):
    """Get status of a specific agent"""
    try:
        if agent_type not in agents:
            return jsonify({
                'success': False,
                'error': f'Agent type {agent_type} not found'
            }), 404
        
        status = agents[agent_type].get_status()
        
        return jsonify({
            'success': True,
            'data': status
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404


@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors"""
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True') == 'True'
    
    print(f"\n{'='*70}")
    print(f"🌐 Travel A2A Agent System - Web Interface")
    print(f"{'='*70}")
    print(f"Server running on: http://localhost:{port}")
    print(f"{'='*70}\n")
    
    app.run(debug=debug, port=port, host='0.0.0.0', use_reloader=False)
