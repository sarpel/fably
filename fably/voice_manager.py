"""
Voice Management System

This module provides voice management capabilities including voice selection,
cycling, categorization, and persistence for the Fably storytelling system.
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from fably import utils
from fably.tts_service import tts_service


class VoiceManager:
    """Manages voice selection, cycling, and categorization."""
    
    def __init__(self, config_path: Path = None):
        self.config_path = config_path or utils.resolve("voice_config.json")
        self.current_voice = "nova"
        self.current_provider = "openai"
        self.voice_history = []
        self.favorites = []
        self.voice_categories = {
            "child_friendly": [],
            "character_voices": [],
            "narrator_voices": [],
            "educational": [],
            "dramatic": []
        }
        self._load_config()
    
    def _load_config(self):
        """Load voice configuration from file."""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.current_voice = config.get("current_voice", "nova")
                    self.current_provider = config.get("current_provider", "openai")
                    self.voice_history = config.get("voice_history", [])
                    self.favorites = config.get("favorites", [])
                    self.voice_categories = config.get("voice_categories", self.voice_categories)
                logging.debug(f"Loaded voice config from {self.config_path}")
            except Exception as e:
                logging.warning(f"Failed to load voice config: {str(e)}")
    
    def _save_config(self):
        """Save voice configuration to file."""
        try:
            config = {
                "current_voice": self.current_voice,
                "current_provider": self.current_provider,
                "voice_history": self.voice_history[-50:],  # Keep last 50
                "favorites": self.favorites,
                "voice_categories": self.voice_categories
            }
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
            logging.debug(f"Saved voice config to {self.config_path}")
        except Exception as e:
            logging.error(f"Failed to save voice config: {str(e)}")
    
    def set_voice(self, voice: str, provider: str = None):
        """Set the current voice and provider."""
        if provider is None:
            provider = self.current_provider
        
        # Add to history if it's a new selection
        voice_key = f"{provider}:{voice}"
        if voice_key not in self.voice_history:
            self.voice_history.append(voice_key)
        
        self.current_voice = voice
        self.current_provider = provider
        self._save_config()
        
        logging.info(f"Voice set to {voice} ({provider})")
    
    def get_current_voice(self) -> Tuple[str, str]:
        """Get the current voice and provider."""
        return self.current_voice, self.current_provider
    
    async def cycle_voice(self, direction: int = 1, category: str = None) -> Tuple[str, str]:
        """
        Cycle through available voices.
        
        Args:
            direction: 1 for next, -1 for previous
            category: Optional category to cycle within
            
        Returns:
            Tuple of (voice, provider)
        """
        all_voices = await tts_service.get_all_voices()
        
        # Flatten voices from all providers
        voice_list = []
        for provider_name, voices in all_voices.items():
            for voice in voices:
                voice_list.append((voice["id"], provider_name, voice))
        
        if not voice_list:
            logging.warning("No voices available for cycling")
            return self.current_voice, self.current_provider
        
        # Filter by category if specified
        if category and category in self.voice_categories:
            category_voices = self.voice_categories[category]
            filtered_list = []
            for voice_id, provider, voice_data in voice_list:
                voice_key = f"{provider}:{voice_id}"
                if voice_key in category_voices:
                    filtered_list.append((voice_id, provider, voice_data))
            voice_list = filtered_list if filtered_list else voice_list
        
        # Find current voice index
        current_key = f"{self.current_provider}:{self.current_voice}"
        current_index = 0
        
        for i, (voice_id, provider, _) in enumerate(voice_list):
            if f"{provider}:{voice_id}" == current_key:
                current_index = i
                break
        
        # Calculate next index
        next_index = (current_index + direction) % len(voice_list)
        next_voice, next_provider, _ = voice_list[next_index]
        
        # Set new voice
        self.set_voice(next_voice, next_provider)
        
        return next_voice, next_provider
    
    async def get_voice_info(self, voice: str = None, provider: str = None) -> Dict:
        """Get detailed information about a voice."""
        voice = voice or self.current_voice
        provider = provider or self.current_provider
        
        try:
            voices = await tts_service.get_voices_by_provider(provider)
            for voice_data in voices:
                if voice_data["id"] == voice:
                    return voice_data
        except Exception as e:
            logging.error(f"Failed to get voice info: {str(e)}")
        
        return {"id": voice, "name": voice, "provider": provider}
    
    async def get_recommended_voices(self, use_case: str = "storytelling") -> List[Dict]:
        """Get recommended voices for a specific use case."""
        all_voices = await tts_service.get_all_voices()
        recommended = []
        
        # Define recommendations based on use case
        if use_case == "storytelling":
            # Look for clear, expressive voices suitable for children
            preferred_voices = [
                "openai:nova",     # Clear female voice
                "openai:alloy",    # Neutral voice
                "openai:fable",    # Expressive female voice
            ]
        elif use_case == "educational":
            preferred_voices = [
                "openai:echo",     # Clear male voice
                "openai:nova",     # Clear female voice
            ]
        else:
            # Default recommendations
            preferred_voices = [
                "openai:nova",
                "openai:alloy",
            ]
        
        # Add preferred voices that are available
        for provider_name, voices in all_voices.items():
            for voice in voices:
                voice_key = f"{provider_name}:{voice['id']}"
                if voice_key in preferred_voices:
                    recommended.append({
                        **voice,
                        "recommendation_reason": f"Excellent for {use_case}"
                    })
        
        # Add other high-quality voices
        for provider_name, voices in all_voices.items():
            for voice in voices:
                if len(recommended) >= 10:  # Limit recommendations
                    break
                
                voice_key = f"{provider_name}:{voice['id']}"
                if voice_key not in [r[f"{r['provider']}:{r['id']}"] for r in recommended]:
                    if provider_name == "elevenlabs":
                        # ElevenLabs voices are generally high quality
                        recommended.append({
                            **voice,
                            "recommendation_reason": "High-quality AI voice"
                        })
        
        return recommended[:10]  # Return top 10 recommendations
    
    def add_to_favorites(self, voice: str, provider: str = None):
        """Add a voice to favorites."""
        provider = provider or self.current_provider
        voice_key = f"{provider}:{voice}"
        
        if voice_key not in self.favorites:
            self.favorites.append(voice_key)
            self._save_config()
            logging.info(f"Added {voice_key} to favorites")
    
    def remove_from_favorites(self, voice: str, provider: str = None):
        """Remove a voice from favorites."""
        provider = provider or self.current_provider
        voice_key = f"{provider}:{voice}"
        
        if voice_key in self.favorites:
            self.favorites.remove(voice_key)
            self._save_config()
            logging.info(f"Removed {voice_key} from favorites")
    
    async def get_favorite_voices(self) -> List[Dict]:
        """Get detailed information about favorite voices."""
        favorites_info = []
        all_voices = await tts_service.get_all_voices()
        
        for favorite in self.favorites:
            provider, voice_id = favorite.split(":", 1)
            if provider in all_voices:
                for voice in all_voices[provider]:
                    if voice["id"] == voice_id:
                        favorites_info.append({
                            **voice,
                            "is_favorite": True
                        })
                        break
        
        return favorites_info
    
    def categorize_voice(self, voice: str, provider: str, category: str):
        """Add a voice to a category."""
        if category not in self.voice_categories:
            self.voice_categories[category] = []
        
        voice_key = f"{provider}:{voice}"
        if voice_key not in self.voice_categories[category]:
            self.voice_categories[category].append(voice_key)
            self._save_config()
            logging.info(f"Added {voice_key} to category {category}")
    
    def get_category_voices(self, category: str) -> List[str]:
        """Get voices in a specific category."""
        return self.voice_categories.get(category, [])
    
    async def preview_voice(self, voice: str, provider: str = None, 
                           preview_text: str = None) -> Path:
        """
        Generate a preview audio sample for a voice.
        
        Args:
            voice: Voice ID
            provider: Provider name
            preview_text: Text to synthesize for preview
            
        Returns:
            Path to preview audio file
        """
        provider = provider or self.current_provider
        preview_text = preview_text or "Hello! This is a preview of my voice. I'm excited to tell you wonderful stories!"
        
        # Create preview directory
        preview_dir = utils.resolve("voice_previews")
        preview_file = preview_dir / f"preview_{provider}_{voice}.mp3"
        
        try:
            await tts_service.synthesize(
                text=preview_text,
                voice=voice,
                provider=provider,
                output_file=preview_file
            )
            
            logging.info(f"Generated voice preview: {preview_file}")
            return preview_file
            
        except Exception as e:
            logging.error(f"Failed to generate voice preview: {str(e)}")
            raise


# Global voice manager instance
voice_manager = VoiceManager()


async def get_current_voice() -> Tuple[str, str]:
    """Get the current voice and provider."""
    return voice_manager.get_current_voice()


def set_current_voice(voice: str, provider: str = None):
    """Set the current voice."""
    voice_manager.set_voice(voice, provider)


async def cycle_to_next_voice(category: str = None) -> Tuple[str, str]:
    """Cycle to the next voice."""
    return await voice_manager.cycle_voice(1, category)


async def cycle_to_previous_voice(category: str = None) -> Tuple[str, str]:
    """Cycle to the previous voice."""
    return await voice_manager.cycle_voice(-1, category)


async def get_voice_recommendations(use_case: str = "storytelling") -> List[Dict]:
    """Get voice recommendations for a use case."""
    return await voice_manager.get_recommended_voices(use_case)


async def preview_voice_sample(voice: str, provider: str = None) -> Path:
    """Generate a voice preview sample."""
    return await voice_manager.preview_voice(voice, provider)
