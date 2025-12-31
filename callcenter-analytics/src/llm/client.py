"""
LLM Client Module
Handles communication with various LLM providers
"""

import os
from typing import Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()


class LLMClient:
    """Client for interacting with LLM APIs"""

    def __init__(self, config: dict):
        self.config = config
        llm_config = config.get('llm', {})

        self.provider = llm_config.get('provider', 'openai')
        self.model = llm_config.get('model', 'gpt-4')
        self.temperature = llm_config.get('temperature', 0.7)
        self.max_tokens = llm_config.get('max_tokens', 2000)

        # Get API key from environment
        api_key_env = llm_config.get('api_key_env', 'OPENAI_API_KEY')
        self.api_key = os.getenv(api_key_env)

        # Initialize client
        self.client = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize the appropriate LLM client based on provider"""
        if self.provider == 'openai':
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=self.api_key)
                print(f"✓ Initialized OpenAI client with model: {self.model}")
            except ImportError:
                raise ImportError("OpenAI package not installed. Run: pip install openai")

        elif self.provider == 'anthropic':
            try:
                from anthropic import Anthropic
                self.client = Anthropic(api_key=self.api_key)
                print(f"✓ Initialized Anthropic client with model: {self.model}")
            except ImportError:
                raise ImportError("Anthropic package not installed. Run: pip install anthropic")

        elif self.provider == 'ollama':
            try:
                import requests
                base_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
                self.client = {'base_url': base_url, 'model': self.model}
                print(f"✓ Initialized Ollama client with model: {self.model}")
            except Exception as e:
                raise Exception(f"Error initializing Ollama: {str(e)}")

        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Generate text using LLM

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt

        Returns:
            Generated text
        """
        if not self.client:
            raise Exception("LLM client not initialized")

        try:
            if self.provider == 'openai':
                return self._generate_openai(prompt, system_prompt)
            elif self.provider == 'anthropic':
                return self._generate_anthropic(prompt, system_prompt)
            elif self.provider == 'ollama':
                return self._generate_ollama(prompt, system_prompt)
        except Exception as e:
            raise Exception(f"Error generating text: {str(e)}")

    def _generate_openai(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate using OpenAI API"""
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )

        return response.choices[0].message.content

    def _generate_anthropic(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate using Anthropic API"""
        kwargs = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "messages": [{"role": "user", "content": prompt}]
        }

        if system_prompt:
            kwargs["system"] = system_prompt

        response = self.client.messages.create(**kwargs)
        return response.content[0].text

    def _generate_ollama(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate using Ollama local API"""
        import requests

        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"

        payload = {
            "model": self.client['model'],
            "prompt": full_prompt,
            "stream": False,
            "options": {
                "temperature": self.temperature,
                "num_predict": self.max_tokens
            }
        }

        response = requests.post(
            f"{self.client['base_url']}/api/generate",
            json=payload
        )
        response.raise_for_status()

        return response.json()['response']

    def generate_structured(self, prompt: str, system_prompt: Optional[str] = None,
                           schema: Optional[Dict] = None) -> Dict:
        """
        Generate structured output (JSON)

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            schema: Optional JSON schema for output

        Returns:
            Parsed JSON response
        """
        import json

        # Add instruction to output JSON
        structured_prompt = f"{prompt}\n\nPlease provide your response in valid JSON format."

        if schema:
            structured_prompt += f"\n\nFollow this schema:\n{json.dumps(schema, indent=2)}"

        response_text = self.generate(structured_prompt, system_prompt)

        # Try to extract JSON from response
        try:
            # Find JSON in response (handle markdown code blocks)
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                json_text = response_text[json_start:json_end].strip()
            else:
                json_text = response_text

            return json.loads(json_text)

        except json.JSONDecodeError as e:
            print(f"⚠ Warning: Could not parse JSON response: {str(e)}")
            return {"raw_response": response_text}

    def batch_generate(self, prompts: List[str], system_prompt: Optional[str] = None) -> List[str]:
        """
        Generate responses for multiple prompts

        Args:
            prompts: List of prompts
            system_prompt: Optional system prompt for all

        Returns:
            List of generated responses
        """
        responses = []
        total = len(prompts)

        for i, prompt in enumerate(prompts, 1):
            print(f"  Processing {i}/{total}...")
            response = self.generate(prompt, system_prompt)
            responses.append(response)

        return responses
