# Story Continuation Mode - User Guide

## Overview

Fably now supports **Story Continuation Mode**, allowing children to extend their favorite stories beyond the original ending. This feature enables a more interactive and persistent storytelling experience.

## How to Use Story Continuation

### Voice Commands

Children can use natural voice commands to continue stories:

- **"Continue the story"** - Continues the most recent story
- **"Continue the story about [topic]"** - Continues a specific story (e.g., "Continue the story about the princess")
- **"Tell me more about [topic]"** - Alternative phrasing for continuation
- **"What happens next"** - Continues the most recent story
- **"Keep going"** - Simple continuation request

### Examples

```
Child: "Continue the story about the space spider"
Fably: [Finds the story about space spider and continues from where it left off]

Child: "What happens next?"
Fably: [Continues the most recently created story]

Child: "Tell me more about the dog named Cosmo"
Fably: [Finds and continues the Cosmo story]
```

## CLI Usage

### Continue a Specific Story

```bash
# Continue by story directory name
fably --continue-story "about_a_princess_and_a_frog"

# Continue by topic keywords  
fably --continue-story "princess frog"
```

### Customize Continuation Patterns

```bash
# Add custom continuation phrases
fably --continuation-patterns "continue,more story,tell me more,what's next"
```

### Voice Query with Continuation

```bash
# Start in voice mode - child can say continuation commands
fably --loop
```

## How It Works

### Story Discovery

When a continuation is requested, Fably:

1. **Topic Extraction**: Analyzes the query for specific topics (e.g., "princess", "space spider")
2. **Story Matching**: Searches existing stories for keyword matches
3. **Relevance Scoring**: Ranks stories by how well they match the requested topic
4. **Fallback**: If no topic specified, uses the most recently created story

### Context Preservation

Fably maintains story consistency by:

- **Reading Previous Content**: Loads all existing paragraphs from the story
- **Context Injection**: Includes the story background in the LLM prompt
- **Character Continuity**: Maintains characters, setting, and narrative style
- **Sequential Numbering**: Continues paragraph numbering from where it left off

### Example Continuation Process

1. Child says: "Continue the story about the princess"
2. Fably searches for stories containing "princess"
3. Finds `/stories/about_a_princess_and_a_frog/`
4. Reads existing paragraphs 0-5
5. Creates continuation prompt with story context
6. Generates new paragraphs 6, 7, 8...
7. Saves new content and plays the continuation

## Story Format Compatibility

Continuation mode works with:

- ✅ Stories created via voice commands
- ✅ Stories created via CLI text input
- ✅ Stories created via web interface
- ✅ Both OpenAI and ElevenLabs generated stories
- ✅ Stories with any voice/model configuration

## Configuration Options

### Continuation Patterns (CLI)

```bash
--continuation-patterns "continue the story,tell me more,what happens next,continue,keep going,more story"
```

### Direct Continuation (CLI)

```bash
--continue-story "topic or directory name"
```

### Safety Integration

Story continuation respects all existing safety features:

- **Query Guard**: Continuation patterns are validated alongside "tell me a story"
- **Content Filtering**: OpenAI safety measures apply to continued content
- **Query Logging**: All continuation requests are logged and saved

## Technical Details

### File Structure

Continued stories maintain the same structure:

```
stories/about_a_princess_and_a_frog/
├── info.yaml                 # Original story metadata
├── voice_query.wav           # Original voice request
├── paragraph_0.txt           # Original story paragraphs
├── paragraph_1.txt
├── ...
├── paragraph_5.txt
├── paragraph_6.txt           # New continuation paragraphs
├── paragraph_7.txt
└── ...
```

### Context Management

- **Max Context**: Up to 10 previous paragraphs included in continuation prompts
- **Memory Efficiency**: Large stories are summarized to fit context limits
- **Prompt Engineering**: Specialized continuation prompts maintain narrative coherence

## Troubleshooting

### "No story found to continue"

**Cause**: Fably couldn't find a matching story for the topic.

**Solutions**:
- Use more specific keywords from the original story
- Try "continue" or "what happens next" to use the most recent story
- Check that stories exist in the configured stories directory

### Story doesn't match expected content

**Cause**: Multiple stories might match the same keywords.

**Solutions**:
- Use more specific topic keywords
- Use the exact directory name with `--continue-story`
- Check existing story directories to understand naming

### Continuation feels disconnected

**Cause**: The story context might be too large or the prompt unclear.

**Solutions**:
- This is rare due to context injection, but regenerating might help
- The LLM occasionally creates slight variations - this is normal creative behavior

## Voice Interface Tips

### For Children

- **Be Specific**: "Continue the story about the magic dog" works better than "continue"
- **Use Keywords**: Include memorable words from the original story
- **Natural Speech**: Normal conversation works - no need for special commands
- **Repeat if Needed**: Fably will ask for clarification if the request is unclear

### For Parents

- Test continuation phrases during setup
- Review generated content as stories develop
- Use the web interface to manage longer story collections
- Set voice cycle mode for variety in continued stories

## Integration with Existing Features

Story continuation works seamlessly with:

- **Voice Cycling**: Continue stories with different voices
- **Web Interface**: Browse and continue stories via the enhanced Gradio app  
- **Multiple Providers**: Works with both OpenAI and ElevenLabs TTS
- **Hardware Controls**: Button press can trigger continuation if recent voice query was a continuation request

This feature transforms Fably from a single-story generator into a persistent storytelling companion that grows with your child's imagination.
