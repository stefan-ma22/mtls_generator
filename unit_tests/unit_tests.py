import unittest
import mtls_ssl_generator
from pathlib import Path

class TestMTLSGenerator(unittest.TestCase):
    def test_generate_certificates(self):
        mtls_ssl_generator.ensure_ou_directory_exists(Path("generated_certificates"))
        mtls_ssl_generator.create_ca(Path("generated_certificates/test_ou"), "Test-Root-CA")
        mtls_ssl_generator.create_server(Path("generated_certificates/test_ou"), Path("generated_certificates/test_ou/server"), "test-server")
        mtls_ssl_generator.create_client(Path("generated_certificates/test_ou"), Path("generated_certificates/test_ou/clients/test-client"), "test-client")