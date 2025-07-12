"""
Main Fably logic (cleaned for Gemini LLM and ElevenLabs TTS only).
"""

import asyncio
import concurrent.futures
import logging
import shutil
import time
import threading
from fably import utils

# --- LLM and TTS provider usage should be via ctx.llm_client and ctx.tts_service (abstraction) ---

def generate_story(ctx, query, prompt):
    """
    Generates a story stream based on a given query and prompt using the LLM API and persists the information
    about the models used to generate the story to a file.
    """
    completion_params = {
        "stream": True,
        "model": ctx.llm_model,
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": query},
        ],
    }
    # Gemini models: use max_tokens and temperature if supported
    completion_params["max_tokens"] = ctx.max_tokens
    completion_params["temperature"] = ctx.temperature
    return ctx.llm_client.chat.completions.create(**completion_params)


async def synthesize_audio(ctx, story_path, index, text=None):
    """
    Fetches TTS audio for a given paragraph of a story and saves it to a file.
    Uses the TTS service abstraction for multi-provider support.
    """
    logging.debug("Synthesizing audio for paragraph %i...", index)
    audio_file_path = story_path / f"paragraph_{index}.{ctx.tts_format}"
    if audio_file_path.exists():
        logging.debug("Paragraph %i audio already exists at %s", index, audio_file_path)
        return audio_file_path
    if not text:
        text_file_path = story_path / f"paragraph_{index}.txt"
        if text_file_path.exists():
            logging.debug("Reading paragraph %i text from %s ...", index, text_file_path)
            text = utils.read_from_file(text_file_path)
        else:
            raise ValueError(f"No text found for paragraph {index} in {story_path}")
    # Use the TTS service abstraction
    await ctx.tts_service.synthesize(
        text=text,
        voice=ctx.tts_voice,
        provider=getattr(ctx, 'tts_provider', 'elevenlabs'),
        output_file=audio_file_path,
        format=ctx.tts_format,
        model=ctx.tts_model
    )
    logging.debug("Saved audio for paragraph %i to %s", index, audio_file_path)
    return audio_file_path


async def writer(ctx, story_queue, query=None):
    """
    Creates a story based on a textual query or story request.
    """
    if query:
        query_local = "n/a"
    elif hasattr(ctx, 'story_request') and ctx.story_request:
        query = f"bana {ctx.story_request} hakkında bir hikaye anlat"
        query_local = "story_request"
        logging.info("Story request: %s", ctx.story_request)
    else:
        raise RuntimeError("No query provided and no story_request set.")
    # Check if this is a continuation query
    is_continuation = utils.is_continuation_query(query, ctx.continuation_patterns)
    # Handle story continuation
    if is_continuation:
        continue_story_path = utils.find_story_for_continuation(
            ctx.stories_path, query, ctx.continuation_patterns
        )
        if not continue_story_path:
            logging.warning("No existing story found to continue")
            await story_queue.put(None)
            return
        story_path = continue_story_path
        story_context = utils.extract_story_context(story_path, max_paragraphs=10)
        starting_paragraph_index = utils.get_next_paragraph_index(story_path)
        logging.info(f"Continuing story '{story_context['original_query']}' from paragraph %i", starting_paragraph_index)
        for index in range(story_context['paragraph_count']):
            await story_queue.put((story_path, index, None))
    else:
        story_path = ctx.stories_path / utils.query_to_filename(query, prefix="")
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
        logging.debug("Reading prompt...")
        base_prompt = utils.read_from_file(ctx.prompt_file)
        if is_continuation and story_context:
            continuation_context = "\n\n".join(story_context['paragraphs'])
            prompt = f"{base_prompt}\n\nYou are continuing an existing story. Here is what has happened so far:\n\nOriginal request: {story_context['original_query']}\n\nStory so far:\n{continuation_context}\n\nNow continue this story based on the user's request: {query}"
        else:
            prompt = base_prompt
        story_stream = await generate_story(ctx, query, prompt)
        index = starting_paragraph_index
        paragraph = []
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
    Processes the queue of paragraphs and sends them off to be read and synthezized into audio files.
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
                utils.play_audio_file(audio_file)
            await loop.run_in_executor(pool, speak)


async def run_story_loop(ctx, query=None, terminate=False):
    """
    The main loop for running the story.
    """
    ctx.talking = True
    story_queue = asyncio.Queue()
    reading_queue = asyncio.Queue()
    writer_task = asyncio.create_task(writer(ctx, story_queue, query))
    reader_task = asyncio.create_task(reader(ctx, story_queue, reading_queue))
    speaker_task = asyncio.create_task(speaker(ctx, reading_queue))
    await asyncio.gather(writer_task, reader_task, speaker_task)
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
    The main Fably loop (cleaned).
    """
    # LLM and TTS clients must be set up in ctx externally (Gemini, ElevenLabs)
    # No hardware, STT, or OpenAI logic remains
    if hasattr(ctx, 'continue_story') and ctx.continue_story:
        story_path = None
        potential_path = ctx.stories_path / ctx.continue_story
        if potential_path.exists() and potential_path.is_dir():
            story_path = potential_path
        else:
            matching_stories = utils.find_stories_by_topic(ctx.stories_path, ctx.continue_story, max_results=1)
            if matching_stories:
                story_path = matching_stories[0]
        if story_path:
            query = f"continue the story about {ctx.continue_story}"
            logging.info(f"Continuing story via CLI: {story_path.name}")
        else:
            logging.error(f"Story not found for continuation: {ctx.continue_story}")
            return
    if not query:
        raise RuntimeError("No query provided and no story_request set.")
    tell_story(ctx, query=query, terminate=True)
    while ctx.running:
        time.sleep(1.0)
    logging.debug("Shutting down... bye!")
