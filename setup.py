from setuptools import setup, find_packages

setup(
    name='fably',
    version='1.0.0',
    python_requires='>=3.8',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'openai>=1.0.0',
        'requests',
        'click',
        'python-dotenv',
        'pyyaml',
        'numpy',
        'sounddevice',
        'soundfile',
        'vosk',
        'pydub',
        'aiohttp',
        # Platform-specific dependencies for Raspberry Pi
        'apa102-pi; platform_machine=="armv7l" or platform_machine=="aarch64"',
        'gpiozero; platform_machine=="armv7l" or platform_machine=="aarch64"',
        'RPi.GPIO; platform_machine=="armv7l" or platform_machine=="aarch64"',
        # Wakeword engines (optional, platform-specific)
        'pvporcupine; platform_machine=="armv7l" or platform_machine=="aarch64"',
        'onnxruntime; platform_machine!="armv7l"',
    ],
    extras_require={
        'dev': [
            'black',
            'pylint',
            'pytest',
        ],
        'wakeword': [
            'pvporcupine',
            'onnxruntime', 
            'tflite-runtime',
        ],
        'web': [
            'gradio',
            'plotly',
            'pandas',
        ],
    },
    entry_points={
        'console_scripts': [
            'fably=fably.cli:cli',
        ],
    },
    package_data={
        'fably': [
            'sounds/*.wav',
            'sounds/*.txt', 
            '*.txt',
            'examples/**/*',
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Multimedia :: Sound/Audio :: Speech",
        "Topic :: Education",
    ],
    description="AI storyteller for children - Turkish language optimized for 5-year-old",
    author="Fably Contributors",
    author_email="fably@example.com",
    url="https://github.com/sarpel/fably",
)
