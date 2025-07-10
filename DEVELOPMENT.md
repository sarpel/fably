# Fably Development Guide

This comprehensive guide covers development procedures, enhancement plans, web interface development, and project improvement strategies for the Fably AI storytelling system.

## 🛠️ Development Environment Setup

### Prerequisites
- Python 3.8+
- Virtual environment management
- Git version control
- Modern code editor (VS Code recommended)

### Development Installation
```bash
# Clone the repository
git clone https://github.com/sarpel/fably.git
cd fably

# Set up development environment
python3 -m venv .venv
source .venv/bin/activate
pip install --editable .

# Install development dependencies
pip install black pylint pytest

# Set up pre-commit hooks (optional)
pip install pre-commit
pre-commit install
```

### Development Tools
```bash
# Code formatting
./dev-tools.sh format
# Or: black fably tools servers

# Code quality checks  
./dev-tools.sh check
# Or: pylint fably tools/*.py servers/*/

# Run tests
./dev-tools.sh test

# Debug functionality
./dev-tools.sh debug "test hikayesi"
```

## 📋 Project Enhancement Roadmap

### ✨ Quality of Life Improvements

#### 1. Web Interface Story Management
Currently using `gradio` for basic testing. Planned enhancements:

**Story Library Management:**
- **Hikaye Kütüphanesi**: List existing stories from `fably/stories` directory
- **Selection Interface**: Browse and select stories from organized list
- **Text Editor**: Edit story paragraphs with real-time preview
- **Selective Regeneration**: "Save and Refresh Audio" button for modified paragraphs only
- **Batch Operations**: Update multiple stories efficiently

**Implementation Priority:** High - User requested feature

#### 2. Dynamic Voice and Character Selection
Currently TTS voice parameters are set via command line. Planned improvements:

**Web Interface Voice Controls:**
- **Voice Selection Dropdown**: Choose from OpenAI voices (`nova`, `alloy`, `shimmer`, etc.)
- **Real-time Preview**: Sample voice before story generation
- **Voice Cycling**: Hardware button patterns for voice switching

**Device-Level Controls:**
- **Hardware Button Patterns**: Double-tap to cycle voices
- **Voice Memory**: Remember preferred voice per story type

#### 3. Story Continuation System
Replace single-shot generation with continuation capabilities:

**Continuation Features:**
- **Context Preservation**: Maintain story state and character consistency
- **Chapter-based Stories**: Extend stories across multiple sessions
- **Interactive Choices**: Allow user input to influence story direction
- **Bookmark System**: Resume stories from specific points

#### 4. Advanced Audio Quality Enhancement
**Noise Reduction Improvements:**
- **Adaptive Filtering**: Dynamic noise floor adjustment using `tools/noise_floor.py`
- **Environment Calibration**: Automatic ambient noise measurement
- **False Trigger Prevention**: Smart activation to reduce unwanted responses
- **Audio Quality Monitoring**: Real-time input signal analysis

### 🚀 Technical Enhancements

#### 1. Wakeword Detection System
Replace button-only activation with voice activation:

**Wakeword Engine Integration:**
- **OpenWakeWord**: Integration for "Hey Fably" detection
- **MicroWakeWord**: Lightweight alternative for Pi Zero 2W
- **Custom Training**: Project-specific wakeword models
- **Sensitivity Tuning**: Adjustable detection thresholds

**Implementation Benefits:**
- Natural interaction without physical button
- Enhanced user experience for children
- Hands-free operation capability

#### 2. Containerization and Self-Hosting
Support Docker deployment for simplified distribution:

**Docker Implementation:**
- **Main Application Container**: `Dockerfile` for core Fably app
- **Server Containers**: Individual containers for STT/TTS/LLM servers
- **Docker Compose**: Single-command deployment with `docker-compose.yml`
- **Environment Configuration**: Containerized settings management

**Benefits:**
- Simplified deployment process
- Consistent environment across platforms
- Easy scaling and management
- Self-hosting capability for privacy

#### 3. Enhanced Error Handling and Status Reporting
**Error Management System:**
- **Voice Feedback**: Audio error messages in Turkish ("İnternete bağlanamıyorum", "Model yüklenirken sorun oluştu")
- **LED Status Indicators**: Visual feedback system using hardware LEDs
  - 🔵 Blue: System ready
  - 🟢 Green: Listening
  - 🟡 Yellow: Processing story
  - 🔴 Red: Error occurred
- **Graceful Degradation**: Fallback systems for network/API failures

## 🌐 Enhanced Web Interface Development

### Current Implementation
The enhanced Gradio application provides comprehensive story management:

#### Core Features
- **📖 Story Library**: Browse and edit existing stories
- **✨ Story Creation**: Voice and text input with configuration
- **⚙️ Settings Management**: API configuration and model selection
- **🎵 Audio Generation**: High-quality TTS with voice selection

