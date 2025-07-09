# 📚 Fably - Yapay Zeka Hikaye Anlatıcısı

> 5 yaşındaki Türk çocukları için özel olarak tasarlanmış yapay zeka destekli hikaye anlatıcısı

Fably, çocukların hayal gücünü geliştiren, güvenli ve eğitici hikayeler oluşturan gelişmiş bir AI sistemidir. Raspberry Pi'da çalışacak şekilde optimize edilmiş, tamamen Türkçe dil desteği sunan ve çoklu AI provider entegrasyonu içeren modern bir hikaye anlatıcısıdır.

## 🌟 Temel Özellikler

### 🎯 Çocuk Odaklı Tasarım
- **5 yaş grubu için optimize** - Yaş grubuna uygun kelime dağarcığı ve anlatım
- **Tamamen güvenli içerik** - Şiddet, korku ve uygunsuz içerik filtresi
- **Türk kültürü uyumlu** - Türk isimleri, değerleri ve kültürel öğeler
- **Eğitici değerler** - Dostluk, paylaşma, dürüstlük gibi değerleri öğretir

### 🤖 Gelişmiş AI Entegrasyonu
- **Çoklu LLM Desteği**: OpenAI GPT-4o, Google Gemini, Deepseek
- **Akıllı STT**: OpenAI Whisper, Google Cloud Speech, Local Whisper
- **Kaliteli TTS**: OpenAI sesler, ElevenLabs premium sesler
- **Ses Kalitesi**: Gürültü azaltma, otomatik kalibrasyon

### 🎨 Modern Kullanıcı Arayüzü
- **Gelişmiş Web Arayüzü**: Modern, responsive Gradio tabanlı
- **Light/Dark Mode**: Tema değiştirme desteği
- **Canlı İzleme**: Sistem metrikleri, CPU/RAM/disk takibi
- **Live Loglar**: Gerçek zamanlı sistem günlükleri
- **Mobil Uyumlu**: Tablet ve telefon desteği

### 🔧 Donanım ve Sistem
- **Raspberry Pi Optimize**: Pi Zero 2W ve Pi 5 desteği
- **Düşük Kaynak**: 512MB RAM'de çalışır
- **GPIO Desteği**: Düğme kontrolü, LED feedback
- **Ses İşleme**: Gelişmiş gürültü azaltma algoritmaları

## 🚀 Hızlı Başlangıç

### Kurulum

1. **Repository'yi klonlayın:**
```bash
git clone https://github.com/stefanom/fably.git
cd fably
```

2. **Bağımlılıkları yükleyin:**
```bash
python -m venv fably-env
source fably-env/bin/activate  # Linux/Mac
# veya
fably-env\Scripts\activate  # Windows

pip install --editable .
```

3. **API anahtarlarını ayarlayın:**
```bash
cp env.example .env
# .env dosyasını düzenleyerek API anahtarlarınızı ekleyin
```

### Temel Kullanım

**Komut satırından hikaye oluşturma:**
```bash
fably "bana bir prenses hikayesi anlat"
```

**Web arayüzünü başlatma:**
```bash
fably --web-interface
# Tarayıcıda http://localhost:7860 adresine gidin
```

**Gelişmiş seçeneklerle:**
```bash
fably --llm-provider gemini \
      --tts-provider elevenlabs \
      --noise-reduction \
      --auto-calibrate \
      --loop
```

## ⚙️ Konfigürasyon

### API Anahtarları

`.env` dosyasında gerekli API anahtarlarını ayarlayın:

```env
# OpenAI (zorunlu - temel LLM ve TTS için)
OPENAI_API_KEY=sk-...

# Google Gemini (opsiyonel - gelişmiş LLM için)
GEMINI_API_KEY=AI...

# Deepseek (opsiyonel - alternatif LLM için)
DEEPSEEK_API_KEY=sk-...

# ElevenLabs (opsiyonel - premium TTS için)
ELEVENLABS_API_KEY=...

# Google Cloud (opsiyonel - gelişmiş STT için)
GOOGLE_CLOUD_API_KEY=...
GOOGLE_PROJECT_ID=your-project-id
```

### Provider Seçenekleri

#### LLM (Language Model) Sağlayıcıları:
- **OpenAI**: `gpt-4o`, `gpt-4o-mini`, `gpt-3.5-turbo`
- **Google Gemini**: `gemini-1.5-pro`, `gemini-1.5-flash`, `gemini-pro`
- **Deepseek**: `deepseek-chat`, `deepseek-coder`

