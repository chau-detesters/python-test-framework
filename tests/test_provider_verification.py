import pytest
import subprocess
import time
import threading
from pact import Verifier
import uvicorn
from provider.service import app

class TestProviderVerification:
    """Provider verification tests"""
    
    @classmethod
    def setup_class(cls):
        """Start the provider service"""
        def run_server():
            uvicorn.run(app, host="127.0.0.1", port=3000, log_level="error")
        
        cls.server_thread = threading.Thread(target=run_server, daemon=True)
        cls.server_thread.start()
        time.sleep(2)  # Give server time to start
    
    def test_verify_pacts(self):
        """Verify that the provider satisfies all consumer contracts"""
        verifier = Verifier(
            provider='UserAPI',
            provider_base_url='http://127.0.0.1:3000',
        )
        pact_file = 'pacts/get_user_success.json/UserService-UserAPI.json'
        output, logs = verifier.verify_pacts(
            pact_file,
            verbose=True,
            provider_states_setup_url='http://127.0.0.1:3000/_pact/provider_states'
        )
        assert output == 0, f"Pact verification failed: {logs}" 