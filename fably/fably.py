"""
Main Fably logic.
"""

import asyncio
import concurrent.futures
import logging
import shutil
import time
import threading

import openai

try:
    from gpiozero import Button
except (ImportError, NotImplementedError):
    Button = None

from fably import utils
from fably.wakeword import create_wakeword_detector, get_available_engines


def generate_story(ctx, query, prompt):
    """
    Generates a story stream based on a given query and prompt using the OpenAI API and persists the information
    about the models used to generate the story to a file.
    """
    
    # Handle different parameter names and support for different models
    completion_params = {
        "stream": True,
        "model": ctx.llm_model,
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": query},
        ],
    }
    
    # Handle reasoning models (o-series) vs regular models
    if ctx.llm_model.startswith(("o1", "o3", "o4")):
        # Reasoning models: use max_completion_tokens, no temperature/top_p
        completion_params["max_completion_tokens"] = ctx.max_tokens
        # Note: o-series models have fixed temperature=1, top_p=1 internally
    else:
        # Regular models: use max_tokens and support temperature
        completion_params["max_tokens"] = ctx.max_tokens
        completion_params["temperature"] = ctx.temperature

    return ctx.llm_client.chat.completions.create(**completion_params)


async def synthesize_audio(ctx, story_path, index, text=None):
    """
    Fetches TTS audio for a given paragraph of a story and saves it to a file.
    Uses the new TTS service abstraction for multi-provider support.
    """
    logging.debug("Synthesizing audio for paragraph %i...", index)

    audio_file_path = story_path / f"paragraph_{index}.{ctx.tts_format}"

    if audio_file_path.exists():
        logging.debug("Paragraph %i audio already exists at %s", index, audio_file_path)
        return audio_file_path

    if not text:
        text_file_path = story_path / f"paragraph_{index}.txt"
        if text_file_path.exists():
            logging.debug(
                "Reading paragraph %i text from %s ...", index, text_file_path
            )
            text = utils.read_from_file(text_file_path)
        else:
            raise ValueError(f"No text found for paragraph {index} in {story_path}")

    # Use the new TTS service if available, fallback to legacy OpenAI client
    if hasattr(ctx, 'tts_service') and ctx.tts_service:
        try:
            await ctx.tts_service.synthesize(
                text=text,
                voice=ctx.tts_voice,
                provider=getattr(ctx, 'tts_provider', None),
                output_file=audio_file_path,
                format=ctx.tts_format,
                model=ctx.tts_model
            )
        except Exception as e:
            logging.error(f"TTS service synthesis failed: {str(e)}")
            # Fallback to legacy OpenAI client
            response = await ctx.tts_client.audio.speech.create(
                input=text,
                model=ctx.tts_model,
                voice=ctx.tts_voice,
                response_format=ctx.tts_format,
            )
            response.write_to_file(audio_file_path)
    else:
        # Legacy OpenAI client
        response = await ctx.tts_client.audio.speech.create(
            input=text,
            model=ctx.tts_model,
            voice=ctx.tts_voice,
            response_format=ctx.tts_format,
        )
        response.write_to_file(audio_file_path)

    logging.debug("Saved audio for paragraph %i to %s", index, audio_file_path)
    return audio_file_path


