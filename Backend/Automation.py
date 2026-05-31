"""
Automation.py — System and application automation handler for Nexon AI.
Handles 'open', 'close', 'play', 'system', 'google search', 'youtube search' tasks.
"""

import os
import asyncio
import webbrowser
from urllib.parse import quote_plus
from AppOpener import open as open_app, close as close_app
import keyboard
import time
import pywhatkit

async def Automation(commands: list[str]):
    """
    Process a list of DMM automation commands.
    """
    for cmd in commands:
        try:
            if cmd.startswith("open "):
                target = cmd.replace("open ", "").strip()
                # Use webbrowser for known web platforms, AppOpener for desktop apps
                if target in ["google", "chrome"]:
                    webbrowser.open("https://www.google.com")
                elif target in ["youtube"]:
                    webbrowser.open("https://www.youtube.com")
                elif target in ["facebook", "instagram", "whatsapp"]:
                    webbrowser.open(f"https://{target}.com")
                else:
                    open_app(target, match_closest=True)

            elif cmd.startswith("close "):
                target = cmd.replace("close ", "").strip()
                close_app(target, match_closest=True)

            elif cmd.startswith("play "):
                song = cmd.replace("play ", "").strip()

                print(f"[PLAY REQUEST] {song}")

                pywhatkit.playonyt(song)

            elif cmd.startswith("google search "):
                query = cmd.replace("google search ", "").strip()
                webbrowser.open(f"https://www.google.com/search?q={quote_plus(query)}")

            elif cmd.startswith("youtube search "):
                query = cmd.replace("youtube search ", "").strip()
                webbrowser.open(f"https://www.youtube.com/results?search_query={quote_plus(query)}")

            elif cmd.startswith("system "):
                task = cmd.replace("system ", "").strip()
                if "volume up" in task or "increase volume" in task:
                    for _ in range(5): keyboard.press_and_release("volume up")
                elif "volume down" in task or "decrease volume" in task:
                    for _ in range(5): keyboard.press_and_release("volume down")
                elif "mute" in task or "unmute" in task:
                    keyboard.press_and_release("volume mute")
                elif "pause" in task or "play" in task:
                    keyboard.press_and_release("play/pause media")
                    
        except Exception as e:
            print(f"[Automation Error] Failed to execute '{cmd}': {e}")
            raise e
