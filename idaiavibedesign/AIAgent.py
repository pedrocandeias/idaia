import json
import re
import requests
import FreeCAD
from typing import Dict, List, Optional, Any
import threading
import time

class AIAgentConfig:
    """Configuration for AI agents"""
    
    def __init__(self):
        self.provider = "ollama"  # ollama, openai, or anthropic
        self.model = "llama3.1:8b"
        self.api_key = ""
        self.base_url = "http://localhost:11434/v1"
        self.timeout = 120  # Increase timeout for complex requests
        self.max_retries = 2   # Reduce retries to avoid memory buildup
        self.temperature = 0.1
        
    def to_dict(self):
        return {
            "provider": self.provider,
            "model": self.model,
            "api_key": self.api_key,
            "base_url": self.base_url,
            "timeout": self.timeout,
            "max_retries": self.max_retries,
            "temperature": self.temperature
        }
    
    def from_dict(self, data):
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)

class AIAgent:
    """AI Agent for processing natural language CAD commands"""
    
    def __init__(self, config: AIAgentConfig):
        self.config = config
        self.conversation_history = []
        self.context = {
            "active_document": None,
            "created_objects": [],
            "last_command": None
        }
        
    def process_prompt(self, user_prompt: str, context: Dict = None) -> Dict[str, Any]:
        """Process a natural language prompt and return structured CAD commands"""
        
        if context:
            self.context.update(context)
            
        system_prompt = self._get_system_prompt()
        
        try:
            response = self._call_llm(system_prompt, user_prompt)
            parsed_response = self._parse_ai_response(response)
            
            # Update conversation history
            self.conversation_history.append({
                "user": user_prompt,
                "assistant": response,
                "timestamp": time.time(),
                "parsed": parsed_response
            })
            
            # Keep only last 5 conversations to prevent memory buildup
            if len(self.conversation_history) > 5:
                self.conversation_history = self.conversation_history[-5:]
            
            return parsed_response
            
        except Exception as e:
            FreeCAD.Console.PrintError(f"AI Agent Error: {str(e)}\n")
            return {"error": str(e), "fallback": True}
    
    def _get_system_prompt(self) -> str:
        """Generate system prompt with current context"""
        
        base_prompt = """You are a specialized AI assistant for FreeCAD CAD modeling. Your job is to interpret natural language descriptions and convert them into structured CAD commands.

AVAILABLE SHAPES:
- Box/Cube: rectangular solids
- Cylinder: circular tubes/pipes
- Sphere: round balls
- Cone: pointed circular objects
- Torus: donut shapes
- Wedge: triangular prisms
- Hexagon: six-sided prisms

SUPPORTED OPERATIONS:
- Create new objects
- Modify existing objects (move, rotate, scale)
- Boolean operations (union, difference, intersection)
- Patterns (linear, polar arrays)

UNITS: mm, cm, dm, m, in, ft (default: mm)

RESPONSE FORMAT:
Return a JSON object with this structure:
{
  "commands": [
    {
      "type": "create",
      "shape": "box|cylinder|sphere|cone|torus|wedge|hexagon",
      "dimensions": {"length": 10, "width": 10, "height": 10},
      "position": {"x": 0, "y": 0, "z": 0},
      "rotation": {"x": 0, "y": 0, "z": 0},
      "name": "object_name"
    }
  ],
  "explanation": "Brief explanation of what will be created",
  "confidence": 0.95
}

For complex operations, break them into multiple commands.
Always include dimensions in millimeters.
Be precise with object names and positions."""

        # Add context information
        if self.context.get("created_objects"):
            base_prompt += f"\n\nCURRENT OBJECTS IN SCENE: {', '.join(self.context['created_objects'])}"
        
        if self.context.get("last_command"):
            base_prompt += f"\n\nLAST COMMAND: {self.context['last_command']}"
        
        return base_prompt
    
    def _call_llm(self, system_prompt: str, user_prompt: str) -> str:
        """Call the configured LLM API"""
        
        headers = {
            "Content-Type": "application/json"
        }
        
        if self.config.provider == "openai":
            headers["Authorization"] = f"Bearer {self.config.api_key}"
        elif self.config.provider == "anthropic":
            headers["x-api-key"] = self.config.api_key
            headers["anthropic-version"] = "2023-06-01"
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        # Add conversation history for context (limited to reduce memory usage)
        for entry in self.conversation_history[-2:]:  # Last 2 exchanges only
            messages.insert(-1, {"role": "user", "content": entry["user"]})
            messages.insert(-1, {"role": "assistant", "content": entry["assistant"]})
        
        data = {
            "model": self.config.model,
            "messages": messages,
            "temperature": self.config.temperature,
            "max_tokens": 1000
        }
        
        for attempt in range(self.config.max_retries):
            try:
                response = requests.post(
                    f"{self.config.base_url}/chat/completions",
                    headers=headers,
                    json=data,
                    timeout=self.config.timeout
                )
                response.raise_for_status()
                
                result = response.json()
                return result["choices"][0]["message"]["content"]
                
            except requests.exceptions.HTTPError as e:
                # Handle specific HTTP errors
                if hasattr(e.response, 'status_code'):
                    status_code = e.response.status_code
                    if status_code == 500:
                        error_msg = f"Ollama server error (500) - likely memory/resource issue. Try a smaller model or restart Ollama."
                        if attempt == self.config.max_retries - 1:
                            raise Exception(error_msg)
                        FreeCAD.Console.PrintWarning(f"Attempt {attempt + 1}: {error_msg} Retrying...\n")
                        time.sleep(5)  # Longer wait for server errors
                    elif status_code == 404:
                        raise Exception(f"Model '{self.config.model}' not found. Check if model is installed: ollama pull {self.config.model}")
                    elif status_code == 429:
                        if attempt == self.config.max_retries - 1:
                            raise Exception("Too many requests. Please wait and try again.")
                        time.sleep(10)  # Wait longer for rate limits
                    else:
                        if attempt == self.config.max_retries - 1:
                            raise Exception(f"HTTP {status_code}: {str(e)}")
                        time.sleep(2 ** attempt)
                else:
                    if attempt == self.config.max_retries - 1:
                        raise Exception(f"HTTP error: {str(e)}")
                    time.sleep(2 ** attempt)
                    
            except requests.exceptions.Timeout:
                error_msg = f"Request timed out after {self.config.timeout} seconds"
                if attempt == self.config.max_retries - 1:
                    raise Exception(f"{error_msg}. Try increasing timeout in AI settings or using a faster model.")
                FreeCAD.Console.PrintWarning(f"Attempt {attempt + 1}: {error_msg}. Retrying...\n")
                time.sleep(5)
                
            except requests.exceptions.ConnectionError:
                error_msg = "Could not connect to Ollama"
                if attempt == self.config.max_retries - 1:
                    raise Exception(f"{error_msg}. Make sure Ollama is running: ollama serve")
                FreeCAD.Console.PrintWarning(f"Attempt {attempt + 1}: {error_msg}. Retrying...\n")
                time.sleep(3)
                
            except requests.exceptions.RequestException as e:
                if attempt == self.config.max_retries - 1:
                    raise Exception(f"LLM API call failed after {self.config.max_retries} attempts: {str(e)}")
                time.sleep(2 ** attempt)  # Exponential backoff
        
        raise Exception("Failed to get response from LLM")
    
    def _parse_ai_response(self, response: str) -> Dict[str, Any]:
        """Parse AI response into structured commands"""
        
        # Clean up response - remove markdown code blocks if present
        clean_response = response.strip()
        if clean_response.startswith('```'):
            # Remove opening ```json or ``` 
            lines = clean_response.split('\n')
            if lines[0].startswith('```'):
                lines = lines[1:]
            # Remove closing ```
            if lines and lines[-1].strip() == '```':
                lines = lines[:-1]
            clean_response = '\n'.join(lines)
        
        try:
            # Try to find JSON in the response
            json_match = re.search(r'\{.*\}', clean_response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                parsed = json.loads(json_str)
                
                # Validate required fields
                if "commands" in parsed and isinstance(parsed["commands"], list):
                    return parsed
                    
        except json.JSONDecodeError as e:
            FreeCAD.Console.PrintWarning(f"JSON parse error: {str(e)}\nResponse was: {response[:200]}...\n")
        
        # Fallback: try to parse manually
        return self._fallback_parse(response)
    
    def _fallback_parse(self, response: str) -> Dict[str, Any]:
        """Fallback parser for non-JSON responses"""
        
        commands = []
        
        # Simple pattern matching for basic shapes
        if re.search(r'box|cube|rectangular', response.lower()):
            dimensions = self._extract_dimensions(response)
            commands.append({
                "type": "create",
                "shape": "box",
                "dimensions": dimensions,
                "position": {"x": 0, "y": 0, "z": 0},
                "rotation": {"x": 0, "y": 0, "z": 0},
                "name": "Box"
            })
        
        elif re.search(r'cylinder|tube|pipe', response.lower()):
            dimensions = self._extract_dimensions(response)
            commands.append({
                "type": "create",
                "shape": "cylinder",
                "dimensions": dimensions,
                "position": {"x": 0, "y": 0, "z": 0},
                "rotation": {"x": 0, "y": 0, "z": 0},
                "name": "Cylinder"
            })
        
        elif re.search(r'sphere|ball', response.lower()):
            dimensions = self._extract_dimensions(response)
            commands.append({
                "type": "create",
                "shape": "sphere",
                "dimensions": dimensions,
                "position": {"x": 0, "y": 0, "z": 0},
                "rotation": {"x": 0, "y": 0, "z": 0},
                "name": "Sphere"
            })
        
        return {
            "commands": commands,
            "explanation": "Fallback parsing used",
            "confidence": 0.6,
            "fallback": True
        }
    
    def _extract_dimensions(self, text: str) -> Dict[str, float]:
        """Extract dimensions from text"""
        
        dimensions = {"length": 10, "width": 10, "height": 10}
        
        # Unit conversion to mm
        units = {
            'mm': 1.0, 'cm': 10.0, 'dm': 100.0, 'm': 1000.0,
            'in': 25.4, 'ft': 304.8, '"': 25.4, "'": 304.8
        }
        
        # XxYxZ pattern
        xyz_match = re.search(r'(\d+(?:\.\d+)?)x(\d+(?:\.\d+)?)x(\d+(?:\.\d+)?)\s*([a-z"\']*)', text.lower())
        if xyz_match:
            x, y, z, unit = xyz_match.groups()
            unit_factor = units.get(unit or 'mm', 1.0)
            dimensions = {
                "length": float(x) * unit_factor,
                "width": float(y) * unit_factor,
                "height": float(z) * unit_factor
            }
        
        # Individual dimensions
        patterns = {
            'diameter': r'diameter\s+(\d+(?:\.\d+)?)\s*([a-z"\']*)',
            'radius': r'radius\s+(\d+(?:\.\d+)?)\s*([a-z"\']*)',
            'height': r'height\s+(\d+(?:\.\d+)?)\s*([a-z"\']*)',
            'length': r'length\s+(\d+(?:\.\d+)?)\s*([a-z"\']*)',
            'width': r'width\s+(\d+(?:\.\d+)?)\s*([a-z"\']*)'
        }
        
        for dim_name, pattern in patterns.items():
            match = re.search(pattern, text.lower())
            if match:
                value, unit = match.groups()
                unit_factor = units.get(unit or 'mm', 1.0)
                dimensions[dim_name] = float(value) * unit_factor
        
        return dimensions
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        
    def get_history(self) -> List[Dict]:
        """Get conversation history"""
        return self.conversation_history.copy()
    
    def update_context(self, **kwargs):
        """Update agent context"""
        self.context.update(kwargs)

class AIAgentManager:
    """Manager for AI agents with threading support"""
    
    def __init__(self):
        self.config = AIAgentConfig()
        self.agent = None
        self.is_busy = False
        
    def initialize_agent(self, config: AIAgentConfig = None):
        """Initialize AI agent with configuration"""
        if config:
            self.config = config
        self.agent = AIAgent(self.config)
        
    def process_async(self, prompt: str, callback=None, context: Dict = None):
        """Process prompt asynchronously"""
        if self.is_busy:
            return False
            
        def worker():
            self.is_busy = True
            try:
                result = self.agent.process_prompt(prompt, context)
                if callback:
                    callback(result)
            except Exception as e:
                if callback:
                    callback({"error": str(e)})
            finally:
                self.is_busy = False
        
        thread = threading.Thread(target=worker)
        thread.daemon = True
        thread.start()
        return True
    
    def is_available(self) -> bool:
        """Check if agent is available"""
        return self.agent is not None and not self.is_busy
    
    def test_connection(self) -> bool:
        """Test connection to AI service"""
        try:
            if not self.agent:
                return False
                
            test_response = self.agent._call_llm("You are a test assistant.", "Respond with 'OK'")
            return "ok" in test_response.lower()
        except:
            return False