async def writer(ctx, story_queue, query=None):
    """
    Creates a story based on a voice query or story request.

    If a textual query is given, it is used. If not, it records sound until silence,
    then transcribes the voice query.

    Then it uses a large generative language model to create a story based on the query,
    processes the returned content as a stream, chunks it into paragraphs and appends them
    to the queue for downstream processing.
    """
    if query:
        query_local = "n/a"
        voice_query_file = None
    elif hasattr(ctx, 'story_request') and ctx.story_request:
        # Handle specific story request
        query = f"bana {ctx.story_request} hakkında bir hikaye anlat"
        query_local = "story_request"
        voice_query_file = None
        logging.info("Story request: %s", ctx.story_request)
    else:
        utils.play_sound("what_story", audio_driver=ctx.sound_driver)

        # Use enhanced recording with noise reduction if enabled
        if getattr(ctx, 'noise_reduction', False):
            voice_query, query_sample_rate, query_local = utils.record_until_silence_with_noise_reduction(
                ctx.recognizer, 
                ctx.trim_first_frame,
                noise_floor=getattr(ctx, 'noise_floor', None),
                noise_sensitivity=getattr(ctx, 'noise_sensitivity', 2.0),
                enable_noise_reduction=True
            )
        else:
            voice_query, query_sample_rate, query_local = utils.record_until_silence(
                ctx.recognizer, ctx.trim_first_frame
            )
        query, voice_query_file = utils.transcribe(
            ctx.stt_client,
            voice_query,
            ctx.stt_model,
            ctx.language,
            query_sample_rate,
            ctx.queries_path,
        )
        logging.info("Voice query: %s [%s]", query, query_local)

    # Check if this is a continuation query
    is_continuation = utils.is_continuation_query(query, ctx.continuation_patterns)
    
    # For new stories, let the LLM handle any request intelligently
    # No more rigid query validation - users can speak freely!

    # Handle story continuation
    if is_continuation:
        # Find story to continue
        continue_story_path = utils.find_story_for_continuation(
            ctx.stories_path, query, ctx.continuation_patterns
        )
        
        if not continue_story_path:
            logging.warning("No existing story found to continue")
            utils.play_sound("sorry", audio_driver=ctx.sound_driver)
            await story_queue.put(None)
            return
        
        # Use existing story path and get continuation context
        story_path = continue_story_path
        story_context = utils.extract_story_context(story_path, max_paragraphs=10)
        starting_paragraph_index = utils.get_next_paragraph_index(story_path)
        
        logging.info(f"Continuing story '{story_context['original_query']}' from paragraph {starting_paragraph_index}")
        
        # Read existing paragraphs to queue them for replay
        for index in range(story_context['paragraph_count']):
            await story_queue.put((story_path, index, None))
        
    else:
        # Handle new story creation
        story_path = ctx.stories_path / utils.query_to_filename(
            query, prefix=""  # No prefix needed anymore
        )
        story_context = None
        starting_paragraph_index = 0

    # Generate new content if needed
    if ctx.ignore_cache or (
        not ctx.ignore_cache and (is_continuation or (not story_path.exists() and not story_path.is_dir()))
    ):
        if not is_continuation:
            logging.debug("Creating story folder at %s", story_path)
            story_path.mkdir(parents=True, exist_ok=True)

            logging.debug("Writing model info to disk...")
            ctx.persist_runtime_params(
                story_path / "info.yaml",
                query=query,
                query_local=query_local,
            )

        # This file will not exist when the query is passed as an argument
        if voice_query_file:
            logging.debug("Copying the original voice query...")
            shutil.move(voice_query_file, story_path / "voice_query.wav")

        logging.debug("Reading prompt...")
        base_prompt = utils.read_from_file(ctx.prompt_file)
        
        # Create continuation-aware prompt if needed
        if is_continuation and story_context:
            continuation_context = "\n\n".join(story_context['paragraphs'])
            prompt = f"{base_prompt}\n\nYou are continuing an existing story. Here is what has happened so far:\n\nOriginal request: {story_context['original_query']}\n\nStory so far:\n{continuation_context}\n\nNow continue this story based on the user's request: {query}"
        else:
            prompt = base_prompt

        logging.debug("Creating story...")
        story_stream = await generate_story(ctx, query, prompt)

        index = starting_paragraph_index
        paragraph = []

        logging.debug("Iterating over the story stream to capture paragraphs...")
        async for chunk in story_stream:
            fragment = chunk.choices[0].delta.content
            if fragment is None:
                break

            paragraph.append(fragment)

            if fragment.endswith("\n\n"):
                paragraph_str = "".join(paragraph)
                logging.info("Paragraph %i: %s", index, paragraph_str)
                utils.write_to_file(
                    story_path / f"paragraph_{index}.txt", paragraph_str
                )
                await story_queue.put((story_path, index, paragraph_str))
                index += 1
                paragraph = []

        logging.debug("Finished processing the story stream.")
    else:
        logging.debug("Reading cached story at %s", story_path)
        for index in range(len(list(story_path.glob("paragraph_*.txt")))):
            await story_queue.put((story_path, index, None))

    logging.debug("Done processing the story.")
    await story_queue.put(None)  # Indicates that we're done


