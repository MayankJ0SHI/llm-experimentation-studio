import os
import json
import google.generativeai as genai
from openai import OpenAI

class LLM_Provider:
    def __init__(self,config:dict):
        self.providerName = config['provider']
        self.model = config['models'][self.providerName]
        
        if self.providerName == 'openai':
            key = os.getenv('OPENAI_API_KEY')
            if not key:
                raise ValueError(f"OPENAI API KEY environment variable was not set.")
            self.client = OpenAI(api_key=key)
        elif self.providerName == 'gemini':
            key = os.getenv('GEMINI_API_KEY')
            if not key:
                raise ValueError(f"GEMINI API KEY environment variable was not set.")
            genai.configure(api_key=key)
            self.client = genai.GenerativeModel(self.model)
        else:
            raise ValueError(f"Please provide the valid LLM Provider name")
        print(f"{self.providerName.title()} initialized with model {self.model}")
    
    def chat(self, history: list, temperature: float, max_tokens: int) -> str:
        if not (0 <= temperature <= 1):
            raise ValueError("Temperature must be between 0 and 1")

        if max_tokens <= 0:
            raise ValueError("Max tokens must be > 0")

        try:
            # ---------------- OPENAI ---------------- #
            if self.providerName == 'openai':
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=history,  # ✅ directly pass history
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                return response.choices[0].message.content.strip()

            # ---------------- GEMINI ---------------- #
            elif self.providerName == 'gemini':
                # Convert history to text
                conversation_text = "\n".join(
                    f"{m['role']}: {m['content']}" for m in history
                )

                response = self.client.generate_content(
                    conversation_text,
                    generation_config={
                        'max_output_tokens': max_tokens,
                        'temperature': temperature
                    }
                )
                return response.text.strip()

        except Exception as e:
            print(f"Error in {self.providerName}: {str(e)}")
            raise
    
    def compare_outputs(self, prompt: str, temperatures: list, max_tokens: int):
        results = []

        for temp in temperatures:
            history = [{"role": "user", "content": prompt}]  # create fresh history
            output = self.chat(history, temp, max_tokens)

            results.append({
                "temperature": temp,
                "output": output
            })

        return results
        
    