#### STT (Speech-to-Text) Sağlayıcıları:
- **OpenAI Whisper**: Cloud tabanlı, hızlı
- **Google Cloud Speech**: Yüksek doğruluk, Türkçe optimize
- **Local Whisper**: Offline çalışma, gizlilik

#### TTS (Text-to-Speech) Sağlayıcıları:
- **OpenAI**: `nova`, `alloy`, `echo`, `fable`, `onyx`, `shimmer`
- **ElevenLabs**: Premium kalitede, çeşitli sesler

## 🎮 Kullanım Senaryoları

### 1. Basit Hikaye Anlatımı
```bash
# OpenAI ile basit kullanım
fably "bana bir kedi hikayesi anlat"
```

### 2. Premium Kalite
```bash
# Gemini LLM + ElevenLabs TTS
fably --llm-provider gemini \
      --tts-provider elevenlabs \
      "bana bir macera hikayesi anlat"
```

### 3. Offline Çalışma
```bash
# Tamamen yerel modeller
fably --stt-provider local_whisper \
      --local-whisper-model base \
      --loop
```

### 4. Gürültülü Ortam
```bash
# Gelişmiş ses işleme
fably --noise-reduction \
      --noise-sensitivity 1.5 \
      --auto-calibrate \
      --calibration-duration 5.0
```

### 5. Ses Değiştirme Modu
```bash
# Düğme ile ses değiştirme
fably --voice-cycle --loop
# Çift tıklama ile sesler arasında geçiş
```

## 📱 Web Arayüzü Özellikleri

Web arayüzünü `fably --web-interface` ile başlatın ve aşağıdaki özelliklerden yararlanın:

### 📖 Hikaye Kütüphanesi
- Mevcut hikayeleri görüntüleme ve düzenleme
- Paragraf bazında düzenleme
- Ses yeniden oluşturma
- Hikaye devam ettirme

### ✨ Yeni Hikaye Oluşturma
- Sesli veya yazılı talep
- Provider ve model seçimi
- Gerçek zamanlı hikaye oluşturma
- Ses sentezi ve kaydetme

### 📚 Koleksiyonlar
- Hikaye arama ve filtreleme
- İstatistikler ve analizler
- Toplu işlemler
- Dışa aktarma

### ⚙️ Ayarlar
- API anahtarı yönetimi
- Provider konfigürasyonu
- Ses kalitesi ayarları
- Sistem parametreleri

### 🔧 Sistem İzleme
- CPU, RAM, disk kullanımı
- Sıcaklık monitörü
- Gerçek zamanlı grafikler
- Performance metrikleri

### 📋 Canlı Günlükler
- Gerçek zamanlı log akışı
- Log seviyesi filtreleme
- Hata takibi
- Sistem durumu

### 🎨 Tema Desteği
- Light/Dark mode toggle
- Modern, responsive tasarım
- Mobil cihaz uyumluluğu
- Accessibility desteği

## 🔧 Raspberry Pi Kurulumu

### Otomatik Kurulum (Önerilen)
```bash
# Tüm bağımlılıkları otomatik yükler
chmod +x setup.sh
./setup.sh
```

### Systemd Servisi Kurulumu
```bash
# Otomatik başlatma için
sudo cp install/rpi/fably.service /etc/systemd/system/
sudo systemctl enable fably.service
sudo systemctl start fably.service

# Durum kontrolü
sudo systemctl status fably.service
```

### Donanım Gereksinimleri

#### Raspberry Pi Zero 2W (Minimum)
- **RAM**: 512MB
- **CPU**: Quad-core ARM Cortex-A53
- **Storage**: 16GB microSD (Class 10)
- **Audio**: USB Audio Adapter
- **Network**: WiFi

#### Raspberry Pi 5 (Önerilen)
- **RAM**: 8GB
- **CPU**: Quad-core ARM Cortex-A76
- **Storage**: 32GB microSD (A2 sınıfı)
- **Audio**: USB Audio / HAT
- **Cooling**: Aktif soğutma

### Ses Donanımı
- **Mikrofon**: USB mikrofon veya HAT
- **Hoparlör**: 3.5mm veya USB hoparlör
- **Önerilen**: Waveshare USB Audio Adapter

## 🎛️ Gelişmiş Özellikler

### Ses Kalitesi Optimizasyonu

**Gürültü Azaltma:**
```bash
fably --noise-reduction \
      --noise-sensitivity 2.5 \
      --auto-calibrate \
      --calibration-duration 4.0
```