async def reader(ctx, story_queue, reading_queue):
    """
    Processes the queue of paragraphs and sends them off to be read
    and synthezized into audio files to be read by the speaker.
    """
    while ctx.talking:
        item = await story_queue.get()
        if item is None:
            logging.debug("Done reading the story.")
            await reading_queue.put(None)
            break

        story_path, index, paragraph = item

        audio_file = await synthesize_audio(ctx, story_path, index, paragraph)
        await reading_queue.put(audio_file)


async def speaker(ctx, reading_queue):
    """
    Processes the queue of audio files and plays them.
    """
    loop = asyncio.get_running_loop()
    with concurrent.futures.ThreadPoolExecutor() as pool:
        while ctx.talking:
            audio_file = await reading_queue.get()
            if audio_file is None:
                logging.debug("Done playing the story.")
                break

            def speak():
                ctx.leds.stop()
                utils.play_audio_file(audio_file, ctx.sound_driver)

            await loop.run_in_executor(pool, speak)


async def run_story_loop(ctx, query=None, terminate=False):
    """
    The main loop for running the story.
    """
    ctx.talking = True
    ctx.leds.start()

    story_queue = asyncio.Queue()
    reading_queue = asyncio.Queue()

    writer_task = asyncio.create_task(writer(ctx, story_queue, query))
    reader_task = asyncio.create_task(reader(ctx, story_queue, reading_queue))
    speaker_task = asyncio.create_task(speaker(ctx, reading_queue))

    await asyncio.gather(writer_task, reader_task, speaker_task)

    ctx.leds.stop()
    ctx.talking = False

    if terminate:
        ctx.running = False


def tell_story(ctx, query=None, terminate=False):
    """
    Forks off a thread to tell the story.
    """

    def tell_story_wrapper():
        asyncio.run(run_story_loop(ctx, query, terminate))

    threading.Thread(target=tell_story_wrapper).start()


