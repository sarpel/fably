# Enhanced Fably Web Interface

This enhanced Gradio application provides a comprehensive web-based story management system for Fably.

## Features

### 📖 Story Library
- **Browse Stories**: View all existing stories from your stories directory and examples
- **Story Details**: See metadata including query, model used, voice, temperature, etc.
- **Paragraph Editor**: Edit individual paragraphs with live preview
- **Selective Audio Regeneration**: Regenerate audio for specific paragraphs with different voices
- **Batch Operations**: Save all changes or regenerate all audio at once

### ✨ Create New Story
- **Voice Input**: Record voice queries using your microphone
- **Text Input**: Type story requests directly
- **Advanced Configuration**: Adjust creativity (temperature) and length (max tokens)
- **Custom Prompts**: Modify the story generation prompt
- **Voice Selection**: Choose from available OpenAI TTS voices
- **Audio Generation**: Convert stories to speech with high-quality TTS
- **Story Saving**: Save stories in standard Fably format

### ⚙️ Settings
- **API Configuration**: Set OpenAI API key and service URLs
- **Model Selection**: Configure STT, LLM, and TTS models
- **Local Server Support**: Use local AI servers (Ollama, etc.)
- **Voice Defaults**: Set default TTS voice
- **Safety Settings**: Configure query guard phrases
- **Path Management**: Set stories and examples directories

## Quick Start

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set OpenAI API Key**:
   - Copy `.env.example` to `.env` in the main Fably directory
   - Add your OpenAI API key: `OPENAI_API_KEY=sk-...`

3. **Launch the Interface**:
   ```bash
   # Linux/Mac
   ./run_enhanced.sh
   
   # Windows
   run_enhanced.bat
   
   # Or directly
   python enhanced_app.py
   ```

4. **Access the Interface**:
   - Open your browser to `http://localhost:7860`

## Usage Guide

### Managing Existing Stories

1. Go to the **📖 Story Library** tab
2. Select a story from the dropdown list
3. View story details and metadata
4. Edit paragraphs in the text boxes
5. Choose a voice for audio regeneration
6. Click **💾 Save All Changes** to save text edits
7. Click **🎵 Regenerate All Audio** to update audio files

### Creating New Stories

1. Go to the **✨ Create New Story** tab
2. Either:
   - Record a voice query using the microphone
   - Type your request directly
3. Adjust creativity and length settings
4. Click **✨ Generate Story**
5. Review the generated story
6. Select a voice and click **🎵 Convert to Audio**
7. Click **💾 Save Story** to save in Fably format

### Configuration

1. Go to the **⚙️ Settings** tab
2. Configure API endpoints and keys
3. Set model preferences
4. Adjust default voice and generation parameters
5. Click **💾 Save Settings** to apply changes

## Local AI Server Support

The enhanced interface supports local AI servers for privacy and cost savings:

1. **LLM Server**: Use Ollama for local story generation
   - Set LLM URL to `http://localhost:11434/v1`
   - Set LLM Model to `llama3:latest` or your preferred model

2. **STT Server**: Use the included STT server for speech recognition
   - Set STT URL to `http://localhost:5000/v1`

3. **TTS Server**: Use the included TTS server for speech synthesis
   - Set TTS URL to `http://localhost:5001/v1`

See the `/servers/` directory for setup instructions.

## Safety Features

- **Query Guard**: Stories must start with configurable phrase (default: "tell me a story")
- **Content Filtering**: Uses OpenAI's built-in safety measures
- **Secure Storage**: All stories saved locally in readable format

## File Structure

Generated stories are saved in this format:
```
stories/
  your_story_name/
    info.yaml          # Story metadata
    paragraph_0.txt     # First paragraph
    paragraph_1.txt     # Second paragraph
    ...
    paragraph_0.mp3     # Audio files (when generated)
    paragraph_1.mp3
    ...
```

## Troubleshooting

### Common Issues

1. **"No stories found"**: Check that stories exist in the configured paths
2. **API errors**: Verify your OpenAI API key in Settings
3. **Audio playback issues**: Ensure your browser supports MP3/WAV playback
4. **Import errors**: Run `pip install -r requirements.txt`

### Error Messages

- **"Query must start with..."**: Add the required query guard phrase
- **"API key not found"**: Set your OpenAI API key in the .env file
- **"Error loading story"**: Check file permissions and story format

## Advanced Usage

### Custom Prompts

Modify the story generation prompt to change the storytelling style:
- Go to Create New Story tab
- Edit the "Story Generation Prompt" text area
- Examples: "Tell exciting adventure stories", "Create educational stories about science"

### Voice Switching

Different voices work better for different story types:
- **Nova**: Clear, friendly voice (default)
- **Alloy**: Neutral, professional
- **Echo**: Warm, conversational
- **Fable**: Expressive, dramatic
- **Onyx**: Deep, authoritative
- **Shimmer**: Bright, energetic

### Batch Processing

For multiple stories:
1. Use the Story Library to edit multiple stories
2. Save changes to all selected stories
3. Regenerate audio with consistent voice settings

## Integration with Main Fably

This web interface is fully compatible with the main Fably CLI application:
- Stories created here work with `fably` command
- Hardware deployments can use these stories
- All settings are portable between interfaces

## Contributing

This enhanced interface follows Fably's development standards:
- Use Black for code formatting: `black enhanced_app.py`
- Check with Pylint: `pylint enhanced_app.py`
- Follow async patterns where appropriate
- Maintain backward compatibility
