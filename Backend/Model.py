"""
Model.py — Query Decision-Making Model (DMM) using Gemini.

MIGRATION NOTE:
  Previously used Cohere (command-r-plus-08-2024).
  Now uses Gemini via the centralized AIService layer.
  
Purpose:
  Classifies each user query into one or more action categories:
  general, realtime, open, close, play, generate image, system, etc.

Public API (unchanged):
  FirstLayerDMM(prompt) — returns list of action strings
"""

from Backend.AIService import classify_query


def FirstLayerDMM(prompt: str = "test") -> list[str]:
    """
    Classify a user query into action labels.
    
    Returns a list like:
      ['general what is python?']
      ['open chrome', 'general tell me about AI']
      ['generate image a cat on the moon']
      ['exit']
    
    Falls back to ['general <prompt>'] on any error.
    """
    return classify_query(prompt)


if __name__ == "__main__":
    from rich import print
    print("[bold cyan]Nexon AI — Decision Making Model (Gemini)[/bold cyan]")
    print("Type a query to see how it's classified. Type 'exit' to quit.\n")
    while True:
        user_input = input(">>>> ").strip()
        if user_input.lower() in ("exit", "quit"):
            break
        if user_input:
            output = FirstLayerDMM(user_input)
            print(f"[bold green]Detected Actions:[/bold green] {output}")