def main(ctx, query=None):
    """
    The main Fably loop.
    """

    ctx.stt_client = openai.Client(base_url=ctx.stt_url, api_key=ctx.api_key, )
    ctx.llm_client = openai.AsyncClient(base_url=ctx.llm_url, api_key=ctx.api_key)
    ctx.tts_client = openai.AsyncClient(base_url=ctx.tts_url, api_key=ctx.api_key)

    # Handle direct story continuation via CLI
    if hasattr(ctx, 'continue_story') and ctx.continue_story:
        # Find story to continue by name or topic
        story_path = None
        
        # First try exact directory name match
        potential_path = ctx.stories_path / ctx.continue_story
        if potential_path.exists() and potential_path.is_dir():
            story_path = potential_path
        else:
            # Try topic-based search
            matching_stories = utils.find_stories_by_topic(ctx.stories_path, ctx.continue_story, max_results=1)
            if matching_stories:
                story_path = matching_stories[0]
        
        if story_path:
            query = f"continue the story about {ctx.continue_story}"
            logging.info(f"Continuing story via CLI: {story_path.name}")
        else:
            logging.error(f"Story not found for continuation: {ctx.continue_story}")
            return

    # If a query is not present, introduce ourselves
    if not query:
        ctx.recognizer = utils.get_speech_recognizer(ctx.models_path, ctx.sound_model)
        
        # Calibrate noise floor if noise reduction is enabled
        if getattr(ctx, 'noise_reduction', False):
            if getattr(ctx, 'auto_calibrate', False):
                logging.info("Auto-calibrating noise floor...")
                utils.play_sound("calibrating", audio_driver=ctx.sound_driver, fallback_silent=True)
                ctx.noise_floor = utils.calibrate_noise_floor(
                    duration=getattr(ctx, 'calibration_duration', 3.0)
                )
            else:
                # Use a default noise floor if not auto-calibrating
                ctx.noise_floor = 0.01
                logging.info(f"Using default noise floor: {ctx.noise_floor}")
        else:
            ctx.noise_floor = None

    if ctx.loop and (Button or (hasattr(ctx, 'wakeword_engine') and ctx.wakeword_engine)):
        ctx.leds.start()
        utils.play_sound("startup", audio_driver=ctx.sound_driver)

        # Let's introduce ourselves
        utils.play_sound("hi", audio_driver=ctx.sound_driver)

        # Initialize wakeword detector if enabled
        wakeword_detector = None
        if hasattr(ctx, 'wakeword_engine') and ctx.wakeword_engine and hasattr(ctx, 'wakeword_model') and ctx.wakeword_model:
            try:
                wakeword_detector = create_wakeword_detector(
                    engine=ctx.wakeword_engine,
                    model_path=ctx.wakeword_model,
                    sensitivity=getattr(ctx, 'wakeword_sensitivity', 0.5)
                )
                
                def on_wakeword_detected():
                    if not ctx.talking:
                        logging.info("Wakeword detected! Starting story...")
                        tell_story(ctx, terminate=False)
                
                wakeword_detector.start_listening(on_wakeword_detected)
                logging.info(f"Wakeword detection active ({ctx.wakeword_engine})")
                
            except Exception as e:
                logging.error(f"Failed to initialize wakeword detector: {e}")
                wakeword_detector = None

        # Enhanced GPIO button functionality
        if Button and (not wakeword_detector or getattr(ctx, 'gpio_button', False)):
            def pressed(ctx):
                ctx.press_time = time.time()
                logging.debug("Button pressed")

            def released(ctx):
                release_time = time.time()
                pressed_for = release_time - ctx.press_time
                logging.debug("Button released after %f seconds", pressed_for)

                if pressed_for < ctx.button.hold_time:
                    if not ctx.talking:
                        logging.info("Button press - telling a story...")
                        tell_story(ctx, terminate=False)
                        logging.debug("Forked the storytelling thread")
                    else:
                        logging.debug("Button press ignored - already telling a story")

            def held(ctx):
                logging.info("Button held - shutting down...")
                if wakeword_detector:
                    wakeword_detector.stop_listening()
                ctx.running = False

            ctx.button = Button(pin=ctx.button_gpio_pin, hold_time=ctx.hold_time)
            ctx.button.when_pressed = lambda: pressed(ctx)
            ctx.button.when_released = lambda: released(ctx)
            ctx.button.when_held = lambda: held(ctx)

            # Add voice cycling functionality if enabled
            if hasattr(ctx, 'voice_cycle') and ctx.voice_cycle:
                try:
                    from fably.cli import add_voice_cycling_to_button_handler
                    add_voice_cycling_to_button_handler(ctx)
                    logging.info("Voice cycling enabled - double-tap button to change voice")
                except Exception as e:
                    logging.warning(f"Failed to enable voice cycling: {str(e)}")

            logging.info("GPIO button active on pin %d", ctx.button_gpio_pin)

        # Give instructions based on input method
        if wakeword_detector:
            utils.play_sound("instructions_wakeword", audio_driver=ctx.sound_driver, fallback_text="Say the wakeword to start")
        else:
            utils.play_sound("instructions", audio_driver=ctx.sound_driver)

        # Stop the LEDs once we're ready
        ctx.leds.stop()
        
        # Keep the main thread running and handle cleanup
        try:
            while ctx.running:
                time.sleep(1.0)
        finally:
            if wakeword_detector:
                wakeword_detector.stop_listening()
    else:
        # Here the query can be None, but it's ok.
        # We will record one from the user in that case.
        tell_story(ctx, query=query, terminate=True)

    # Keep the main thread from existing until we're done.
    while ctx.running:
        time.sleep(1.0)

    utils.play_sound("bye", audio_driver=ctx.sound_driver)
    logging.debug("Shutting down... bye!")
