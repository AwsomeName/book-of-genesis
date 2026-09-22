import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import MagicMock, patch
import urllib.error

from genesis.provider import ProviderError, NoRedirects, provider_status, list_models


class ProviderTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.config = {'base_url': 'https://example.com', 'expires_at': '2099-01-01T00:00:00+00:00',
                       'enabled': True, 'service_eligibility_confirmed': True,
                       'daily_allowance_cny': '80.00', 'api_key': 'fake-secret-should-not-appear'}
        self.save()
        (self.directory / 'credentials.json').write_text(json.dumps({'api_key': 'fake-secret-should-not-appear'}))

    def save(self):
        (self.directory / 'provider.json').write_text(json.dumps(self.config))

    def test_status_does_not_expose_secrets_or_claim_balance(self):
        result = provider_status(self.directory)
        self.assertNotIn('fake-secret', json.dumps(result))
        self.assertIsNone(result['verified_balance'])
        self.assertFalse(result['inference_implemented'])

    def test_expired_and_paused_configs_never_use_network(self):
        with patch('urllib.request.build_opener') as opener:
            self.config['expires_at'] = '2000-01-01T00:00:00+00:00'
            self.save()
            with self.assertRaises(ProviderError):
                list_models(self.directory)
            self.config['expires_at'] = '2099-01-01T00:00:00+00:00'
            self.config['enabled'] = False
            self.save()
            with self.assertRaises(ProviderError):
                list_models(self.directory)
            self.config['enabled'] = True
            self.config['service_eligibility_confirmed'] = False
            self.save()
            with self.assertRaises(ProviderError):
                list_models(self.directory)
            opener.assert_not_called()

    def test_models_are_read_without_inference(self):
        response = MagicMock()
        response.__enter__.return_value.read.return_value = b'{"data":[{"id":"test-model"}]}'
        with patch('urllib.request.build_opener') as factory:
            factory.return_value.open.return_value = response
            result = list_models(self.directory)
            request = factory.return_value.open.call_args.args[0]
        self.assertEqual(request.full_url, 'https://example.com/v1/models')
        self.assertEqual(result['models'], ['test-model'])
        self.assertFalse(result['inference_performed'])

    def test_provider_errors_do_not_echo_credentials(self):
        error = urllib.error.HTTPError('https://example.com', 401, 'fake-secret-should-not-appear', {}, None)
        with patch('urllib.request.build_opener') as factory:
            factory.return_value.open.side_effect = error
            with self.assertRaises(ProviderError) as caught:
                list_models(self.directory)
        self.assertNotIn('fake-secret', str(caught.exception))
        self.assertIn('401', str(caught.exception))

    def test_rejects_insecure_and_credential_bearing_endpoints(self):
        for url in ('http://example.com', 'https://user:password@example.com', 'https://example.com?key=secret'):
            self.config['base_url'] = url
            self.save()
            with self.assertRaises(ProviderError):
                provider_status(self.directory)

    def test_redirects_are_not_followed(self):
        self.assertIsNone(NoRedirects().redirect_request(None, None, 302, '', {}, 'https://elsewhere.example'))
