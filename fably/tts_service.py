"""
TTS Service Abstraction Layer

This module provides a unified interface for multiple Text-to-Speech providers,
including ElevenLabs (and Gemini placeholder). It allows seamless switching between providers
while maintaining consistent functionality.
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import requests
import soundfile as sf


class TTSProvider(ABC):
    """Abstract base class for TTS providers."""
    
    @abstractmethod
    async def synthesize(self, text: str, voice: str, **kwargs) -> bytes:
        """Synthesize speech from text and return audio data."""
        pass
    
    @abstractmethod
    async def get_available_voices(self) -> List[Dict[str, str]]:
        """Get list of available voices with metadata."""
        pass
    
    @abstractmethod
    def get_supported_formats(self) -> List[str]:
        """Get list of supported audio formats."""
        pass


class ElevenLabsTTSProvider(TTSProvider):
    """ElevenLabs TTS provider implementation."""
    
    # Updated with latest ElevenLabs models (2025)
    AVAILABLE_MODELS = {
        "eleven_v3": {
            "name": "Eleven v3 (Alpha)",
            "description": "Most emotionally rich, expressive speech synthesis model",
            "languages": "70+",
            "character_limit": 10000,
            "features": ["dramatic_delivery", "multi_speaker_dialogue"]
        },
        "eleven_multilingual_v2": {
            "name": "Eleven Multilingual v2", 
            "description": "Lifelike, consistent quality speech synthesis model",
            "languages": "29",
            "character_limit": 10000,
            "features": ["stable_quality", "long_form"]
        },
        "eleven_flash_v2_5": {
            "name": "Eleven Flash v2.5",
            "description": "Fast, affordable speech synthesis model with ultra-low latency",
            "languages": "32", 
            "character_limit": 40000,
            "latency": "~75ms",
            "features": ["ultra_low_latency", "cost_effective"]
        },
        "eleven_turbo_v2_5": {
            "name": "Eleven Turbo v2.5",
            "description": "High quality, low-latency model with balanced quality and speed",
            "languages": "32",
            "character_limit": 40000, 
            "latency": "~250-300ms",
            "features": ["balanced_quality_speed"]
        }
    }
    
    SUPPORTED_FORMATS = ["mp3", "wav", "flac", "ogg"]
    
    def __init__(self, api_key: str, base_url: str = "https://api.elevenlabs.io"):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": api_key
        }
        self._voice_cache = None
        self.default_model = "eleven_multilingual_v2"  # Updated from eleven_monolingual_v1
    
    async def synthesize(self, text: str, voice: str, **kwargs) -> bytes:
        """Synthesize speech using ElevenLabs API."""
        url = f"{self.base_url}/v1/text-to-speech/{voice}"
        
        # ElevenLabs voice settings
        voice_settings = kwargs.get("voice_settings", {
            "stability": 0.5,
            "similarity_boost": 0.75,
            "style": 0.0,
            "use_speaker_boost": True
        })
        
        data = {
            "text": text,
            "model_id": kwargs.get("model", self.default_model),  # Use updated default
            "voice_settings": voice_settings
        }
        
        # Use aiohttp for async requests
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data, headers=self.headers) as response:
                if response.status == 200:
                    return await response.read()
                else:
                    error_text = await response.text()
                    raise Exception(f"ElevenLabs API error: {response.status} - {error_text}")
    
    async def get_available_voices(self) -> List[Dict[str, str]]:
        """Get ElevenLabs available voices with metadata."""
        if self._voice_cache:
            return self._voice_cache
        
        url = f"{self.base_url}/v1/voices"
        
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers) as response:
                if response.status == 200:
                    data = await response.json()
                    voices = []
                    
                    for voice in data.get("voices", []):
                        voices.append({
                            "id": voice["voice_id"],
                            "name": voice["name"],
                            "description": voice.get("description", ""),
                            "gender": voice.get("labels", {}).get("gender", "unknown"),
                            "accent": voice.get("labels", {}).get("accent", ""),
                            "age": voice.get("labels", {}).get("age", ""),
                            "use_case": voice.get("labels", {}).get("use case", ""),
                            "provider": "elevenlabs"
                        })
                    
                    self._voice_cache = voices
                    return voices
                else:
                    logging.warning("Failed to fetch ElevenLabs voices, using empty list")
                    return []
    
    def get_supported_formats(self) -> List[str]:
        """Get ElevenLabs supported audio formats."""
        return self.SUPPORTED_FORMATS


class GeminiTTSProvider(TTSProvider):
    """Google Gemini TTS provider implementation (placeholder)."""
    
    # Note: Gemini doesn't have a direct TTS API yet (as of 2025)
    # This is a placeholder for future integration or third-party solutions
    AVAILABLE_MODELS = {
        "gemini-tts-placeholder": {
            "name": "Gemini TTS (Placeholder)",
            "description": "Placeholder for future Gemini TTS integration",
            "character_limit": 1000,
            "features": ["placeholder"]
        }
    }
    
    SUPPORTED_FORMATS = ["wav"]
    
    def __init__(self, api_key: str, base_url: str = "https://generativelanguage.googleapis.com/v1beta"):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.default_model = "gemini-tts-placeholder"
        
    async def synthesize(self, text: str, voice: str, **kwargs) -> bytes:
        """Synthesize speech using Gemini TTS API."""
        # Since Gemini doesn't have TTS yet, we'll raise a helpful error
        raise NotImplementedError(
            "Gemini TTS is not yet available. Gemini API currently only supports text generation. "
            "Use OpenAI or ElevenLabs for TTS functionality. "
            "This provider is a placeholder for future Gemini TTS integration."
        )
    
    async def get_available_voices(self) -> List[Dict[str, str]]:
        """Get Gemini available voices with metadata."""
        # Placeholder voices for future implementation
        voices = [
            {
                "id": "placeholder",
                "name": "Placeholder Voice",
                "description": "Placeholder for future Gemini TTS implementation",
                "provider": "gemini"
            }
        ]
        return voices
    
    def get_supported_formats(self) -> List[str]:
        """Get Gemini supported audio formats."""
        return self.SUPPORTED_FORMATS


class TTSService:
    """Unified TTS service that manages multiple providers."""
    
    def __init__(self):
        self.providers: Dict[str, TTSProvider] = {}
        self.default_provider = "elevenlabs"
        self.default_voice = "nova"
        self.default_format = "mp3"
    
    def add_provider(self, name: str, provider: TTSProvider):
        """Add a TTS provider."""
        self.providers[name] = provider
        logging.debug(f"Added TTS provider: {name}")
    
    def set_default_provider(self, provider_name: str):
        """Set the default TTS provider."""
        if provider_name in self.providers:
            self.default_provider = provider_name
            logging.debug(f"Set default TTS provider to: {provider_name}")
        else:
            raise ValueError(f"Provider '{provider_name}' not found")
    
    async def synthesize(self, text: str, voice: str, provider: str, output_file: Optional[Path] = None, **kwargs) -> Union[Path, bytes, None]:
        """
        Synthesize speech from text.
        
        Args:
            text: Text to synthesize
            voice: Voice ID to use (provider-specific)
            provider: Provider name to use (defaults to default_provider)
            output_file: Path to save audio file
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Path to saved audio file if output_file specified, None otherwise
        """
        if text is None:
            raise ValueError("text parameter cannot be None")
        if voice is None:
            raise ValueError("voice parameter cannot be None")
        if provider is None:
            raise ValueError("provider parameter cannot be None")
        provider_name = provider
        voice_id = voice
        
        if provider_name not in self.providers:
            raise ValueError(f"Provider '{provider_name}' not available")
        
        provider_instance = self.providers[provider_name]
        
        try:
            audio_data = await provider_instance.synthesize(text, voice_id, **kwargs)
            
            if output_file is not None:
                # Write audio data to file
                with open(output_file, "wb") as f:
                    f.write(audio_data)
                logging.debug(f"Audio saved to {output_file}")
                return output_file
            
            return audio_data
            
        except Exception as e:
            logging.error(f"TTS synthesis failed with {provider_name}: {str(e)}")
            raise
    
    async def get_all_voices(self) -> Dict[str, List[Dict[str, str]]]:
        """Get voices from all providers."""
        all_voices = {}
        
        for provider_name, provider in self.providers.items():
            try:
                voices = await provider.get_available_voices()
                all_voices[provider_name] = voices
            except Exception as e:
                logging.warning(f"Failed to get voices from {provider_name}: {str(e)}")
                all_voices[provider_name] = []
        
        return all_voices
    
    async def get_voices_by_provider(self, provider_name: str) -> List[Dict[str, str]]:
        """Get voices for a specific provider."""
        if provider_name not in self.providers:
            raise ValueError(f"Provider '{provider_name}' not available")
        
        return await self.providers[provider_name].get_available_voices()
    
    def get_available_providers(self) -> List[str]:
        """Get list of available provider names."""
        return list(self.providers.keys())
    
    def get_supported_formats(self, provider_name: str = None) -> List[str]:
        """Get supported formats for a provider."""
        provider_name = provider_name or self.default_provider
        
        if provider_name not in self.providers:
            raise ValueError(f"Provider '{provider_name}' not available")
        
        return self.providers[provider_name].get_supported_formats()


# Global TTS service instance
tts_service = TTSService()


def initialize_tts_service(elevenlabs_key: str = None,
                          gemini_key: str = None,
                          elevenlabs_url: str = "https://api.elevenlabs.io",
                          gemini_url: str = "https://generativelanguage.googleapis.com/v1beta"):
    """Initialize the global TTS service with available providers (OpenAI removed)."""
    
    if elevenlabs_key:
        try:
            elevenlabs_provider = ElevenLabsTTSProvider(elevenlabs_key, elevenlabs_url)
            tts_service.add_provider("elevenlabs", elevenlabs_provider)
            logging.info("ElevenLabs TTS provider initialized")
        except Exception as e:
            logging.warning(f"Failed to initialize ElevenLabs provider: {str(e)}")
    
    if gemini_key:
        try:
            gemini_provider = GeminiTTSProvider(gemini_key, gemini_url)
            tts_service.add_provider("gemini", gemini_provider)
            logging.info("Gemini TTS provider initialized (placeholder - not functional yet)")
        except Exception as e:
            logging.warning(f"Failed to initialize Gemini provider: {str(e)}")
    
    # Set default provider preference (ElevenLabs if available)
    if "elevenlabs" in tts_service.providers:
        tts_service.set_default_provider("elevenlabs")
    elif "gemini" in tts_service.providers:
        tts_service.set_default_provider("gemini")
    else:
        logging.warning("No functional TTS providers available")


async def list_all_voices() -> Dict[str, List[Dict[str, str]]]:
    """Convenience function to list all available voices."""
    return await tts_service.get_all_voices()


async def synthesize_with_voice(text: str, voice: str, provider: str, output_file: Optional[Path] = None, **kwargs) -> Union[Path, bytes, None]:
    """Convenience function for voice synthesis."""
    if text is None:
        raise ValueError("text parameter cannot be None")
    if voice is None:
        raise ValueError("voice parameter cannot be None")
    if provider is None:
        raise ValueError("provider parameter cannot be None")
    return await tts_service.synthesize(text, voice, provider, output_file, **kwargs)
