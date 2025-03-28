import time
import logging

def process_text_with_ai(input_text, retries=3, backoff_factor=2):
    for attempt in range(retries):
        try:
            chat_session = model.start_chat(history=[])
            response = chat_session.send_message(input_text)
            return response.text
        except Exception as e:
            logging.error(f"Error processing text with AI: {e}")
            if "429" in str(e):
                wait_time = backoff_factor ** attempt
                logging.info(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                break
    return ""