**Parametreler:**
- `--noise-sensitivity`: 0.1-10.0 (yüksek = daha hassas)
- `--calibration-duration`: 1.0-10.0 saniye
- `--auto-calibrate`: Otomatik ortam gürültüsü ölçümü

### Ses Döngüsü (Voice Cycling)
```bash
# Düğme ile ses değiştirme
fably --voice-cycle --loop

# Düğmeye çift tıklayarak sesler arasında geçiş yapın
```

### Hikaye Devam Ettirme
```bash
# Mevcut hikayeye devam et
fably --continue-story "prenses" "ejderle karşılaştığında ne oldu?"
```

### Provider Testleri
```bash
# Tüm provider'ları test et
fably --test-providers

# Mevcut sesleri listele
faby --list-voices

# Ses önizlemesi
fably --voice-preview "nova"
```

## 🔒 Güvenlik ve Gizlilik

### Çocuk Güvenliği
- **İçerik Filtresi**: Otomatik şiddet/korku tespiti
- **Kültürel Uyum**: Türk değerleri ve aile yapısı
- **Yaş Uygunluk**: 5 yaş seviyesinde kelime seçimi
- **Pozitif Mesajlar**: Her hikaye öğretici değerler içerir

### Veri Güvenliği
- **Yerel İşleme**: Ses kayıtları cihazda kalır
- **Şifreli Bağlantı**: API çağrıları HTTPS ile
- **Veri Saklama**: Hikayeler yerel olarak saklanır
- **Gizlilik**: Kişisel veri paylaşımı yok

### Offline Çalışma
```bash
# Tamamen offline mod
fably --stt-provider local_whisper \
      --llm-provider ollama \
      --local-whisper-model base
```

## 📊 Performans ve Optimizasyon

### Bellek Kullanımı
- **Pi Zero 2W**: ~300MB RAM kullanımı
- **Pi 5**: ~1GB RAM kullanımı (gelişmiş özelliklerle)
- **Optimizasyon**: Model boyutu ayarlanabilir

### Response Süreleri
- **STT**: 1-3 saniye (ses uzunluğuna bağlı)
- **LLM**: 5-15 saniye (model ve token sayısına bağlı)
- **TTS**: 2-5 saniye (metin uzunluğuna bağlı)
- **Toplam**: 8-23 saniye (end-to-end)

### Optimizasyon İpuçları

**Hız için:**
```bash
fably --llm-model gpt-3.5-turbo \
      --max-tokens 1000 \
      --tts-provider openai
```

**Kalite için:**
```bash
fably --llm-provider gemini \
      --llm-model gemini-1.5-pro \
      --tts-provider elevenlabs \
      --max-tokens 2000
```

**Düşük kaynak için:**
```bash
fably --local-whisper-model tiny \
      --max-tokens 800 \
      --noise-reduction false
```

## 🛠️ Geliştirme

### Kod Kalitesi
```bash
# Kod formatlama
./format.sh

# Lint kontrolleri
./check.sh

# Tüm kontroller
./push.sh "commit mesajı"
```

### Test Etme
```bash
# Unit testler
python -m pytest tests/ -v

# Entegrasyon testleri
python tests/test_asyncio.py

# Ses testleri
python tools/capture_voice_query.py
python tools/mic_spectrogram.py
```

### Custom Provider Ekleme

Yeni bir LLM provider eklemek için `fably/llm_service.py` dosyasına:

```python
class CustomLLMProvider(LLMProvider):
    def __init__(self, api_key: str, base_url: str):
        super().__init__("Custom", api_key, base_url)
    
    async def generate_story(self, prompt: str, **kwargs):
        # Kendi implementasyonunuz
        pass
```

## 📈 İzleme ve Log

### Sistem Logları
```bash
# Systemd logları
journalctl -u fably.service -f

# Debug modu
fably --debug --loop

# Performans testi
python tools/performance_test.py
```

### Web Arayüzü İzleme
- Gerçek zamanlı CPU/RAM/disk grafikler
- Live log akışı
- Provider durumu
- Ses kalitesi metrikleri

## 🔄 Güncelleme

### Otomatik Güncelleme
```bash
./update.sh
```

### Manuel Güncelleme
```bash
git pull origin main
pip install --editable . --upgrade
sudo systemctl restart fably.service
```

## 🐛 Sorun Giderme

### Yaygın Problemler