#### Technical Architecture
```python
# Enhanced app structure
enhanced_app.py:
  ├── Story Library Tab
  │   ├── Story selection and metadata display
  │   ├── Paragraph editing with live preview
  │   └── Selective audio regeneration
  ├── Story Creation Tab
  │   ├── Voice recording interface
  │   ├── Text input with prompt customization
  │   └── Advanced configuration options
  └── Settings Tab
      ├── API key management
      ├── Model configuration
      └── Default parameter settings
```

#### Development Standards
```bash
# Install development requirements
cd tools/gradio_app
pip install -r requirements.txt

# Launch development server
./dev-tools.sh web-enhanced
# Or: python enhanced_app.py

# Code formatting for web components
black enhanced_app.py

# Testing web interface
./dev-tools.sh test
```

### Future Web Interface Enhancements

#### Real-Time Collaboration
- **Multi-User Support**: Family members can contribute to stories
- **Live Story Building**: Real-time collaborative story creation
- **Version Control**: Track story changes and revisions

#### Advanced Audio Features
- **Sound Effects Integration**: Background sounds and music
- **Voice Character Mapping**: Different voices for different characters
- **Audio Timeline Editor**: Precise control over audio timing

#### Mobile Optimization
- **Responsive Design**: Full mobile browser support
- **Touch Interface**: Gesture-based controls for tablets
- **Offline Capability**: Progressive Web App (PWA) features

## 🔧 Development Best Practices

### Code Organization
```
fably/
├── fably/                   # Core application
│   ├── cli.py              # Command-line interface
│   ├── fably.py            # Main application logic
│   ├── utils.py            # Utility functions
│   ├── voice_manager.py    # Voice recognition
│   └── tts_service.py      # Text-to-speech
├── tools/                  # Development tools
│   ├── gradio_app/        # Web interface
│   └── *.py               # Utility scripts
├── servers/               # Local AI servers
└── tests/                 # Test suite
```

### Coding Standards
```bash
# File formatting requirements
black --line-length 120 fably/

# Code quality requirements  
pylint --rcfile=.pylintrc fably/

# Import organization
isort fably/

# Type checking (optional)
mypy fably/
```

### Testing Strategy
```python
# Unit tests for core functionality
pytest tests/test_fably.py

# Integration tests for full workflow
pytest tests/test_integration.py

# Audio testing
python tools/capture_voice_query.py

# Hardware testing (Pi only)
python tools/button_play_leds.py
```

### Git Workflow
```bash
# Feature development
git checkout -b feature/story-continuation
git commit -m "feat: add story continuation system"

# Bug fixes
git checkout -b fix/audio-crackling
git commit -m "fix: resolve audio buffer issues"

# Release preparation
git checkout -b release/v1.1.0
git commit -m "chore: prepare v1.1.0 release"
```

## 📊 Performance Optimization

### Raspberry Pi Zero 2W Optimization
```python
# Memory management
import gc
gc.collect()  # Periodic garbage collection

# CPU optimization
import os
os.nice(10)   # Lower process priority for background tasks

# Audio buffer optimization
BUFFER_SIZE = 1024  # Optimized for Pi Zero 2W
SAMPLE_RATE = 16000 # Reduced for lower CPU usage
```

### Resource Monitoring
```bash
# Monitor system resources during development
htop

# Check memory usage
free -h

# Monitor temperature (Pi)
watch -n 1 vcgencmd measure_temp
```
- [ ] Error handling and recovery
- [ ] Memory usage under continuous operation
- [ ] Network failure graceful degradation

## 🚀 Deployment and Distribution

### Production Build Process
```bash
# Create production build
./setup.sh clean
./setup.sh install

# Generate distribution package
python setup.py sdist bdist_wheel

# Create hardware-specific packages
./create_pi_image.sh      # Raspberry Pi SD card image
./create_docker_image.sh  # Docker container
```

### Release Management
```bash
# Version bumping
bumpversion patch  # 1.0.0 -> 1.0.1
bumpversion minor  # 1.0.1 -> 1.1.0
bumpversion major  # 1.1.0 -> 2.0.0

# Tag releases
git tag -a v1.1.0 -m "Release version 1.1.0"
git push origin v1.1.0

# Generate release notes
git log --oneline v1.0.0..v1.1.0
```

## 🎯 Project Milestones and Roadmap

### Phase 1: Core Functionality ✅ Complete
- [x] Basic story generation
- [x] Voice recognition
- [x] Text-to-speech synthesis
- [x] Hardware button integration
- [x] LED status indicators

