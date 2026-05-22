from dotenv import load_dotenv
import anthropic

load_dotenv()

anthropic_client: anthropic.AsyncAnthropic = anthropic.AsyncAnthropic()