**1. API Anahtarı Hatası:**
```
ValueError: OPENAI_API_KEY environment variable not set
```
**Çözüm:** `.env` dosyasında API anahtarınızı kontrol edin.

**2. Ses Cihazı Bulunamadı:**
```bash
# Ses cihazlarını listele
python tools/list_sound_devices.py

# ALSA ayarları (Raspberry Pi)
sudo raspi-config  # Advanced Options > Audio
```

**3. Permission Hatası (GPIO):**
```bash
sudo usermod -a -G gpio $USER
# Oturumu yeniden başlatın
```

**4. Düşük Ses Kalitesi:**
```bash
# Gürültü tabanı ölçümü
python tools/noise_floor.py

# Mikrofon test
python tools/mic_spectrogram.py

# Gelişmiş ses filtresi
fably --noise-reduction --auto-calibrate --debug
```

**5. Yavaş Response:**
```bash
# Lightweight modeller kullanın
fably --llm-model gpt-3.5-turbo \
      --local-whisper-model tiny \
      --max-tokens 1000
```

### Debug Komutları
```bash
# Provider bağlantı testleri
fably --test-providers

# Ses önizleme
fably --voice-preview nova

# Sistem durumu
htop
vcgencmd measure_temp  # Raspberry Pi sıcaklık
```

## 📞 Destek ve Topluluk

### Topluluk Kaynakları
- **GitHub Issues**: [Sorun bildirimi](https://github.com/stefanom/fably/issues)
- **Discussions**: [Topluluk forumu](https://github.com/stefanom/fably/discussions)
- **Wiki**: [Detaylı dokümantasyon](https://github.com/stefanom/fably/wiki)

### Katkıda Bulunma
1. Fork edin ve klonlayın
2. Feature branch oluşturun (`git checkout -b yeni-ozellik`)
3. Değişikliklerinizi commit edin (`git commit -am 'feat: yeni özellik'`)
4. Branch'i push edin (`git push origin yeni-ozellik`)
5. Pull Request oluşturun

### Dokümantasyon
- **Installation Guide**: [Kurulum rehberi](docs/installation.md)
- **API Reference**: [API dokümantasyonu](docs/api.md)
- **Hardware Guide**: [Donanım kılavuzu](docs/hardware.md)
- **Troubleshooting**: [Sorun giderme](docs/troubleshooting.md)

## 📝 Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakın.

## 🙏 Teşekkürler

Fably projesi aşağıdaki açık kaynak projelerin desteğiyle geliştirilmektedir:

- **OpenAI**: GPT modelleri ve Whisper STT
- **Google**: Gemini AI ve Cloud Speech API
- **Deepseek**: Açık kaynak LLM modelleri
- **ElevenLabs**: Kaliteli TTS servisleri
- **Gradio**: Modern web arayüzü framework
- **Raspberry Pi Foundation**: Uygun fiyatlı donanım platformu

## 🚀 Roadmap

### v2.0 (Yakında)
- [ ] Çoklu dil desteği (İngilizce, Arapça)
- [ ] Görsel hikaye desteği (DALL-E entegrasyonu)
- [ ] Sesli etkileşim (soru-cevap diyalogları)
- [ ] Ebeveyn dashboard ve kontrol paneli
- [ ] Hikaye kişiselleştirme (çocuğun ismini kullanma)

### v2.1
- [ ] Çocuk profilleri ve tercihleri
- [ ] İlerleme takibi ve başarı rozetleri
- [ ] Gamification öğeleri
- [ ] Sosyal paylaşım (güvenli)

### v3.0
- [ ] AR/VR entegrasyonu
- [ ] Çoklu karakter sesleri
- [ ] İnteraktif hikayeler (seçim yapma)
- [ ] AI öğretmen asistanı

---

## 🌈 Hızlı Başlangıç Özeti

```bash
# 1. Klonla
git clone https://github.com/stefanom/fably.git && cd fably

# 2. Kur
python -m venv fably-env && source fably-env/bin/activate
pip install --editable .

# 3. API anahtarını ayarla
echo "OPENAI_API_KEY=sk-your-key-here" > .env

# 4. Çalıştır
fably "bana bir kedi hikayesi anlat"

# 5. Web arayüzü
fably --web-interface
```

**Fably ile çocuklarınızın hayal dünyası sınırsız! 🎭✨**

*Bu proje, çocukların güvenli bir şekilde teknoloji ile tanışması ve yaratıcılıklarını geliştirmesi amacıyla sevgiyle geliştirilmiştir.*
