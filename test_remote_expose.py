from utils.remote_expose import exposeRemote
import requests
import time

def test_remote_expose():
    with exposeRemote('voces/output.wav') as remote_url:
        print(f"File is now accessible at: {remote_url}")
        
        # Give ngrok a moment to set up the tunnel
        time.sleep(120)
        
        # Try to access the file
        try:
            response = requests.get(remote_url)
            if response.status_code == 200:
                print("\nSuccessfully accessed the file! Content:")
                print("-" * 50)
                print(response.text)
                print("-" * 50)
            else:
                print(f"Error accessing file: Status code {response.status_code}")
        except Exception as e:
            print(f"Error accessing file: {e}")

if __name__ == "__main__":
    test_remote_expose()
