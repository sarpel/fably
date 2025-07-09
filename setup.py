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
    ],
    entry_points='''
        [console_scripts]
        fably=fably.cli:cli
    ''',
)
