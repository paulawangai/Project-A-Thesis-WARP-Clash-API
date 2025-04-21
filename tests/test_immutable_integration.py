import unittest
import sys
import os
import copy
import logging
from unittest.mock import MagicMock, patch

# Add the project root to Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

# Import the immutable decorator
from fp_decorators.immutable import immutable

# Import modules to test
from services.subscription import generateSingBoxSubFile, generateShadowRocketSubFile, generateLoonSubFile, generateSurgeSubFile

class TestImmutableIntegration(unittest.TestCase):
    
    def setUp(self):
        # Set up common mocks and test data
        self.logger = logging.getLogger("test")
        
        # Mock Account object
        self.mock_account = MagicMock()
        self.mock_account.private_key = "test_private_key"
        
        # Mock Entrypoint objects
        self.mock_entrypoint = MagicMock()
        self.mock_entrypoint.ip = "1.1.1.1"
        self.mock_entrypoint.port = 8080
        self.mock_entrypoint.loss = 0.1
        self.mock_entrypoint.delay = 100
        
        # Create a list of mock entrypoints
        self.mock_entrypoints = [self.mock_entrypoint for _ in range(3)]
    
    @patch('services.subscription.getRandomEntryPoints')
    @patch('services.subscription.getCurrentAccount')
    @patch('services.subscription.SING_BOX')
    @patch('services.subscription.NodeNameGenerator')
    @patch('services.subscription.GEOIP')
    @patch('services.subscription.CF_CONFIG')
    @patch('services.subscription.json')
    def test_generateSingBoxSubFile_immutable(self, mock_json, mock_cf_config, mock_geoip, 
                                              mock_node_name_gen, mock_sing_box, 
                                              mock_getCurrentAccount, mock_getRandomEntryPoints):
        """Test that generateSingBoxSubFile works with the immutable decorator."""
        # Set up mocks
        mock_getCurrentAccount.return_value = self.mock_account
        mock_getRandomEntryPoints.return_value = (self.mock_entrypoints, "")
        mock_node_name_gen.return_value.next.return_value = "test_node"
        mock_geoip.lookup.return_value = "US"
        mock_geoip.lookup_emoji.return_value = "🇺🇸"
        mock_cf_config.get.return_value = "test_public_key"
        
        # Mock SING_BOX as a dictionary with the structure needed
        mock_sing_box_value = {
            "outbounds": [
                {"outbounds": []},  # Section Select
                {"outbounds": []}   # Section UrlTest
            ]
        }
        mock_sing_box.__getitem__.side_effect = mock_sing_box_value.__getitem__
        mock_sing_box.copy.return_value = copy.deepcopy(mock_sing_box_value)
        
        # Mock json.dumps to return predictable output
        mock_json.dumps.return_value = "json_content"
        
        # Apply decorator to the function
        original_function = generateSingBoxSubFile
        decorated_function = immutable(original_function)
        
        # Test the function
        result = decorated_function(
            account=self.mock_account,
            logger=self.logger,
            random_name=False,
            best=False,
            ipv6=False
        )
        
        # Check that the function returned the expected result
        self.assertEqual(result, "json_content")
        
        # Check that getCurrentAccount was not called since we provided an account
        mock_getCurrentAccount.assert_not_called()
        
        # Check that getRandomEntryPoints was called with the right parameters
        mock_getRandomEntryPoints.assert_called_with(best=False, logger=self.logger, ipv6=False)
    
if __name__ == '__main__':
    unittest.main()