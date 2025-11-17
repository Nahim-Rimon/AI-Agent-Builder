# This is a lightweight CrewAI-compatible adapter stub.
# Replace with real CrewAI integration by adjusting the Agent class.
import time
from typing import Optional

OPENAI_CHAT_COMPLETIONS_URL = 'https://api.openai.com/v1/chat/completions'
FIREWORKS_CHAT_COMPLETIONS_URL = 'https://api.fireworks.ai/inference/v1/chat/completions'
GEMINI_GENERATE_URL_TEMPLATE = 'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent'


class CrewAgent:
    def __init__(
        self,
        name,
        role: str = '',
        goal: str = '',
        model: str = 'gpt-4-turbo',
        temperature: float = 0.7,
        max_tokens: int = 1024,
        api_key: Optional[str] = None,
        provider: str = 'openai'
    ):
        self.name = name
        self.role = role
        self.goal = goal
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.api_key = api_key
        self.provider = (provider or 'openai').lower()

    def think(self, prompt: str, api_key: Optional[str] = None) -> str:
        api_key = (api_key or self.api_key or '').strip()
        if not api_key:
            # Simple deterministic stub response used when no API key is provided.
            time.sleep(0.2)
            return f"[{self.name} - {self.model} | temp={self.temperature}] Echo: {prompt[:100]}"

        provider = (self.provider or 'openai').lower()
        if provider == 'openai':
            return self._call_openai(prompt, api_key, OPENAI_CHAT_COMPLETIONS_URL)
        if provider == 'fireworks':
            return self._call_openai(prompt, api_key, FIREWORKS_CHAT_COMPLETIONS_URL)
        if provider == 'gemini':
            return self._call_gemini(prompt, api_key)

        raise RuntimeError(f'Unsupported provider "{provider}". Please choose OpenAI, Fireworks, or Gemini.')

    def _call_openai(self, prompt: str, api_key: str, base_url: str) -> str:
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        payload = {
            'model': self._normalize_model_name(),
            'messages': [
                {'role': 'system', 'content': self._build_system_prompt()},
                {'role': 'user', 'content': prompt}
            ],
            'temperature': self.temperature,
            'max_tokens': self.max_tokens
        }

        requests_client = self._get_requests_client()

        try:
            response = requests_client.post(
                base_url,
                headers=headers,
                json=payload,
                timeout=60
            )
        except requests_client.RequestException as exc:  # type: ignore[attr-defined]
            raise RuntimeError(f'Network error while contacting the model API: {exc}') from exc

        if response.status_code >= 400:
            detail = self._extract_error_message(response)
            raise RuntimeError(f'Model API error ({response.status_code}): {detail}')

        data = response.json()
        try:
            return data['choices'][0]['message']['content'].strip()
        except (KeyError, IndexError, TypeError):
            raise RuntimeError('Received an unexpected response format from the model API.')

    def _call_gemini(self, prompt: str, api_key: str) -> str:
        model_name = self._normalize_model_name()
        url = GEMINI_GENERATE_URL_TEMPLATE.format(model=model_name)
        payload = {
            'contents': [
                {
                    'role': 'user',
                    'parts': [{'text': prompt}]
                }
            ],
            'generationConfig': {
                'temperature': self.temperature,
                'maxOutputTokens': self.max_tokens
            }
        }

        requests_client = self._get_requests_client()

        try:
            response = requests_client.post(
                url,
                params={'key': api_key},
                json=payload,
                timeout=60
            )
        except requests_client.RequestException as exc:  # type: ignore[attr-defined]
            raise RuntimeError(f'Network error while contacting the Gemini API: {exc}') from exc

        if response.status_code >= 400:
            detail = self._extract_error_message(response)
            raise RuntimeError(f'Model API error ({response.status_code}): {detail}')

        data = response.json()
        try:
            candidates = data['candidates']
            first_candidate = candidates[0]
            parts = first_candidate['content']['parts']
            return parts[0]['text'].strip()
        except (KeyError, IndexError, TypeError):
            raise RuntimeError('Received an unexpected response format from the Gemini API.')

    def _build_system_prompt(self) -> str:
        role = f"Role: {self.role}\n" if self.role else ''
        goal = f"Goal: {self.goal}\n" if self.goal else ''
        return f"You are agent {self.name}.\n{role}{goal}Respond as helpfully as possible."

    def _normalize_model_name(self) -> str:
        return (self.model or '').strip().replace(' ', '-')

    @staticmethod
    def _get_requests_client():
        try:
            import requests  # type: ignore
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError('The "requests" package is not available in the backend environment.') from exc
        return requests

    @staticmethod
    def _extract_error_message(response) -> str:
        try:
            data = response.json()
        except ValueError:
            return response.text or 'Unknown error'

        if isinstance(data, dict):
            if 'error' in data:
                error = data['error']
                if isinstance(error, dict):
                    return error.get('message') or error.get('status') or response.text
                return str(error)
        return response.text or 'Unknown error'