### Phase 2: Enhanced User Experience 🔄 In Progress
- [x] Web interface development
- [x] Story library management
- [x] Voice selection options
- [ ] Story continuation system
- [ ] Advanced audio quality

### Phase 3: Advanced Features 📋 Planned
- [ ] Wakeword detection integration
- [ ] Containerization support
- [ ] Multi-language support expansion
- [ ] Advanced error handling
- [ ] Performance optimization

### Phase 4: Production Readiness 🎯 Future
- [ ] Automated testing suite
- [ ] Documentation completion
- [ ] Distribution packaging
- [ ] Hardware certification
- [ ] Security audit

## 🔐 Security and Privacy Considerations

### Data Privacy
```python
# Local data storage only
STORIES_PATH = "./fably/stories"  # Local filesystem
CACHE_PATH = "./fably/cache"      # No cloud storage

# API key security
load_dotenv()  # Environment variables only
# Never commit API keys to repository
```

### Child Safety
```python
# Content filtering
SAFETY_PROMPT = """
Generate appropriate stories for 5-year-old children.
Avoid scary, violent, or inappropriate content.
Focus on positive, educational, and fun themes.
"""

# Query validation
def validate_child_safe_query(query):
    # Implement content filtering logic
    pass
```

### Network Security
```bash
# Firewall configuration for Pi deployment
sudo ufw enable
sudo ufw allow 22    # SSH
sudo ufw allow 7860  # Web interface
sudo ufw deny 80     # Block unused web ports
```

## 📚 Documentation Standards

### Code Documentation
```python
def generate_story(prompt: str, voice: str = "nova") -> Dict[str, Any]:
    """
    Generate a story using AI language model.
    
    Args:
        prompt: The story prompt from user
        voice: TTS voice to use for audio generation
        
    Returns:
        Dictionary containing story metadata and content
        
    Raises:
        APIError: When external API calls fail
        ValidationError: When prompt validation fails
    """
    pass
```

### User Documentation
- **README.md**: Main project overview and quick start
- **HARDWARE_SETUP.md**: Hardware configuration guide
- **API_REFERENCE.md**: Developer API documentation
- **TROUBLESHOOTING.md**: Common issues and solutions

### Development Documentation
- **DEVELOPMENT.md**: This file - comprehensive development guide
- **CONTRIBUTING.md**: Guidelines for external contributors
- **CHANGELOG.md**: Version history and changes
- **LICENSE.md**: Project licensing information

## 🤝 Contributing Guidelines

### Getting Started
1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Follow coding standards and run tests
4. Submit pull request with detailed description

### Code Review Process
- All changes require peer review
- Automated tests must pass
- Code coverage should not decrease
- Documentation must be updated for new features

### Issue Reporting
```markdown
## Bug Report Template
**Environment:**
- OS: [e.g., Raspberry Pi OS]
- Python version: [e.g., 3.9.2]
- Fably version: [e.g., 1.0.0]

**Steps to Reproduce:**
1. Step one
2. Step two
3. Error occurs

**Expected Behavior:**
Description of expected result

**Actual Behavior:**
Description of what actually happened

**Additional Context:**
Any other relevant information
```

## 🎮 Interactive Development Tools

### Development Commands
```bash
# Quick development setup
./dev-tools.sh setup

# Run development server with hot reload
./dev-tools.sh serve --reload

# Generate test stories for development
./dev-tools.sh generate-test-stories

# Profile performance
./dev-tools.sh profile --duration 60

# Memory leak detection
./dev-tools.sh memory-check
```

### Debugging Tools
```python
# Debug mode activation
import logging
logging.basicConfig(level=logging.DEBUG)

# Memory profiling
import tracemalloc
tracemalloc.start()

# Performance timing
import time
start_time = time.time()
# ... code to measure ...
elapsed = time.time() - start_time
```

## 🌟 Innovation and Future Directions

### AI/ML Enhancements
- **Local AI Models**: Integration with smaller, specialized models
- **Personalization**: Adaptive storytelling based on user preferences
- **Multilingual Support**: Expanding beyond Turkish to other languages
- **Voice Cloning**: Family member voice synthesis for characters

### Hardware Integrations
- **IoT Connectivity**: Smart home integration
- **Wearable Devices**: Smartwatch controls
- **Visual Elements**: E-ink displays for story illustrations
- **Gesture Control**: Camera-based interaction

### Community Features
- **Story Sharing**: Safe community story exchange
- **Collaborative Creation**: Family story building
- **Educational Integration**: Curriculum-aligned content
- **Accessibility**: Support for special needs children

This development guide provides a comprehensive framework for contributing to and enhancing the Fably project. Whether you're implementing new features, fixing bugs, or improving documentation, these guidelines will help ensure high-quality, maintainable code that serves the project's mission of providing safe, engaging AI-powered storytelling for children.
