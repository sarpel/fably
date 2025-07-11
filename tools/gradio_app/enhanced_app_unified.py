_list = get_story_list()
        total_stories = len(stories_list)
        total_paragraphs = 0
        voice_counts = {}
        recent_stories = []
        
        for name, path in stories_list:
            story_path = Path(path)
            
            # Count paragraphs
            paragraphs = list(story_path.glob("paragraph_*.txt"))
            total_paragraphs += len(paragraphs)
            
            # Get voice info
            info_file = story_path / "info.yaml"
            if info_file.exists():
                try:
                    with open(info_file, 'r') as f:
                        info = yaml.safe_load(f)
                    voice = info.get('tts_voice', 'unknown')
                    voice_counts[voice] = voice_counts.get(voice, 0) + 1
                    
                    # Check if recent (last 7 days)
                    import time
                    if story_path.stat().st_mtime > time.time() - (7 * 24 * 3600):
                        recent_stories.append(name)
                except:
                    pass
        
        # Generate HTML stats with current language
        stats_html = f"""
        <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 10px 0;">
            <h4>📊 {_('quick_stats')}</h4>
            <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin-top: 10px;">
                <div><strong>Total Stories:</strong> {total_stories}</div>
                <div><strong>Total Paragraphs:</strong> {total_paragraphs}</div>
                <div><strong>Recent Stories:</strong> {len(recent_stories)}</div>
                <div><strong>Avg Paragraphs:</strong> {total_paragraphs // total_stories if total_stories > 0 else 0}</div>
            </div>
            
            <h5 style="margin-top: 15px;">🎵 Voice Usage</h5>
            <div style="font-size: 0.9em;">
        """
        
        for voice, count in sorted(voice_counts.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total_stories * 100) if total_stories > 0 else 0
            stats_html += f"<div>{voice}: {count} stories ({percentage:.1f}%)</div>"
        
        stats_html += """
            </div>
        </div>
        """
        
        return stats_html
    
    except Exception as e:
        return f"<div style='color: #dc3545; padding: 10px; background: #f8d7da; border-radius: 5px;'>Error generating statistics: {str(e)}</div>"


def filter_story_collection(search_query: str, category: str, voice_filter: str) -> str:
    """Filter and display story collection based on criteria."""
    try:
        stories_list = get_story_list()
        filtered_stories = []
        
        for name, path in stories_list:
            story_path = Path(path)
            include_story = True
            
            # Apply search filter
            if search_query and search_query.strip():
                query_lower = search_query.lower().strip()
                if query_lower not in name.lower():
                    # Check story content
                    found_in_content = False
                    for para_file in story_path.glob("paragraph_*.txt"):
                        try:
                            content = para_file.read_text().lower()
                            if query_lower in content:
                                found_in_content = True
                                break
                        except:
                            pass
                    if not found_in_content:
                        include_story = False
            
            # Apply category filter
            if include_story and category != _('all_categories'):
                if category == _('recent'):
                    import time
                    if story_path.stat().st_mtime <= time.time() - (7 * 24 * 3600):
                        include_story = False
                elif category == _('long_stories'):
                    paragraph_count = len(list(story_path.glob("paragraph_*.txt")))
                    if paragraph_count < 7:
                        include_story = False
                elif category == _('short_stories'):
                    paragraph_count = len(list(story_path.glob("paragraph_*.txt")))
                    if paragraph_count >= 7:
                        include_story = False
            
            # Apply voice filter
            if include_story and voice_filter != _('all_voices'):
                info_file = story_path / "info.yaml"
                if info_file.exists():
                    try:
                        with open(info_file, 'r') as f:
                            info = yaml.safe_load(f)
                        story_voice = info.get('tts_voice', '')
                        if story_voice != voice_filter:
                            include_story = False
                    except:
                        include_story = False
                else:
                    include_story = False
            
            if include_story:
                filtered_stories.append((name, path))
        
        # Generate HTML for filtered stories
        if not filtered_stories:
            return f"<div style='color: #6c757d; padding: 10px;'>{_('no_story_selected')}</div>"
        
        html_content = f"""
        <div style="max-height: 400px; overflow-y: auto;">
            <h5>📖 Found {len(filtered_stories)} stories</h5>
        """
        
        for name, path in filtered_stories[:20]:  # Limit to 20 for performance
            story_path = Path(path)
            paragraph_count = len(list(story_path.glob("paragraph_*.txt")))
            
            # Get story info
            info_file = story_path / "info.yaml"
            voice_info = "Unknown"
            query_info = "Unknown"
            if info_file.exists():
                try:
                    with open(info_file, 'r') as f:
                        info = yaml.safe_load(f)
                    voice_info = info.get('tts_voice', 'Unknown')
                    query_info = info.get('query', 'Unknown')[:100] + "..." if len(info.get('query', '')) > 100 else info.get('query', 'Unknown')
                except:
                    pass
            
            html_content += f"""
            <div style="border: 1px solid #dee2e6; padding: 10px; margin: 5px 0; border-radius: 5px; background: #ffffff;">
                <div style="font-weight: bold; color: #495057;">{name}</div>
                <div style="font-size: 0.9em; color: #6c757d; margin: 5px 0;">
                    Query: {query_info}
                </div>
                <div style="font-size: 0.8em; color: #868e96;">
                    {paragraph_count} {_('paragraphs')} • Voice: {voice_info}
                </div>
            </div>
            """
        
        if len(filtered_stories) > 20:
            html_content += f"<div style='text-align: center; padding: 10px; color: #6c757d;'>... and {len(filtered_stories) - 20} more stories</div>"
        
        html_content += "</div>"
        return html_content
    
    except Exception as e:
        return f"<div style='color: #dc3545; padding: 10px; background: #f8d7da; border-radius: 5px;'>Error filtering stories: {str(e)}</div>"


if __name__ == "__main__":
    # Launch the unified enhanced Gradio interface
    app = create_gradio_interface()
    app.launch(
        share=False,
        server_name="0.0.0.0",
        server_port=7860,
        show_error=True
    )
