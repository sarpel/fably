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
                    
                    **Teknik Özellikler:**
                    - 🎯 **Çocuk Güvenli**: Uygun içerik filtreleri
                    - 🚀 **Düşük Gecikme**: Gerçek zamanlı hikaye üretimi
                    - 🏠 **Yerel Dağıtım**: Raspberry Pi desteği
                    - 🔧 **Modüler Mimari**: Esnek yapılandırma
                    - 🌍 **Çok Dilli**: Türkçe ve İngilizce desteği
                    - 🎨 **Dark Theme**: Göz yormayan arayüz
                    """)
        
        # Dummy event handlers (these would be implemented with actual functionality)
        def handle_language_change(new_language):
            return f"Dil değiştirildi: {new_language}"
        
        def handle_story_selection(selected_story):
            return "", "Detayları görmek için bir hikaye seçin"
        
        def handle_transcription(audio_file):
            return "Transkript: [Ses dosyası işlendi]"
        
        def handle_story_generation(query, prompt, temperature, max_tokens):
            return "Hikaye başarıyla oluşturuldu!"
        
        def handle_settings_save(*args):
            return "Ayarlar başarıyla kaydedildi!"
        
        # Connect basic event handlers
        language_selector.change(
            fn=handle_language_change,
            inputs=[language_selector],
            outputs=[settings_status]
        )
        
        story_dropdown.change(
            fn=handle_story_selection,
            inputs=[story_dropdown],
            outputs=[selected_story_path, story_info_display]
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
        
        return app

def main():
    """Launch the enhanced Fably interface with dark theme"""
    print("🚀 Fably Enhanced Web Interface (Dark Theme) başlatılıyor...")
    print("📍 Adres: http://localhost:7860")
    print("🎨 Dark Theme aktif - Component ID'leri 11, 16, 54, 63, 82, 87 düzeltildi")
    print("⚙️ Tüm ayar sekmelerinde dark background uygulandı")
    
    app = create_gradio_interface()
    
    app.launch(
        share=False,
        server_name="0.0.0.0",
        server_port=7860,
        show_error=True,
        inbrowser=True
    )

if __name__ == "__main__":
    main()
