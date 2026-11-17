"""Test NVIDIA NIM with a synthetic message; never save or print the API key."""
import getpass
import json
import os
import argparse
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from local_config import load_local_env


def main():
    load_local_env()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model', default=os.getenv('NVIDIA_MODEL', 'nvidia/nemotron-3.5-lightning-30b-a3b'))
    args = parser.parse_args()
    key = os.getenv('NVIDIA_API_KEY', '').strip()
    if not key:
        key = getpass.getpass('NVIDIA API key (input is hidden): ').strip()
    if not key:
        print('No key entered. Test cancelled.')
        return 1
    model = args.model.strip()
    body = {'model': model, 'messages': [{'role': 'user', 'content': 'Reply with: API is working'}],
            'max_tokens': 256, 'stream': False}
    if model == 'nvidia/nemotron-3.5-lightning-30b-a3b':
        body['chat_template_kwargs'] = {'enable_thinking': False}
    request = Request('https://integrate.api.nvidia.com/v1/chat/completions',
                      data=json.dumps(body).encode(),
                      headers={'Authorization': 'Bearer ' + key, 'Content-Type': 'application/json'})
    print(f'Testing NVIDIA model: {model}')
    try:
        with urlopen(request, timeout=45) as response:
            payload = json.loads(response.read(100000))
        content = payload['choices'][0]['message']['content']
        if not isinstance(content, str) or not content.strip():
            print('NVIDIA responded, but returned no text. Try another model.')
            return 1
        print('Success: NVIDIA returned a model response.')
        # Deliberately do not print arbitrary provider content or error bodies.
        return 0
    except HTTPError as error:
        hints = {401: 'Invalid or expired key.', 403: 'Your account does not have access.',
                 404: 'The model or endpoint is unavailable.',
                 410: 'This model endpoint has been retired. Your key may still be valid. Choose another model with --model MODEL_ID.',
                 429: 'Rate or quota limit reached.'}
        print(f'HTTP {error.code}: {hints.get(error.code, "NVIDIA rejected the request. Try again later or choose another model.")}')
    except (URLError, TimeoutError, OSError):
        print('Could not reach NVIDIA. Check your connection and try again.')
    except (ValueError, KeyError, TypeError, IndexError, AttributeError):
        print('NVIDIA returned an unexpected response. Try another text model.')
    return 1


if __name__ == '__main__':
    raise SystemExit(main())
