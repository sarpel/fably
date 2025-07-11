"""
Localization system for Fably Enhanced Web Interface
Supports Turkish and English with Turkish as default
"""

# Language translations dictionary
TRANSLATIONS = {
    'tr': {
        # Main interface
        'title': '📚 Fably - AI Hikaye Anlatıcısı Yönetim Arayüzü',
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
        'transcribe_voice': '🔤 Sesli Sorguyu Metne Çevir',
        'transcribed_query': '📝 Metne Çevrilmiş Sorgu',
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
        
        # OpenAI settings
        'openai_config': 'OpenAI API Yapılandırması',
        'openai_api_key': 'OpenAI API Anahtarı',
        'openai_base_url': 'OpenAI Temel URL',
        'openai_models': 'OpenAI Modelleri',
        'language_model': 'Dil Modeli',
        'stt_model': 'Konuşma-Metin Modeli',
        'tts_model': 'Metin-Konuşma Modeli',
        'default_voice': 'Varsayılan OpenAI Sesi',
        'api_key_required': 'OpenAI servisleri için gerekli',
        'custom_endpoint_info': 'Özel OpenAI uyumlu uç noktalar için değiştirin',
        'story_generation_model': 'Hikaye üretimi için model',
        'higher_quality_tts': 'Daha yüksek kalite için tts-1-hd',
        'voice_for_tts': 'OpenAI TTS için ses',
        
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
        'stt_model_optional': 'STT Modeli ID (isteğe bağlı)',
        'tts_model_optional': 'TTS Modeli ID (isteğe bağlı)',
        'test_connection': '🔍 Bağlantıyı Test Et',
        
        # Global Settings
        'global_settings': '🌐 Genel Ayarlar',
        'default_provider_selection': 'Varsayılan Sağlayıcı Seçimi',
        'default_llm_provider': 'Varsayılan Dil Modeli Sağlayıcısı',
        'llm_provider_info': 'Hikaye üretimi için hangi sağlayıcı kullanılacak',
        'default_tts_provider': 'Varsayılan TTS Sağlayıcısı',
        'tts_provider_info': 'Konuşma sentezi için hangi sağlayıcı kullanılacak',
        'default_stt_provider': 'Varsayılan STT Sağlayıcısı',
        'stt_provider_info': 'Konuşma tanıma için hangi sağlayıcı kullanılacak',
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
        'audio_quality_settings': 'Ses Kalitesi Ayarları',
        'enable_noise_reduction': 'Gürültü Azaltmayı Etkinleştir',
        'noise_reduction_info': 'Ses kaydı sırasında arka plan gürültüsünü filtrele',
        'noise_sensitivity': 'Gürültü Hassasiyeti',
        'noise_sensitivity_info': 'Yüksek değerler sessiz seslere daha duyarlı',
        'audio_calibration': 'Ses Kalibrasyonu',
        'auto_calibrate': 'Gürültü Tabanını Otomatik Kalibre Et',
        'auto_calibrate_info': 'Başlangıçta ortam gürültüsünü otomatik ölç',
        'calibration_duration': 'Kalibrasyon Süresi (saniye)',
        'calibration_duration_info': 'Ortam gürültüsünü ne kadar süre ölçeceği',
        
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
        'error_transcribing': 'Ses metne çevrilirken hata',
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
        'about_title': '📚 Fably - AI Hikaye Anlatıcısı Yönetim Arayüzü',
        'about_enhanced': '**Fably Hikaye Yönetimi için Gelişmiş Web Arayüzü**',
        'about_features': 'Bu kapsamlı arayüz şunları yapmanıza olanak tanır:',
        'about_library': '📖 Hikaye Kütüphanesi',
        'about_library_desc': '- Hikayeler dizininizden ve örneklerden mevcut hikayeleri göz atın\\n- Hikaye meta verilerini görüntüleyin (sorgu, kullanılan model, ses, vb.)\\n- Canlı önizleme ile bireysel paragrafları düzenleyin\\n- Farklı seslerle belirli paragraflar için sesi yeniden oluşturun',
        'about_create': '✨ Yeni Hikaye Oluştur',
        'about_create_desc': '- Sesli sorgular kaydedin veya metin istekleri yazın\\n- Üretim parametrelerini yapılandırın (sıcaklık, maksimum token)\\n- Çeşitli LLM modelleri kullanarak hikayeler oluşturun\\n- Hikayeleri seçilebilir seslerle sese dönüştürün\\n- Hikayeleri standart Fably formatında kaydedin',
        'about_settings': '⚙️ Ayarlar',
        'about_settings_desc': '- API uç noktalarını yapılandırın (OpenAI, yerel sunucular)\\n- Varsayılan modelleri ve sesleri ayarlayın\\n- Hikaye dizinlerini ve güvenlik ayarlarını yönetin',
        'about_project_features': '**Fably Proje Özellikleri:**',
        'about_child_safe': '- 🎯 **Çocuk Güvenli**: Yerleşik sorgu korumaları ve içerik filtreleme',
        'about_low_latency': '- 🚀 **Düşük Gecikme**: Hızlı yanıt için akış üretimi',
        'about_self_hostable': '- 🏠 **Kendi Sunucunuzda Barındırılabilir**: Ollama aracılığıyla yerel AI modelleri desteği',
        'about_modular': '- 🔧 **Modüler**: Yapılandırılabilir STT, LLM ve TTS servisleri',
        'about_hardware_ready': '- 📱 **Donanım Hazır**: Raspberry Pi dağıtımı için optimize edilmiş',
        'about_requirements': '**Sistem Gereksinimleri:**',
        'about_req_python': '- Python 3.8+',
        'about_req_api': '- OpenAI API anahtarı (veya yerel AI sunucu kurulumu)',
        'about_req_audio': '- Ses etkileşimi için mikrofon ve hoparlörler',
        'about_more_info': 'Daha fazla bilgi için [Fably GitHub deposunu](https://github.com/stefanom/fably) ziyaret edin.',
        
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
        'title': '📚 Fably - AI Storyteller Management Interface',
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
        'transcribe_voice': '🔤 Transcribe Voice Query',
        'transcribed_query': '📝 Transcribed Query',
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
        
        # Settings and other translations...
        'settings_header': 'Provider Configuration Settings',
        'settings_desc': '*Configure different AI service providers separately*',
        'openai_config': 'OpenAI API Configuration',
        'language_model': 'Language Model',
        'stt_model': 'Speech-to-Text Model',
        'tts_model': 'Text-to-Speech Model',
        'default_voice': 'Default OpenAI Voice',
        'elevenlabs_config': 'ElevenLabs API Configuration',
        'elevenlabs_settings': 'ElevenLabs Settings',
        'gemini_config': 'Google Gemini Configuration',
        'custom_provider': 'Custom AI Provider Setup',
        'global_settings': '🌐 Global Settings',
        'audio_quality_settings': 'Audio Quality Settings',
        'collections_header': 'Advanced Story Management & Organization',
        'no_story_selected': 'No story selected',
        'error_loading_story': 'Error loading story',
        'please_provide_request': 'Please provide a story request',
        'all_settings_saved': '✅ All settings saved successfully!',
        'paragraphs': 'paragraphs',
        'all_categories': 'All',
        'favorites': 'Favorites',
        'recent': 'Recent',
        'about_title': '📚 Fably - AI Storyteller Management Interface',
        'voice_default': 'Default Voice',
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
