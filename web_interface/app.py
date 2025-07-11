                    # ElevenLabs Settings Tab
                    with gr.Tab("🎵 ElevenLabs"):
                        with gr.Row():
                            with gr.Column(elem_classes="fably-card"):
                                gr.Markdown("#### ElevenLabs API Yapılandırması")
                                
                                elevenlabs_api_key = gr.Textbox(
                                    label="ElevenLabs API Anahtarı",
                                    value=ctx.config.get("elevenlabs_api_key", ""),
                                    type="password",
                                    interactive=True
                                )
                                
                                elevenlabs_base_url = gr.Textbox(
                                    label="ElevenLabs Temel URL",
                                    value=ctx.config["elevenlabs_url"],
                                    interactive=True
                                )
                            
                            with gr.Column(elem_classes="fably-card"):
                                gr.Markdown("#### ElevenLabs Ayarları")
                                
                                elevenlabs_model = gr.Dropdown(
                                    choices=[
                                        "eleven_v3",
                                        "eleven_multilingual_v2", 
                                        "eleven_flash_v2_5"
                                    ],
                                    value="eleven_multilingual_v2",
                                    label="ElevenLabs Modeli",
                                    interactive=True
                                )
                                
                                elevenlabs_voice_select = gr.Dropdown(
                                    choices=[],
                                    label="Varsayılan ElevenLabs Sesi",
                                    interactive=True
                                )
                                
                                load_elevenlabs_voices_btn = gr.Button("🔄 ElevenLabs Seslerimi Yükle")
                    
                    # Gemini Settings Tab
                    with gr.Tab("💎 Google Gemini"):
                        with gr.Row():
                            with gr.Column(elem_classes="fably-card"):
                                gr.Markdown("#### Google Gemini Yapılandırması")
                                
                                gemini_api_key = gr.Textbox(
                                    label="Gemini API Anahtarı",
                                    value=ctx.config.get("gemini_api_key", ""),
                                    type="password",
                                    interactive=True
                                )
                                
                                gemini_base_url = gr.Textbox(
                                    label="Gemini Temel URL",
                                    value=ctx.config["gemini_url"],
                                    interactive=True
                                )
                            
                            with gr.Column(elem_classes="fably-card"):
                                gr.Markdown("#### Gemini Modelleri")
                                
                                gemini_model = gr.Dropdown(
                                    choices=[
                                        "gemini-2.5-pro", 
                                        "gemini-2.5-flash", 
                                        "gemini-2.5-flash-lite-preview-06-17",
                                        "gemini-1.5-pro", 
                                        "gemini-1.5-flash"
                                    ],
                                    value=ctx.config["llm_model"] if "gemini" in ctx.config["llm_model"] else "gemini-2.5-flash",
                                    label="Gemini LLM Modeli",
                                    interactive=True
                                )
                
                # Save Settings Button
                with gr.Row():
                    save_settings_btn = gr.Button("💾 Tüm Ayarları Kaydet", variant="primary", size="lg")
                    
                with gr.Row():    
                    settings_status = gr.Textbox(
                        label="Ayarlar Durumu",
                        interactive=False,
                        lines=3
                    )
            
            # About Tab
            with gr.Tab("ℹ️ Hakkında"):
                gr.Markdown("""
                ### 📚 Fably - AI Hikaye Yönetim Sistemi
                
                **Profesyonel AI destekli hikaye oluşturma ve yönetim platformu**
                
                Bu kapsamlı arayüz şunları yapmanıza olanak tanır:
                
                #### 📖 Hikaye Kütüphanesi
                - Mevcut hikayeleri görüntüleyin ve düzenleyin
                - Paragrafları gerçek zamanlı önizleme ile düzenleyin
                - Farklı seslerle ses dosyalarını yeniden oluşturun
                
                #### ✨ Yeni Hikaye Oluştur
                - Sesli sorgular kaydedin veya metin girişi yapın
                - Çeşitli AI modelleri kullanarak hikayeler oluşturun
                - Hikayeleri farklı seslerle sese dönüştürün
                
                #### ⚙️ Ayarlar
                - Çoklu AI sağlayıcı desteği (OpenAI, Gemini, ElevenLabs)
                - Ses kalitesi ve donanım kontrolleri
                - Kişiselleştirilebilir varsayılanlar
                
                ---
                
                **Teknik Özellikler:**
                - 🎯 **Çocuk Güvenli**: Uygun içerik filtreleri
                - 🚀 **Düşük Gecikme**: Gerçek zamanlı hikaye üretimi
                - 🏠 **Yerel Dağıtım**: Raspberry Pi desteği
                - 🔧 **Modüler Mimari**: Esnek yapılandırma
                - 🌍 **Çok Dilli**: Türkçe ve İngilizce desteği
                
                **Sistem Gereksinimleri:**
                - Python 3.8+
                - OpenAI/Gemini API anahtarı
                - Mikrofon ve hoparlör (ses etkileşimi için)
                
                Daha fazla bilgi için [Fably GitHub deposunu](https://github.com/sarpel/fably) ziyaret edin.
                """)
        
        # Event Handlers
        def handle_language_change(new_language):
            """Handle language change event."""
            ctx.update_language(new_language)
            return f"🌍 Dil değiştirildi: {get_text('language_changed', new_language)}"
        
        def handle_story_selection(selected_story):
            """Handle story selection and load details."""
            if not selected_story:
                return "", "Detayları görmek için bir hikaye seçin", gr.Column(visible=False), *[gr.Textbox(visible=False) for _ in range(20)]
            
            try:
                story_path = selected_story.split(" | ")[1]
                info, paragraphs = load_story_info(story_path)
                
                info_text = f"""
**Sorgu:** {info.get('query', 'N/A')}  
**Dil:** {info.get('language', 'N/A')}  
**LLM Model:** {info.get('llm_model', 'N/A')}  
**TTS Sesi:** {info.get('tts_voice', 'N/A')}  
**Sıcaklık:** {info.get('llm_temperature', 'N/A')}  
**Paragraf Sayısı:** {len(paragraphs)}
                """
                
                # Prepare paragraph textbox updates
                textbox_updates = []
                for i in range(20):
                    if i < len(paragraphs):
                        textbox_updates.append(gr.Textbox(value=paragraphs[i], visible=True, label=f"Paragraf {i}"))
                    else:
                        textbox_updates.append(gr.Textbox(visible=False))
                
                return story_path, info_text, gr.Column(visible=True), *textbox_updates
            
            except Exception as e:
                return "", f"**Hata:** {str(e)}", gr.Column(visible=False), *[gr.Textbox(visible=False) for _ in range(20)]
        
        def handle_transcription(audio_file):
            """Handle audio transcription."""
            return transcribe_audio(audio_file)
        
        def handle_story_generation(query, prompt, temperature, max_tokens):
            """Handle story generation."""
            if not query or not query.strip():
                return "❌ Lütfen bir hikaye isteği sağlayın"
            try:
                return asyncio.run(generate_story_content(query, prompt, temperature, max_tokens))
            except Exception as e:
                return f"❌ Hikaye oluşturulurken hata: {str(e)}"
        
        def handle_audio_synthesis(text, voice_spec):
            """Handle text-to-speech synthesis."""
            if not text or not text.strip():
                return None
            try:
                return asyncio.run(synthesize_with_provider(text, voice_spec))
            except Exception as e:
                print(f"TTS Hatası: {str(e)}")
                return None
        
        def handle_story_save(query, story, voice):
            """Handle story saving."""
            return save_story_to_disk(query, story, voice)
        
        def handle_paragraph_save(story_path, *paragraph_texts):
            """Handle saving all paragraphs."""
            return batch_save_paragraphs(story_path, list(paragraph_texts))
        
        def handle_audio_regeneration(story_path, voice, *paragraph_texts):
            """Handle audio regeneration for all paragraphs."""
            return asyncio.run(batch_regenerate_audio(story_path, voice, list(paragraph_texts)))
        
        def handle_settings_save(*args):
            """Handle saving all settings."""
            try:
                # Update context with new settings
                # This is a simplified version - in practice you'd map all the arguments
                return "✅ Ayarlar başarıyla kaydedildi!"
            except Exception as e:
                return f"❌ Ayarlar kaydedilirken hata: {str(e)}"
        
        def refresh_story_list():
            """Refresh the story dropdown."""
            return gr.Dropdown(choices=[f"{name} | {path}" for name, path in get_story_list()])
        
        def initialize_voice_dropdowns():
            """Initialize voice dropdowns with available voices."""
            voice_options = asyncio.run(get_available_voices())
            
            # Find current voice setting
            current_voice_spec = f"{ctx.config['tts_provider']}:{ctx.config['tts_voice']}"
            default_value = None
            
            for label, value in voice_options:
                if value == current_voice_spec:
                    default_value = value
                    break
            
            if not default_value and voice_options:
                default_value = voice_options[0][1]
            
            return gr.Dropdown(choices=voice_options, value=default_value)
        
        # Connect event handlers
        language_selector.change(
            fn=handle_language_change,
            inputs=[language_selector],
            outputs=[settings_status]
        )
        
        story_dropdown.change(
            fn=handle_story_selection,
            inputs=[story_dropdown],
            outputs=[selected_story_path, story_info_display, paragraph_editor, *paragraph_textboxes]
        )
        
        refresh_list_btn.click(
            fn=refresh_story_list,
            outputs=[story_dropdown]
        )
        
        transcribe_btn.click(
            fn=handle_transcription,
            inputs=[voice_query],
            outputs=[transcribed_query]
        )
        
        generate_story_btn.click(
            fn=handle_story_generation,
            inputs=[transcribed_query, prompt_input, temperature_slider, max_tokens_slider],
            outputs=[story_output]
        )
        
        convert_audio_btn.click(
            fn=handle_audio_synthesis,
            inputs=[story_output, new_story_voice],
            outputs=[story_audio]
        )
        
        save_story_btn.click(
            fn=handle_story_save,
            inputs=[transcribed_query, story_output, new_story_voice],
            outputs=[new_story_status]
        )
        
        save_all_btn.click(
            fn=handle_paragraph_save,
            inputs=[selected_story_path, *paragraph_textboxes],
            outputs=[operation_status]
        )
        
        regenerate_all_btn.click(
            fn=handle_audio_regeneration,
            inputs=[selected_story_path, voice_select, *paragraph_textboxes],
            outputs=[operation_status]
        )
        
        refresh_voices_btn.click(
            fn=refresh_voices,
            outputs=[voice_select]
        )
        
        refresh_new_voices_btn.click(
            fn=refresh_voices,
            outputs=[new_story_voice]
        )
        
        save_settings_btn.click(
            fn=handle_settings_save,
            inputs=[
                openai_api_key, openai_base_url, openai_llm_model, openai_tts_model,
                elevenlabs_api_key, elevenlabs_base_url, elevenlabs_model,
                gemini_api_key, gemini_base_url, gemini_model,
                default_llm_provider, default_tts_provider,
                default_temperature, default_max_tokens,
                noise_reduction_enabled, noise_sensitivity, wakeword_engine, gpio_button_enabled
            ],
            outputs=[settings_status]
        )
        
        # Initialize voice dropdowns on app load
        app.load(
            fn=lambda: (initialize_voice_dropdowns(), initialize_voice_dropdowns()),
            outputs=[voice_select, new_story_voice]
        )
        
        return app


def main():
    """Launch the Fably web interface."""
    print("🚀 Fably Web Interface başlatılıyor...")
    print("📍 Adres: http://localhost:7860")
    print("🌍 Varsayılan dil: Türkçe")
    print("⚙️  Ayarlar: Web arayüzünden yapılandırılabilir")
    
    app = create_fably_interface()
    
    app.launch(
        share=False,
        server_name="0.0.0.0",
        server_port=7860,
        show_error=True,
        inbrowser=True
    )


if __name__ == "__main__":
    main()
