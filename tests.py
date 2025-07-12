py',
        'fably/voice_manager.py',
        'fably/tts_service.py',
        'web_interface/app.py',
        'fably-setup.sh',
        'DOCUMENTATION.md'
    ]
    
    optional_dirs = [
        'fably/examples',
        'fably/stories',
        'tools',
        'servers'
    ]
    
    for file_path in essential_files:
        if Path(file_path).exists():
            print(f"✅ {file_path} exists")
        else:
            print(f"❌ {file_path} missing")
            return False
    
    for dir_path in optional_dirs:
        if Path(dir_path).exists():
            print(f"✅ {dir_path}/ directory exists")
        else:
            print(f"⚠️  {dir_path}/ directory missing (optional)")
    
    return True


def test_command_availability():
    """Test that fably command is available"""
    print("\n💻 Testing command availability...")
    
    try:
        result = subprocess.run(['fably', '--help'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ fably command available")
            print(f"✅ Help output: {len(result.stdout.split())} words")
            return True
        else:
            print(f"❌ fably command failed: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("❌ fably command timed out")
        return False
    except FileNotFoundError:
        print("❌ fably command not found")
        print("   Try: pip install --editable .")
        return False


def test_basic_functionality():
    """Test basic Fably functionality without API calls"""
    print("\n🚀 Testing basic functionality...")
    
    try:
        # Test story directory creation
        from fably.utils import ensure_stories_directory
        stories_dir = ensure_stories_directory()
        print(f"✅ Stories directory: {stories_dir}")
        
        # Test configuration loading
        from fably.cli import load_configuration
        config = load_configuration()
        print(f"✅ Configuration loaded: {len(config)} settings")
        
        # Test sound file access
        from fably.utils import get_sound_file_path
        try:
            calibrating_path = get_sound_file_path("calibrating_text.txt")
            if calibrating_path and Path(calibrating_path).exists():
                print("✅ Sound files accessible")
            else:
                print("⚠️  Sound files not found (will be created when needed)")
        except:
            print("⚠️  Sound file access test skipped")
        
        return True
        
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        return False


def test_story_examples():
    """Test example stories"""
    print("\n📚 Testing example stories...")
    
    examples_dir = Path('fably/examples')
    if not examples_dir.exists():
        print("⚠️  Examples directory not found")
        return True
    
    example_count = 0
    for provider_dir in examples_dir.iterdir():
        if provider_dir.is_dir():
            for story_dir in provider_dir.iterdir():
                if story_dir.is_dir() and (story_dir / 'info.yaml').exists():
                    example_count += 1
    
    print(f"✅ Found {example_count} example stories")
    
    if example_count >= 2:
        print("✅ Sufficient examples for testing")
        return True
    else:
        print("⚠️  Limited examples available")
        return True


# ================================================================================
# INTEGRATION TESTS
# ================================================================================

def test_web_interface():
    """Test web interface startup"""
    print("\n🌐 Testing web interface...")
    
    try:
        # Check web interface dependencies
        import gradio as gr
        print("✅ Gradio imported successfully")
        
        # Check web interface file
        web_app_path = Path('web_interface/app.py')
        if web_app_path.exists():
            print("✅ Web interface app.py exists")
        else:
            print("❌ Web interface app.py not found")
            return False
        
        # Check requirements
        web_reqs_path = Path('web_interface/requirements.txt')
        if web_reqs_path.exists():
            print("✅ Web interface requirements.txt exists")
        else:
            print("⚠️  Web interface requirements.txt missing")
        
        return True
        
    except ImportError as e:
        print(f"❌ Web interface dependencies missing: {e}")
        print("   Install with: pip install gradio")
        return False


def test_raspberry_pi_features():
    """Test Raspberry Pi specific features"""
    print("\n🍓 Testing Raspberry Pi features...")
    
    # Check if running on Raspberry Pi
    try:
        with open('/proc/cpuinfo', 'r') as f:
            cpuinfo = f.read()
        is_pi = "Raspberry Pi" in cpuinfo
    except FileNotFoundError:
        is_pi = False
    
    if is_pi:
        print("✅ Running on Raspberry Pi")
        
        # Test GPIO availability
        try:
            import gpiozero
            print("✅ GPIO Zero available")
        except ImportError:
            print("⚠️  GPIO Zero not available (install with: pip install gpiozero)")
        
        # Test LED/button modules
        try:
            from fably import leds
            print("✅ LED module available")
        except ImportError:
            print("⚠️  LED module not available")
    else:
        print("ℹ️  Not running on Raspberry Pi (skipping Pi-specific tests)")
    
    return True


# ================================================================================
# PERFORMANCE TESTS
# ================================================================================

def test_memory_usage():
    """Test memory usage for Pi Zero 2W optimization"""
    print("\n🧠 Testing memory usage...")
    
    try:
        import psutil
        process = psutil.Process()
        memory_mb = process.memory_info().rss / 1024 / 1024
        print(f"✅ Current memory usage: {memory_mb:.1f}MB")
        
        if memory_mb < 100:
            print("✅ Memory usage optimal for Pi Zero 2W")
        elif memory_mb < 200:
            print("⚠️  Memory usage acceptable for Pi Zero 2W")
        else:
            print("❌ Memory usage high for Pi Zero 2W")
            
    except ImportError:
        print("⚠️  psutil not available for memory testing")
    
    return True


def test_startup_time():
    """Test application startup performance"""
    print("\n⏱️ Testing startup performance...")
    
    start_time = time.time()
    
    try:
        # Simulate fably import and initialization
        import fably
        from fably import cli, utils
        
        startup_time = time.time() - start_time
        print(f"✅ Import time: {startup_time:.2f} seconds")
        
        if startup_time < 3.0:
            print("✅ Fast startup (good for Pi Zero 2W)")
        elif startup_time < 10.0:
            print("⚠️  Moderate startup time")
        else:
            print("❌ Slow startup (may impact Pi Zero 2W)")
        
        return True
        
    except Exception as e:
        print(f"❌ Startup test failed: {e}")
        return False


# ================================================================================
# MAIN TEST FUNCTIONS
# ================================================================================

def run_asyncio_test(multithreaded, paragraphs):
    """Run the asyncio pipeline test"""
    print(f"\n🔄 Running asyncio pipeline test...")
    print(f"Mode: {'Multi-threaded' if multithreaded else 'Single-threaded'}")
    print(f"Paragraphs: {paragraphs}")
    
    start_time = time.time()
    asyncio.run(async_main(multithreaded, paragraphs))
    elapsed = time.time() - start_time
    
    # Calculate expected optimal time
    expected = WRITER_TIME + READER_TIME + paragraphs * SPEAKER_TIME
    delta = elapsed - expected
    
    print(f"\n📊 Asyncio Test Results:")
    print(f"Actual time: {elapsed:.2f} seconds")
    print(f"Expected optimal: {expected:.2f} seconds")
    print(f"Difference: {delta:.2f} seconds ({'faster' if delta < 0 else 'slower'} than optimal)")
    
    if delta < 2.0:
        print("✅ Excellent asyncio performance")
    elif delta < 5.0:
        print("⚠️  Acceptable asyncio performance")
    else:
        print("❌ Poor asyncio performance")


def run_all_tests():
    """Run comprehensive test suite"""
    print("🎭 Fably Comprehensive Test Suite")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_imports),
        ("Audio Dependencies", test_audio_dependencies),
        ("AI Dependencies", test_ai_dependencies),
        ("Environment Config", test_environment_config),
        ("File Structure", test_file_structure),
        ("Command Availability", test_command_availability),
        ("Basic Functionality", test_basic_functionality),
        ("Story Examples", test_story_examples),
        ("Web Interface", test_web_interface),
        ("Raspberry Pi Features", test_raspberry_pi_features),
        ("Memory Usage", test_memory_usage),
        ("Startup Performance", test_startup_time)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                failed += 1
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            failed += 1
            print(f"💥 {test_name} CRASHED: {e}")
    
    print(f"\n🏁 Test Summary:")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Success Rate: {passed/(passed+failed)*100:.1f}%")
    
    if failed == 0:
        print("\n🎉 All tests passed! Fably is ready to use.")
    elif failed <= 2:
        print("\n⚠️  Minor issues detected. Fably should work but check failed tests.")
    else:
        print("\n🔧 Multiple issues detected. Review failed tests and run setup again.")


# ================================================================================
# CLI INTERFACE
# ================================================================================

@click.command()
@click.option(
    "--test-type",
    type=click.Choice(['all', 'asyncio', 'quick', 'imports', 'audio', 'web']),
    default='quick',
    help="Type of test to run"
)
@click.option(
    "--multithreaded/--singlethreaded",
    default=True,
    help="Whether to use multithreading for asyncio test"
)
@click.option(
    "--paragraphs",
    default=3,
    help="Number of paragraphs for asyncio test",
    type=int
)
def main(test_type, multithreaded, paragraphs):
    """
    Fably Comprehensive Test Suite
    
    Run various tests to verify Fably installation and functionality.
    """
    
    if test_type == 'all':
        run_all_tests()
        print("\n" + "="*50)
        run_asyncio_test(multithreaded, paragraphs)
        
    elif test_type == 'asyncio':
        run_asyncio_test(multithreaded, paragraphs)
        
    elif test_type == 'quick':
        print("🚀 Quick Test Suite")
        print("=" * 30)
        
        quick_tests = [
            ("Imports", test_imports),
            ("Environment", test_environment_config),
            ("File Structure", test_file_structure),
            ("Command", test_command_availability)
        ]
        
        for test_name, test_func in quick_tests:
            print(f"\n--- {test_name} ---")
            test_func()
            
    elif test_type == 'imports':
        test_imports()
        
    elif test_type == 'audio':
        test_audio_dependencies()
        
    elif test_type == 'web':
        test_web_interface()


if __name__ == "__main__":
    # pylint: disable=no-value-for-parameter
    main()
