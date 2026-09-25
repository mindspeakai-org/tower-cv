import json
from typing import Dict, Any

try:
    # Example placeholder if we were to use a local LLM runner like Ollama
    # import requests
    pass
except ImportError:
    pass

class EventInterpreter:
    """
    Translates raw JSON contextual events into natural language notifications 
    using a local LLM or rule-based templates.
    """
    def __init__(self, use_llm: bool = False, model: str = "llama3"):
        self.use_llm = use_llm
        self.model = model
        
    def _rule_based_translation(self, event: Dict[str, Any]) -> str:
        """
        A fallback rule-based system when an LLM is not available or too slow.
        """
        event_type = event.get("type")
        desc = event.get("description", "")
        zone = event.get("zone")
        pose = event.get("pose")
        
        if event_type == "stationary_prolonged":
            if pose == "lying_down":
                return f"It looks like {event.get('object_id')} is resting or taking a nap{' in the ' + zone if zone else ''}."
            elif pose == "sitting_or_bending":
                return f"{event.get('object_id')} has been sitting{' in the ' + zone if zone else ''} for a while."
            else:
                return f"{event.get('object_id')} has been standing still{' in the ' + zone if zone else ''}."
                
        elif event_type == "pose_changed":
            if pose == "lying_down":
                return f"Attention: {event.get('object_id')} just lay down or fell{' in the ' + zone if zone else ''}."
                
        elif event_type == "zone_entered":
            return f"{event.get('object_id')} just entered the {zone}."
            
        elif event_type == "object_left":
            return f"{event.get('object_id')} left the camera view."
            
        elif event_type == "audio_detected":
            sound = event.get("sound_class", "a sound").replace("_", " ")
            return f"Tower heard {sound}."

    def translate(self, event: Dict[str, Any]) -> str:
        """
        Converts the event dictionary into a human-readable string.
        """
        if not self.use_llm:
            return self._rule_based_translation(event)
            
        # Example LLM integration via local Ollama API
        prompt = f"""
        You are Tower, an intelligent home monitor context engine.
        Translate the following raw JSON event into a single, natural, and friendly sentence for the homeowner.
        Focus on the meaning, not the technical details.
        Event: {json.dumps(event)}
        """
        
        print(f"[LLM Prompt] -> {prompt.strip()}")
        # In a real setup, we would POST to http://localhost:11434/api/generate
        # response = requests.post('http://localhost:11434/api/generate', json={'model': self.model, 'prompt': prompt, 'stream': False})
        # return response.json()['response'].strip()
        
        # Returning fallback for now since we don't have a live endpoint here
        return self._rule_based_translation(event)

if __name__ == "__main__":
    # Test the interpreter
    interpreter = EventInterpreter()
    sample_event = {
        "type": "stationary_prolonged",
        "description": "The person (person_1) has been stationary in front_door for over 10 seconds.",
        "object_id": "person_1",
        "timestamp": 1690000000.0,
        "zone": "front_door",
        "pose": "sitting_or_bending"
    }
    
    print("Raw Event:")
    print(json.dumps(sample_event, indent=2))
    print("\nTower Translation:")
    print(interpreter.translate(sample_event))
