"""
Localization system for Fably Enhanced Web Interface
Supports Turkish and English with Turkish as default
"""

# Language translations dictionary
TRANSLATIONS = {
    'tr': {
        # Main interface
        'title': '📚 Sarpy - AI Hikaye Anlatıcısı Yönetim Arayüzü',
        'subtitle': '*Kapsamlı hikaye oluşturma, düzenleme ve ses üretimi*',
        
        # Tab names
        'tab_story_library': '📖 Hikaye Kütüphanesi',
        'tab_create_story': '✨ Yeni Hikaye Oluştur',
        'tab_settings': '⚙️ Ayarlar',
        'tab_collections': '📚 Koleksiyonlar',
        'tab_about': 'ℹ️ Hakkında',
        
        # Story Library tab
        'library_header': 'Mevcut Hikayeleri Göz At ve Düzenle',
        'select_story': 'Hikaye Seç',
        'refresh_list': '🔄 Listeyi Yenile',
        'story_details': '*Detayları görmek için bir hikaye seçin*',
        'edit_paragraphs': 'Paragrafları Düzenle',
        'tts_voice': 'TTS Sesi',
        'refresh_voices': '🔄 Sesleri Yenile',
        'save_all_changes': '💾 Tüm Değişiklikleri Kaydet',
        'regenerate_all_audio': '🎵 Tüm Sesleri Yeniden Oluştur',
        'continue_story': '📖 Hikayeyi Devam Ettir',
        'story_continuation': 'Hikaye Devamı',
        'continuation_desc': 'Bu hikayeye devam paragrafları ekle',
        'continuation_request': 'Devam İsteği',
        'continuation_placeholder': 'Hikaye nasıl devam etmeli? (örn: "Prenses ejderle karşılaştığında ne olur?")',
        'new_paragraphs': 'Yeni paragraf sayısı',
        'voice_for_new': 'Yeni paragraflar için ses',
        'generate_continuation': '✨ Devamını Oluştur',
        'status': 'Durum',
        
        # Create Story tab
        'create_header': 'Yeni Hikayeler Oluştur ve Üret',
        'voice_query': '🎤 Sesli Sorgu',
        'query_placeholder': 'Veya hikaye isteğinizi doğrudan yazın...',
        'creativity_temp': '🌡️ Yaratıcılık (Sıcaklık)',
        'max_length': '📏 Maksimum Uzunluk (Token)',
        'story_prompt': '📋 Hikaye Üretim İstemi',
        'generate_story': '✨ Hikaye Oluştur',
        'generated_story': '📖 Oluşturulan Hikaye',
        'story_placeholder': 'Oluşturulan hikayeniz burada görünecek...',
        'convert_to_audio': '🎵 Sese Çevir',
        'save_story': '💾 Hikayeyi Kaydet',
        'story_audio': '🔊 Hikaye Sesi',
        
        # Settings tab
        'settings_header': 'Sağlayıcı Yapılandırma Ayarları',
        'settings_desc': '*Farklı AI servis sağlayıcılarını ayrı ayrı yapılandırın*',
        
        # ElevenLabs settings
        'elevenlabs_config': 'ElevenLabs API Yapılandırması',
        'elevenlabs_api_key': 'ElevenLabs API Anahtarı',
        'elevenlabs_base_url': 'ElevenLabs Temel URL',
        'elevenlabs_settings': 'ElevenLabs Ayarları',
        'elevenlabs_model': 'ElevenLabs Modeli',
        'default_elevenlabs_voice': 'Varsayılan ElevenLabs Sesi',
        'load_voices': '🔄 ElevenLabs Seslerimi Yükle',
        'voice_quality_settings': 'Ses Kalitesi Ayarları',
        'stability': 'Kararlılık',
        'similarity_boost': 'Benzerlik Artırma',
        'elevenlabs_required': 'ElevenLabs sesleri için gerekli',
        'v2_recommended': 'Ses sentezi modeli (v2+ önerilir)',
        'account_voices': 'Hesabınızdan mevcut sesleri yükleyecek',
        'stability_info': 'Daha kararlı = daha az varyasyon',
        'similarity_info': 'Yüksek = orijinal sese daha yakın',
        
        # Gemini settings
        'gemini_config': 'Google Gemini Yapılandırması',
        'gemini_api_key': 'Gemini API Anahtarı',
        'gemini_base_url': 'Gemini Temel URL',
        'gemini_models': 'Gemini Modelleri',
        'gemini_llm_model': 'Gemini LLM Modeli',
        'gemini_tts_model': 'Gemini TTS Modeli',
        'default_gemini_voice': 'Varsayılan Gemini Ses Stili',
        'get_from_studio': 'Google AI Studio\'dan alın',
        'llm_for_stories': 'Hikaye üretimi için dil modeli',
        'tts_model_info': 'Metin-konuşma modeli',
        'voice_style_info': 'Gemini TTS için ses stili',
        
        # Custom Provider settings
        'custom_provider': 'Özel AI Sağlayıcı Kurulumu',
        'custom_desc': '*Herhangi bir OpenAI uyumlu API uç noktasını yapılandırın*',
        'provider_name': 'Sağlayıcı Adı',
        'provider_name_placeholder': 'Benim Özel LLM\'im',
        'provider_friendly_name': 'Bu sağlayıcı için dostane ad',
        'api_key': 'API Anahtarı',
        'custom_api_key_placeholder': 'özel-api-anahtarınız',
        'base_url': 'Temel URL',
        'base_url_placeholder': 'http://localhost:1234/v1',
        'full_endpoint_url': 'Tam API uç nokta URL\'si',
        'llm_model_id': 'Dil Modeli ID',
        'llm_model_placeholder': 'llama-3.1-8b-instruct',
        'model_identifier': 'Bu uç nokta için model tanımlayıcısı',
        'tts_model_optional': 'TTS Modeli ID (isteğe bağlı)',
        'test_connection': '🔍 Bağlantıyı Test Et',
        
        # Global Settings
        'global_settings': '🌐 Genel Ayarlar',
        'default_provider_selection': 'Varsayılan Sağlayıcı Seçimi',
        'default_llm_provider': 'Varsayılan Dil Modeli Sağlayıcısı',
        'llm_provider_info': 'Hikaye üretimi için hangi sağlayıcı kullanılacak',
        'default_tts_provider': 'Varsayılan TTS Sağlayıcısı',
        'tts_provider_info': 'Konuşma sentezi için hangi sağlayıcı kullanılacak',
        'story_generation_defaults': 'Hikaye Üretim Varsayılanları',
        'default_temperature': 'Varsayılan Sıcaklık',
        'temperature_info': 'Yaratıcılık seviyesi (0=odaklı, 2=çok yaratıcı)',
        'default_max_tokens': 'Varsayılan Maksimum Token',
        'max_tokens_info': 'Oluşturulan hikayelerin maksimum uzunluğu',
        'language': 'Dil',
        'language_placeholder': 'tr',
        'language_info': 'Hikayeler için dil kodu (tr, en, vb.)',
        'stories_directory': 'Hikayeler Dizini',
        'stories_dir_placeholder': './stories',
        'stories_dir_info': 'Hikayelerin kaydedildiği dizin',
        
        # Audio Quality Settings
        'enable_noise_reduction': 'Gürültü Azaltmayı Etkinleştir',
        'noise_reduction_info': 'Ses kaydı sırasında arka plan gürültüsünü filtrele',
        'noise_sensitivity': 'Gürültü Hassasiyeti',
        'noise_sensitivity_info': 'Yüksek değerler sessiz seslere daha duyarlı',
        
        # Action buttons
        'save_all_settings': '💾 Tüm Ayarları Kaydet',
        'settings_status': 'Ayarlar Durumu',
        
        # Collections tab
        'collections_header': 'Gelişmiş Hikaye Yönetimi ve Organizasyonu',
        'quick_stats': 'Hızlı İstatistikler',
        'refresh_stats': '🔄 İstatistikleri Yenile',
        'filters_search': 'Filtreler ve Arama',
        'search_stories': 'Hikayeleri Ara',
        'search_placeholder': 'Başlık, içerik veya konuya göre ara...',
        'category_filter': 'Kategori Filtresi',
        'voice_filter': 'Ses Filtresi',
        'apply_filters': '🔍 Filtreleri Uygula',
        'story_collection': 'Hikaye Koleksiyonu',
        'add_to_favorites': '⭐ Favorilere Ekle',
        'export_selected': '📤 Seçilenleri Dışa Aktar',
        'delete_selected': '🗑️ Seçilenleri Sil',
        
        # Status messages
        'no_story_selected': 'Hikaye seçilmedi',
        'invalid_story_selection': 'Geçersiz hikaye seçimi',
        'error_loading_story': 'Hikaye yüklenirken hata',
        'no_audio_provided': 'Ses dosyası sağlanmadı',
        'error_generating_story': 'Hikaye oluşturulurken hata',
        'error_speech_synthesis': 'Konuşma sentezi hatası',
        'please_provide_request': 'Lütfen bir hikaye isteği sağlayın',
        'openai_settings_saved': '✅ OpenAI ayarları kaydedildi',
        'elevenlabs_settings_saved': '✅ ElevenLabs ayarları kaydedildi',
        'global_settings_saved': '✅ Genel ayarlar başarıyla kaydedildi!',
        'all_settings_saved': '✅ Tüm ayarlar başarıyla kaydedildi! TTS servisleri güncellendi.',
        'api_key_missing': 'Lütfen önce ElevenLabs API anahtarını girin',
        'voices_loaded': 'ses yüklendi',
        'error_loading_voices': 'Sesler yüklenirken hata',
        'error_saving_settings': 'Ayarlar kaydedilirken hata',
        'paragraph_saved': 'paragraf kaydedildi',
        'error_saving_paragraph': 'Paragraf kaydedilirken hata',
        'audio_regenerated': 'için ses yeniden oluşturuldu',
        'error_regenerating_audio': 'Ses yeniden oluşturulurken hata',
        'story_saved_to': 'Hikaye şuraya kaydedildi',
        'paragraphs': 'paragraf',
        'error_saving_story': 'Hikaye kaydedilirken hata',
        'paragraphs_saved': 'paragraf başarıyla kaydedildi',
        'error_saving_paragraphs': 'Paragraflar kaydedilirken hata',
        'audio_regenerated_all': 'paragraf için ses yeniden oluşturuldu',
        'error_regenerating_all': 'Ses yeniden oluşturulurken hata',
        'continuation_generated': 'yeni paragraf hikayeyi devam ettiriyor!',
        'error_generating_continuation': 'Hikaye devamı oluşturulurken hata',
        
        # Collections
        'all_categories': 'Tümü',
        'favorites': 'Favoriler',
        'recent': 'Son Zamanlarda',
        'long_stories': 'Uzun Hikayeler',
        'short_stories': 'Kısa Hikayeler',
        'all_voices': 'Tüm Sesler',
        'favorites_coming_soon': '⭐ Favoriler özelliği yakında geliyor!',
        'export_coming_soon': '📤 Dışa aktarma özelliği yakında geliyor!',
        'delete_coming_soon': '🗑️ Silme özelliği yakında geliyor!',
        
        # About tab content
        'about_title': '📚 Sarpy - AI Hikaye Anlatıcısı Yönetim Arayüzü',
        'about_enhanced': '**Sarpy Hikaye Yönetimi için Gelişmiş Web Arayüzü**',
        'about_features': 'Bu kapsamlı arayüz şunları yapmanıza olanak tanır:',
        'about_library': '📖 Hikaye Kütüphanesi',
        'about_library_desc': '- Hikayeler dizininizden ve örneklerden mevcut hikayeleri göz atın\\n- Hikaye meta verilerini görüntüleyin (sorgu, kullanılan model, ses, vb.)\\n- Canlı önizleme ile bireysel paragrafları düzenleyin\\n- Farklı seslerle belirli paragraflar için sesi yeniden oluşturun',
        'about_create': '✨ Yeni Hikaye Oluştur',
        'about_create_desc': '- Sesli sorgular kaydedin veya metin istekleri yazın\\n- Üretim parametrelerini yapılandırın (sıcaklık, maksimum token)\\n- Çeşitli LLM modelleri kullanarak hikayeler oluşturun\\n- Hikayeleri seçilebilir seslerle sese dönüştürün\\n- Hikayeleri standart Sarpy formatında kaydedin',
        'about_settings': '⚙️ Ayarlar',
        'about_settings_desc': '- API uç noktalarını yapılandırın (OpenAI, yerel sunucular)\\n- Varsayılan modelleri ve sesleri ayarlayın\\n- Hikaye dizinlerini ve güvenlik ayarlarını yönetin',
        'about_project_features': '**Sarpy Proje Özellikleri:**',
        'about_child_safe': '- 🎯 **Çocuk Güvenli**: Yerleşik sorgu korumaları ve içerik filtreleme',
        'about_low_latency': '- 🚀 **Düşük Gecikme**: Hızlı yanıt için akış üretimi',
        'about_self_hostable': '- 🏠 **Kendi Sunucunuzda Barındırılabilir**: Ollama aracılığıyla yerel AI modelleri desteği',
        'about_modular': '- 🔧 **Modüler**: Yapılandırılabilir STT, LLM ve TTS servisleri',
        'about_hardware_ready': '- 📱 **Donanım Hazır**: Raspberry Pi dağıtımı için optimize edilmiş',
        'about_requirements': '**Sistem Gereksinimleri:**',
        'about_req_python': '- Python 3.8+',
        'about_req_api': '- OpenAI API anahtarı (veya yerel AI sunucu kurulumu)',
        'about_req_audio': '- Ses etkileşimi için mikrofon ve hoparlörler',
        'about_more_info': 'Daha fazla bilgi için [Sarpy GitHub deposunu](https://github.com/stefanom/fably) ziyaret edin.',
        
        # Voice options and model descriptions
        'voice_default': 'Varsayılan Ses',
        'voice_natural': 'Doğal Ses',
        'voice_professional': 'Profesyonel Ses',
        'voice_expressive': 'Anlatıcı Ses',
        
        # Language selector
        'language_selector': 'Arayüz Dili',
        'turkish': 'Türkçe',
        'english': 'English',
    },
    
    'en': {
        # Main interface
        'title': '📚 Sarpy - AI Storyteller Management Interface',
        'subtitle': '*Comprehensive story creation, editing, and audio generation*',
        
        # Tab names
        'tab_story_library': '📖 Story Library',
        'tab_create_story': '✨ Create New Story',
        'tab_settings': '⚙️ Settings',
        'tab_collections': '📚 Collections',
        'tab_about': 'ℹ️ About',
        
        # Story Library tab  
        'library_header': 'Browse and Edit Existing Stories',
        'select_story': 'Select Story',
        'refresh_list': '🔄 Refresh List',
        'story_details': '*Select a story to view details*',
        'edit_paragraphs': 'Edit Paragraphs',
        'tts_voice': 'TTS Voice',
        'refresh_voices': '🔄 Refresh Voices',
        'save_all_changes': '💾 Save All Changes',
        'regenerate_all_audio': '🎵 Regenerate All Audio',
        'continue_story': '📖 Continue Story',
        'story_continuation': 'Story Continuation',
        'continuation_desc': 'Generate additional paragraphs to continue this story',
        'continuation_request': 'Continuation Request',
        'continuation_placeholder': 'How should the story continue? (e.g., "What happens when the princess meets the dragon?")',
        'new_paragraphs': 'Number of new paragraphs',
        'voice_for_new': 'Voice for new paragraphs',
        'generate_continuation': '✨ Generate Continuation',
        'status': 'Status',
        
        # Create Story tab
        'create_header': 'Create and Generate New Stories',
        'voice_query': '🎤 Voice Query',
        'query_placeholder': 'Or type your story request directly...',
        'creativity_temp': '🌡️ Creativity (Temperature)',
        'max_length': '📏 Max Length (Tokens)',
        'story_prompt': '📋 Story Generation Prompt',
        'generate_story': '✨ Generate Story',
        'generated_story': '📖 Generated Story',
        'story_placeholder': 'Your generated story will appear here...',
        'convert_to_audio': '🎵 Convert to Audio',
        'save_story': '💾 Save Story',
        'story_audio': '🔊 Story Audio',
        
        # Settings tab
        'settings_header': 'Provider Configuration Settings',
        'settings_desc': '*Configure different AI service providers separately*',
        
        # ElevenLabs settings
        'elevenlabs_config': 'ElevenLabs API Configuration',
        'elevenlabs_api_key': 'ElevenLabs API Key',
        'elevenlabs_base_url': 'ElevenLabs Base URL',
        'elevenlabs_settings': 'ElevenLabs Settings',
        'elevenlabs_model': 'ElevenLabs Model',
        'default_elevenlabs_voice': 'Default ElevenLabs Voice',
        'load_voices': '🔄 Load My ElevenLabs Voices',
        'voice_quality_settings': 'Voice Quality Settings',
        'stability': 'Stability',
        'similarity_boost': 'Similarity Boost',
        'elevenlabs_required': 'Required for ElevenLabs voices',
        'v2_recommended': 'Voice synthesis model (v2+ recommended)',
        'account_voices': 'Will load available voices from your account',
        'stability_info': 'More stable = less variation',
        'similarity_info': 'Higher = closer to original voice',
        
        # Gemini settings
        'gemini_config': 'Google Gemini Configuration',
        'gemini_api_key': 'Gemini API Key',
        'gemini_base_url': 'Gemini Base URL',
        'gemini_models': 'Gemini Models',
        'gemini_llm_model': 'Gemini LLM Model',
        'gemini_tts_model': 'Gemini TTS Model',
        'default_gemini_voice': 'Default Gemini Voice Style',
        'get_from_studio': 'Get from Google AI Studio',
        'llm_for_stories': 'Language model for story generation',
        'tts_model_info': 'Text-to-speech model',
        'voice_style_info': 'Voice style for Gemini TTS',
        
        # Custom Provider settings
        'custom_provider': 'Custom AI Provider Setup',
        'custom_desc': '*Configure any OpenAI-compatible API endpoint*',
        'provider_name': 'Provider Name',
        'provider_name_placeholder': 'My Custom LLM',
        'provider_friendly_name': 'Friendly name for this provider',
        'api_key': 'API Key',
        'custom_api_key_placeholder': 'your-custom-api-key',
        'base_url': 'Base URL',
        'base_url_placeholder': 'http://localhost:1234/v1',
        'full_endpoint_url': 'Full API endpoint URL',
        'llm_model_id': 'Language Model ID',
        'llm_model_placeholder': 'llama-3.1-8b-instruct',
        'model_identifier': 'Model identifier for this endpoint',
        'tts_model_optional': 'TTS Model ID (optional)',
        'test_connection': '🔍 Test Connection',
        
        # Global Settings
        'global_settings': '🌐 Global Settings',
        'default_provider_selection': 'Default Provider Selection',
        'default_llm_provider': 'Default Language Model Provider',
        'llm_provider_info': 'Which provider to use for story generation',
        'default_tts_provider': 'Default TTS Provider',
        'tts_provider_info': 'Which provider to use for speech synthesis',
        'story_generation_defaults': 'Story Generation Defaults',
        'default_temperature': 'Default Temperature',
        'temperature_info': 'Creativity level (0=focused, 2=very creative)',
        'default_max_tokens': 'Default Max Tokens',
        'max_tokens_info': 'Maximum length of generated stories',
        'language': 'Language',
        'language_placeholder': 'tr',
        'language_info': 'Language code for stories (tr, en, etc.)',
        'stories_directory': 'Stories Directory',
        'stories_dir_placeholder': './stories',
        'stories_dir_info': 'Directory where stories are saved',
        
        # Audio Quality Settings
        'enable_noise_reduction': 'Enable Noise Reduction',
        'noise_reduction_info': 'Filter background noise during voice recording',
        'noise_sensitivity': 'Noise Sensitivity',
        'noise_sensitivity_info': 'Higher values are more sensitive to quiet sounds',
        
        # Action buttons
        'save_all_settings': '💾 Save All Settings',
        'settings_status': 'Settings Status',
        
        # Collections tab
        'collections_header': 'Advanced Story Management & Organization',
        'quick_stats': 'Quick Stats',
        'refresh_stats': '🔄 Refresh Stats',
        'filters_search': 'Filters & Search',
        'search_stories': 'Search Stories',
        'search_placeholder': 'Search by title, content, or topic...',
        'category_filter': 'Category Filter',
        'voice_filter': 'Voice Filter',
        'apply_filters': '🔍 Apply Filters',
        'story_collection': 'Story Collection',
        'add_to_favorites': '⭐ Add to Favorites',
        'export_selected': '📤 Export Selected',
        'delete_selected': '🗑️ Delete Selected',
        
        # Status messages
        'no_story_selected': 'No story selected',
        'invalid_story_selection': 'Invalid story selection',
        'error_loading_story': 'Error loading story',
        'no_audio_provided': 'No audio file provided',
        'error_generating_story': 'Error generating story',
        'error_speech_synthesis': 'Speech synthesis error',
        'please_provide_request': 'Please provide a story request',
        'openai_settings_saved': '✅ OpenAI settings saved',
        'elevenlabs_settings_saved': '✅ ElevenLabs settings saved',
        'global_settings_saved': '✅ Global settings saved successfully!',
        'all_settings_saved': '✅ All settings saved successfully! TTS services updated.',
        'api_key_missing': 'Please enter ElevenLabs API key first',
        'voices_loaded': 'voices loaded',
        'error_loading_voices': 'Error loading voices',
        'error_saving_settings': 'Error saving settings',
        'paragraph_saved': 'paragraph saved',
        'error_saving_paragraph': 'Error saving paragraph',
        'audio_regenerated': 'audio regenerated for',
        'error_regenerating_audio': 'Error regenerating audio',
        'story_saved_to': 'Story saved to',
        'paragraphs': 'paragraphs',
        'error_saving_story': 'Error saving story',
        'paragraphs_saved': 'paragraphs saved successfully',
        'error_saving_paragraphs': 'Error saving paragraphs',
        'audio_regenerated_all': 'audio regenerated for paragraphs',
        'error_regenerating_all': 'Error regenerating audio',
        'continuation_generated': 'new paragraphs continue the story!',
        'error_generating_continuation': 'Error generating story continuation',
        
        # Collections
        'all_categories': 'All',
        'favorites': 'Favorites',
        'recent': 'Recent',
        'long_stories': 'Long Stories',
        'short_stories': 'Short Stories',
        'all_voices': 'All Voices',
        'favorites_coming_soon': '⭐ Favorites feature coming soon!',
        'export_coming_soon': '📤 Export feature coming soon!',
        'delete_coming_soon': '🗑️ Delete feature coming soon!',
        
        # About tab content
        'about_title': '📚 Sarpy - AI Storyteller Management Interface',
        'about_enhanced': '**Enhanced Web Interface for Sarpy Story Management**',
        'about_features': 'This comprehensive interface allows you to:',
        'about_library': '📖 Story Library',
        'about_library_desc': '- Browse existing stories from your stories directory and examples\\n- View story metadata (query, model used, voice, etc.)\\n- Edit individual paragraphs with live preview\\n- Regenerate audio for specific paragraphs with different voices',
        'about_create': '✨ Create New Story',
        'about_create_desc': '- Record voice queries or type text requests\\n- Configure generation parameters (temperature, max tokens)\\n- Generate stories using various LLM models\\n- Convert stories to audio with selectable voices\\n- Save stories in the standard Sarpy format',
        'about_settings': '⚙️ Settings',
        'about_settings_desc': '- Configure API endpoints (OpenAI, local servers)\\n- Set default models and voices\\n- Manage story directories and safety settings',
        'about_project_features': '**Sarpy Project Features:**',
        'about_child_safe': '- 🎯 **Child-Safe**: Built-in query guards and content filtering',
        'about_low_latency': '- 🚀 **Low Latency**: Streaming generation for quick response',
        'about_self_hostable': '- 🏠 **Self-Hostable**: Support for local AI models via Ollama',
        'about_modular': '- 🔧 **Modular**: Configurable STT, LLM, and TTS services',
        'about_hardware_ready': '- 📱 **Hardware Ready**: Optimized for Raspberry Pi deployment',
        'about_requirements': '**System Requirements:**',
        'about_req_python': '- Python 3.8+',
        'about_req_api': '- OpenAI API key (or local AI server setup)',
        'about_req_audio': '- Microphone and speakers for voice interaction',
        'about_more_info': 'For more information, visit the [Sarpy GitHub repository](https://github.com/stefanom/fably).',
        
        # Voice options and model descriptions
        'voice_default': 'Default Voice',
        'voice_natural': 'Natural Voice',
        'voice_professional': 'Professional Voice',
        'voice_expressive': 'Expressive Voice',
        
        # Language selector
        'language_selector': 'Interface Language',
        'turkish': 'Türkçe',
        'english': 'English',
    }
}

# Default language is Turkish
DEFAULT_LANGUAGE = 'tr'

def get_text(key, lang=DEFAULT_LANGUAGE):
    """Get translated text for a given key and language"""
    return TRANSLATIONS.get(lang, TRANSLATIONS[DEFAULT_LANGUAGE]).get(key, key)

def get_available_languages():
    """Get list of available languages"""
    return [
        ('🇹🇷 Türkçe', 'tr'),
        ('🇬🇧 English', 'en')
    ]
