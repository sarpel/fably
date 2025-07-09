from setuptools import setup, find_packages

setup(
    name='fably',
    version='1.0',
    python_requires='>3.8',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'openai',
        'apa102-pi',
        'sounddevice',
        'soundfile',
        'requests',
        'click',
        'python-dotenv',
        'pyyaml',
        'vosk',
        'numpy',
        'pydub',
        'gpiozero',
        'aiohttp',  # For ElevenLabs async requests
        # Wakeword engines (optional)
        'pvporcupine; platform_machine=="armv7l" or platform_machine=="aarch64"',  # PPN for Pi
        'onnxruntime; platform_machine!="armv7l"',  # ONNX for other platforms
    ],
    entry_points='''
        [console_scripts]
        fably=fably.cli:cli
    ''',
)
