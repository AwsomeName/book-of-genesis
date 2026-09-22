"""Read-only online provider discovery; secrets never enter output or snapshots."""
from datetime import datetime, timezone
import json
from pathlib import Path
import urllib.error
import urllib.parse
import urllib.request


class ProviderError(ValueError):
    """A sanitized provider error safe to display."""


class NoRedirects(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        # A bearer credential is scoped to the configured endpoint only.
        return None


def load_config(directory: Path):
    try:
        data = json.loads((directory / 'provider.json').read_text(encoding='utf-8'))
    except (OSError, ValueError):
        raise ProviderError('Provider config missing or invalid; see config/provider.example.json.') from None
    if not isinstance(data, dict):
        raise ProviderError('Provider config must be an object.')
    url = data.get('base_url')
    if not isinstance(url, str):
        raise ProviderError('Provider base_url is required.')
    parsed = urllib.parse.urlsplit(url)
    if (parsed.scheme != 'https' or not parsed.hostname or parsed.username
            or parsed.password or parsed.query or parsed.fragment):
        raise ProviderError('Provider URL must use HTTPS without credentials, query or fragment.')
    try:
        expiry = datetime.fromisoformat(data['expires_at'])
        if expiry.tzinfo is None:
            raise ValueError()
    except (KeyError, TypeError, ValueError):
        raise ProviderError('Provider expires_at must be an ISO timestamp with timezone.') from None
    return data, expiry


def provider_status(directory: Path):
    config, expiry = load_config(directory)
    # Explicit field selection prevents leaking secrets or unknown config entries.
    return {
        'base_url': config['base_url'],
        'model': config.get('model'),
        'enabled': config.get('enabled') is True,
        'service_eligibility_confirmed': config.get('service_eligibility_confirmed') is True,
        'credential_file_present': (directory / 'credentials.json').is_file(),
        'expires_at': expiry.isoformat(),
        'expired': datetime.now(timezone.utc) >= expiry,
        'expiry_source': config.get('expiry_source'),
        'daily_allowance_cny': config.get('daily_allowance_cny'),
        'allowance_source': config.get('allowance_source'),
        'billing_timezone': config.get('billing_timezone'),
        'daily_reset_verified': config.get('daily_reset_verified', False),
        'spending_enforcement': config.get('spending_enforcement', 'not_implemented'),
        'verified_balance': None,
        'inference_implemented': False,
    }


def list_models(directory: Path):
    config, expiry = load_config(directory)
    if datetime.now(timezone.utc) >= expiry:
        raise ProviderError('Local credential validity period has expired; no request sent.')
    if config.get('enabled') is not True or config.get('service_eligibility_confirmed') is not True:
        raise ProviderError('Provider is paused pending service eligibility confirmation; no request sent.')
    try:
        key = json.loads((directory / 'credentials.json').read_text(encoding='utf-8'))['api_key']
        if not isinstance(key, str) or not key.strip() or '\n' in key or '\r' in key:
            raise ValueError()
    except (OSError, ValueError, KeyError, TypeError):
        raise ProviderError('Local API credential is missing or invalid.') from None
    base = config['base_url'].rstrip('/')
    url = base + ('/models' if base.endswith('/v1') else '/v1/models')
    request = urllib.request.Request(url, headers={
        'Authorization': 'Bearer ' + key,
        'User-Agent': 'BookOfGenesis/0.2',
    })
    try:
        with urllib.request.build_opener(NoRedirects()).open(request, timeout=30) as response:
            payload = response.read(2_000_001)
            if len(payload) > 2_000_000:
                raise ProviderError('Provider response exceeded size limit.')
            data = json.loads(payload)
        if not isinstance(data, dict) or not isinstance(data.get('data'), list):
            raise ProviderError('Provider returned an unsupported model list.')
        models = [row['id'] for row in data['data']
                  if isinstance(row, dict) and isinstance(row.get('id'), str)]
        # Provider strings are untrusted and must not be treated as instructions.
        if any(key in model for model in models):
            raise ProviderError('Provider response contained a credential; output suppressed.')
        return {'models': models, 'source': config['base_url'], 'inference_performed': False}
    except urllib.error.HTTPError as error:
        # Do not log response bodies, request headers or arbitrary provider messages.
        raise ProviderError(f'Provider HTTP {error.code}; request was not retried.') from None
    except (urllib.error.URLError, TimeoutError, OSError):
        raise ProviderError('Provider network request failed; request was not retried.') from None
    except (ValueError, TypeError, KeyError) as error:
        if isinstance(error, ProviderError):
            raise
        raise ProviderError('Provider returned invalid JSON or an unsupported response.') from None
