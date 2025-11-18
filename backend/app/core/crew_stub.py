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
        top_p: Optional[float] = 1.0,
        top_k: Optional[int] = 50,
        api_key: Optional[str] = None,
        provider: str = 'openai'
    ):
        self.name = name
        self.role = role
        self.goal = goal
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.top_p = top_p
        self.top_k = top_k
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

    def think_stream(self, prompt: str, api_key: Optional[str] = None):
        """Generator that yields response chunks as they arrive."""
        api_key = (api_key or self.api_key or '').strip()
        if not api_key:
            # Simple deterministic stub response used when no API key is provided.
            time.sleep(0.2)
            yield f"[{self.name} - {self.model} | temp={self.temperature}] Echo: {prompt[:100]}"
            return

        provider = (self.provider or 'openai').lower()
        if provider == 'openai':
            yield from self._call_openai_stream(prompt, api_key, OPENAI_CHAT_COMPLETIONS_URL)
        elif provider == 'fireworks':
            yield from self._call_openai_stream(prompt, api_key, FIREWORKS_CHAT_COMPLETIONS_URL)
        elif provider == 'gemini':
            yield from self._call_gemini_stream(prompt, api_key)
        else:
            raise RuntimeError(f'Unsupported provider "{provider}". Please choose OpenAI, Fireworks, or Gemini.')

    def _call_openai(self, prompt: str, api_key: str, base_url: str) -> str:
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        # Ensure max_tokens is always set and valid
        max_tokens = self.max_tokens if self.max_tokens and self.max_tokens > 0 else 1024
        payload = {
            'model': self._normalize_model_name(),
            'messages': [
                {'role': 'system', 'content': self._build_system_prompt()},
                {'role': 'user', 'content': prompt}
            ],
            'temperature': self.temperature,
            'max_tokens': max_tokens
        }
        if self.top_p is not None:
            payload['top_p'] = self.top_p
        if self.top_k is not None:
            payload['top_k'] = self.top_k

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
            choice = data['choices'][0]
            content = choice['message']['content'].strip()
            finish_reason = choice.get('finish_reason', '')
            
            # If response was cut off due to length, try to complete it
            if finish_reason == 'length':
                # Make a follow-up request to complete the response
                completion_payload = payload.copy()
                completion_payload['messages'].append({
                    'role': 'assistant',
                    'content': content
                })
                completion_payload['messages'].append({
                    'role': 'user',
                    'content': 'Please continue and complete your previous response.'
                })
                # Use a smaller token budget for completion (20% of original, min 50, max 500)
                completion_tokens = max(50, min(500, int(max_tokens * 0.2)))
                completion_payload['max_tokens'] = completion_tokens
                
                try:
                    completion_response = requests_client.post(
                        base_url,
                        headers=headers,
                        json=completion_payload,
                        timeout=60
                    )
                    if completion_response.status_code == 200:
                        completion_data = completion_response.json()
                        if 'choices' in completion_data and len(completion_data['choices']) > 0:
                            completion_choice = completion_data['choices'][0]
                            additional_content = completion_choice['message']['content'].strip()
                            content = content + ' ' + additional_content
                            
                            # If completion was also cut off, try one more time (but with smaller budget)
                            if completion_choice.get('finish_reason') == 'length' and completion_tokens > 50:
                                final_completion_payload = completion_payload.copy()
                                final_completion_payload['messages'].append({
                                    'role': 'assistant',
                                    'content': additional_content
                                })
                                final_completion_payload['messages'].append({
                                    'role': 'user',
                                    'content': 'Please finish your response.'
                                })
                                final_completion_tokens = max(50, int(completion_tokens * 0.5))
                                final_completion_payload['max_tokens'] = final_completion_tokens
                                
                                try:
                                    final_response = requests_client.post(
                                        base_url,
                                        headers=headers,
                                        json=final_completion_payload,
                                        timeout=60
                                    )
                                    if final_response.status_code == 200:
                                        final_data = final_response.json()
                                        if 'choices' in final_data and len(final_data['choices']) > 0:
                                            final_content = final_data['choices'][0]['message']['content'].strip()
                                            content = content + ' ' + final_content
                                except Exception:
                                    pass
                except Exception:
                    # If completion fails, return the original content
                    pass
            
            return content
        except (KeyError, IndexError, TypeError):
            raise RuntimeError('Received an unexpected response format from the model API.')

    def _call_openai_stream(self, prompt: str, api_key: str, base_url: str):
        """Stream response from OpenAI/Fireworks API."""
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        # Ensure max_tokens is always set and valid
        max_tokens = self.max_tokens if self.max_tokens and self.max_tokens > 0 else 1024
        payload = {
            'model': self._normalize_model_name(),
            'messages': [
                {'role': 'system', 'content': self._build_system_prompt()},
                {'role': 'user', 'content': prompt}
            ],
            'temperature': self.temperature,
            'max_tokens': max_tokens,
            'stream': True
        }
        if self.top_p is not None:
            payload['top_p'] = self.top_p
        if self.top_k is not None:
            payload['top_k'] = self.top_k

        requests_client = self._get_requests_client()

        try:
            response = requests_client.post(
                base_url,
                headers=headers,
                json=payload,
                stream=True,
                timeout=60
            )
        except requests_client.RequestException as exc:  # type: ignore[attr-defined]
            raise RuntimeError(f'Network error while contacting the model API: {exc}') from exc

        if response.status_code >= 400:
            detail = self._extract_error_message(response)
            raise RuntimeError(f'Model API error ({response.status_code}): {detail}')

        full_content = ''
        try:
            for line in response.iter_lines():
                if not line:
                    continue
                line = line.decode('utf-8')
                if line.startswith('data: '):
                    data_str = line[6:]  # Remove 'data: ' prefix
                    if data_str == '[DONE]':
                        break
                    try:
                        import json
                        data = json.loads(data_str)
                        if 'choices' in data and len(data['choices']) > 0:
                            delta = data['choices'][0].get('delta', {})
                            content = delta.get('content', '')
                            if content:
                                full_content += content
                                yield content
                    except (json.JSONDecodeError, KeyError):
                        continue
        except Exception as exc:
            raise RuntimeError(f'Error processing stream: {exc}') from exc

    def _call_gemini(self, prompt: str, api_key: str) -> str:
        model_name = self._normalize_model_name()
        url = GEMINI_GENERATE_URL_TEMPLATE.format(model=model_name)
        # Ensure max_tokens is always set and valid
        max_tokens = self.max_tokens if self.max_tokens and self.max_tokens > 0 else 1024
        payload = {
            'contents': [
                {
                    'role': 'user',
                    'parts': [{'text': prompt}]
                }
            ],
            'generationConfig': {
                'temperature': self.temperature,
                'maxOutputTokens': max_tokens
            }
        }
        if self.top_p is not None:
            payload['generationConfig']['top_p'] = self.top_p
        if self.top_k is not None:
            payload['generationConfig']['top_k'] = self.top_k

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
            content = parts[0]['text'].strip()
            finish_reason = first_candidate.get('finishReason', '')
            
            # If response was cut off, try to complete it
            if finish_reason == 'MAX_TOKENS':
                # Make a follow-up request to complete the response
                completion_payload = payload.copy()
                completion_payload['contents'].append({
                    'role': 'model',
                    'parts': [{'text': content}]
                })
                completion_payload['contents'].append({
                    'role': 'user',
                    'parts': [{'text': 'Please continue and complete your previous response.'}]
                })
                # Use a smaller token budget for completion (20% of original, min 50, max 500)
                completion_tokens = max(50, min(500, int(max_tokens * 0.2)))
                completion_payload['generationConfig']['maxOutputTokens'] = completion_tokens
                
                try:
                    completion_response = requests_client.post(
                        url,
                        params={'key': api_key},
                        json=completion_payload,
                        timeout=60
                    )
                    if completion_response.status_code == 200:
                        completion_data = completion_response.json()
                        if 'candidates' in completion_data and len(completion_data['candidates']) > 0:
                            completion_candidate = completion_data['candidates'][0]
                            additional_parts = completion_candidate['content']['parts']
                            if additional_parts and len(additional_parts) > 0:
                                additional_content = additional_parts[0]['text'].strip()
                                content = content + ' ' + additional_content
                                
                                # If completion was also cut off, try one more time (but with smaller budget)
                                if completion_candidate.get('finishReason') == 'MAX_TOKENS' and completion_tokens > 50:
                                    final_completion_payload = completion_payload.copy()
                                    final_completion_payload['contents'].append({
                                        'role': 'model',
                                        'parts': [{'text': additional_content}]
                                    })
                                    final_completion_payload['contents'].append({
                                        'role': 'user',
                                        'parts': [{'text': 'Please finish your response.'}]
                                    })
                                    final_completion_tokens = max(50, int(completion_tokens * 0.5))
                                    final_completion_payload['generationConfig']['maxOutputTokens'] = final_completion_tokens
                                    
                                    try:
                                        final_response = requests_client.post(
                                            url,
                                            params={'key': api_key},
                                            json=final_completion_payload,
                                            timeout=60
                                        )
                                        if final_response.status_code == 200:
                                            final_data = final_response.json()
                                            if 'candidates' in final_data and len(final_data['candidates']) > 0:
                                                final_parts = final_data['candidates'][0]['content']['parts']
                                                if final_parts and len(final_parts) > 0:
                                                    final_content = final_parts[0]['text'].strip()
                                                    content = content + ' ' + final_content
                                    except Exception:
                                        pass
                except Exception:
                    # If completion fails, return the original content
                    pass
            
            return content
        except (KeyError, IndexError, TypeError):
            raise RuntimeError('Received an unexpected response format from the Gemini API.')

    def _call_gemini_stream(self, prompt: str, api_key: str):
        """Stream response from Gemini API."""
        model_name = self._normalize_model_name()
        url = GEMINI_GENERATE_URL_TEMPLATE.format(model=model_name)
        # Ensure max_tokens is always set and valid
        max_tokens = self.max_tokens if self.max_tokens and self.max_tokens > 0 else 1024
        payload = {
            'contents': [
                {
                    'role': 'user',
                    'parts': [{'text': prompt}]
                }
            ],
            'generationConfig': {
                'temperature': self.temperature,
                'maxOutputTokens': max_tokens
            }
        }
        if self.top_p is not None:
            payload['generationConfig']['top_p'] = self.top_p
        if self.top_k is not None:
            payload['generationConfig']['top_k'] = self.top_k

        requests_client = self._get_requests_client()

        try:
            # Note: Gemini API doesn't support streaming in the same way as OpenAI
            # We'll simulate streaming by making the request and yielding chunks
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
            content = parts[0]['text'].strip()
            
            # Simulate streaming by yielding chunks (Gemini doesn't support true streaming)
            chunk_size = 20  # Characters per chunk
            for i in range(0, len(content), chunk_size):
                chunk = content[i:i + chunk_size]
                yield chunk
                time.sleep(0.01)  # Small delay to simulate streaming
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

