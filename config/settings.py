import os
from dotenv import load_dotenv

# Load environment variables from the .env file in the project root
load_dotenv()

# Get the OpenAI API key from the environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("No OpenAI API key found. Please set the OPENAI_API_KEY in your .env file.")