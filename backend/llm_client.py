from openai import OpenAI
from typing import List
from config import settings
from prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE


class LLMClient:
    """
    Client for interacting with OpenAI's models
    Generates answers based on retrieved context
    """
    
    def __init__(self):
        """Initialize the OpenAI client."""
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.LLM_MODEL
    
    def generate_answer(
        self,
        query: str,
        context_chunks: List[str],
        max_tokens: int = 500
    )-> str:
        """
          Generate an answer using retrieved context.
    
          Args:
              query: The user's question
              context_chunks: List of relevant text chunks from vector store
              max_tokens: Maximum length of the response (default: 500)
        
           Returns:
        The generated answer as a string
        """
        #Takes the list of chunks,joins them into one big strent with double lines between each(gpt needs a string not a list)
        context = "\n\n".join(context_chunks)
        
        # Create the user prompt using template
        user_prompt = USER_PROMPT_TEMPLATE.format(context=context, query=query)
        
        try:
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.7,
                frequency_penalty=0.3  # Reduce repetition
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error generating answer: {e}")
            return "I encountered an error while generating the answer,try asking again."
