from yandex_music import Client
import config

def main():
    print("Yandex Music CLI Authentication")
    print("-------------------------------")
    
    client = Client()
    
    def on_code(code):
        print(f"\nGo to: {code.verification_url}")
        print(f"And enter the code: {code.user_code}")
        print("\nWaiting for you to authorize...")

    try:
        token = client.device_auth(on_code=on_code)
        config.set_token(token.access_token)
        print("\nSuccess! Token saved to config.")
        print("You can now run 'python main.py'")
    except Exception as e:
        print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    main()
