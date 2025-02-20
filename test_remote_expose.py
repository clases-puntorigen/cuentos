from utils.remote_expose import exposeRemote
import requests
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_remote_expose():
    # Test 1: Single file exposure
    logger.info("Test 1: Single file exposure")
    with exposeRemote('voces/narrador1.mp3') as remote_url:
        logger.info(f"File is now accessible at: {remote_url}")
        time.sleep(2)  # Give ngrok a moment to set up
        
        try:
            response = requests.get(remote_url)
            logger.info(f"Response status: {response.status_code}")
        except Exception as e:
            logger.error(f"Error accessing file: {e}")
    
    logger.info("Test 1 completed")
    
    # Test 2: Sequential file exposures
    logger.info("Test 2: Sequential file exposures")
    for i in range(3):
        logger.info(f"Iteration {i+1}")
        with exposeRemote('voces/narrador1.mp3') as remote_url:
            logger.info(f"File is now accessible at: {remote_url}")
            time.sleep(1)
    
    logger.info("Test 2 completed")
    logger.info("All tests completed successfully")

if __name__ == "__main__":
    test_remote_expose()
