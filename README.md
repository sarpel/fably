# 🎭 Fably - 5 Yaşındaki Kızın AI Hikaye Anlatıcısı

**Fably**, 5 yaşındaki çocuklara özel olarak tasarlanmış yapay zeka destekli hikaye anlatıcısıdır. Gelişmiş ses tanıma, doğal dil işleme ve metin-ses teknolojisi kullanarak kişiselleştirilmiş, etkileşimli hikayeler oluşturur.

## ✨ Temel Özellikler

### 🎙️ **Gelişmiş Ses Etkileşimi**
- **Çoklu Ses Tanıma** - OpenAI Whisper, Google Cloud Speech, Yerel Whisper
- **Gürültü Azaltma** - Ev ortamı için gelişmiş ses filtreleme
- **Otomatik Kalibrasyon** - Oda gürültüsüne otomatik uyum
- **Ses Değiştirme** - Farklı anlatıcı sesleri arasında geçiş

### 🧠 **Çoklu AI Desteği**
- **OpenAI GPT** - GPT-4o, GPT-4o Mini yüksek kaliteli hikayeler için
- **Google Gemini** - Gemini 1.5 Pro, Gemini 1.5 Flash
- **DeepSeek** - Uygun maliyetli, mükemmel Türkçe desteği
- **Yerel Modeller** - Gizlilik odaklı Ollama desteği

### 🔊 **Profesyonel Metin-Ses**
- **OpenAI Sesleri** - Nova, Alloy, Echo, Fable, Onyx, Shimmer
- **ElevenLabs** - Duygusal ifade ile premium ses sentezi
- **Ses Tutarlılığı** - Hikaye boyunca karakter seslerini koruma

### 📚 **Hikaye Yönetimi**
- **Hikaye Devamı** - Mevcut hikayeleri yeni maceralarla genişletme
- **Akıllı Organizasyon** - Otomatik kategorilendirme ve metadata takibi
- **Koleksiyon Yönetimi** - Hikaye koleksiyonları oluşturma ve paylaşma

### 🌐 **Modern Web Arayüzü**
- **Gerçek Zamanlı Üretim** - Hikayelerin paragraf paragraf gelişimini izleme
- **Etkileşimli Kontroller** - Oynat, duraklat, atla, yeniden üret
- **Görsel Hikaye Tarayıcısı** - Arama ve filtreleme ile zengin arayüz

### 🏠 **Raspberry Pi Optimizasyonu**
- **Düşük Güç Tüketimi** - Her zaman açık çalışma için tasarlandı
- **Donanım Kontrolleri** - Çocuk dostu fiziksel düğme
- **LED Durum Göstergeleri** - Sistem durumu için görsel geri bildirim
- **Otomatik Başlatma** - Sistem ile birlikte otomatik açılır

## 🚀 Hızlı Başlangıç

### Tek Komut Kurulum

```bash
# Fably'yi klon et ve kur (tüm bağımlılıklar dahil)
git clone https://github.com/sarpel/fably.git
cd fably
chmod +x setup.sh
./setup.sh
```

### İlk Hikaye

```bash
# Ortamı aktif et
source .venv/bin/activate

# İlk hikayeni oluştur
fably "Bana cesur bir fare hakkında hikaye anlat"

# Etkileşimli mod
fably --noise-reduction --auto-calibrate --loop

# Web arayüzü
fably --web-app
```

## 📖 Kullanım Kılavuzu

### 🎮 Komut Satırı

#### **Temel Hikaye Üretimi**
```bash
# Tek hikaye üretimi
fably "Bana ejder ve prensesler hakkında hikaye anlat"
fably "Bir robot dinozorla karşılaştığında ne olur?"

# Belirli ayarlarla hikaye
fably --voice "elevenlabs:rachel" --paragraphs 5 "Uzay macerası hikayesi"
fably --model "gpt-4o" --voice "openai:nova" "Suya hikayesi"
```

#### **Etkileşimli Döngü Modu**
```bash
# Ses komutlarını dinlemeye başla
fably --loop

# Gelişmiş kalite modu (önerilen)
fably --noise-reduction --auto-calibrate --loop

# Ses değiştirme modu
fably --voice-cycle --loop

# Tüm özellikler bir arada
fably --noise-reduction --auto-calibrate --voice-cycle --loop
```

#### **Hikaye Devamı**
```bash
# Mevcut hikayeyi devam ettir
fably --continue "cesur_sovalye_hakkinda" "Şövalye ejderle karşılaştığında ne olur?"

# Farklı sesle devam ettir
fably --continue "uzay_macerasi" --voice "elevenlabs:adam" "Uzay gemisi Mars'a iniyor"
```

### 🌐 Web Arayüzü

```bash
# Profesyonel web arayüzünü başlat
fably --web-app
# http://localhost:7860 adresinde açılır

# Veya doğrudan başlat
python web_interface/launch.py
```

#### **Web Arayüzü Özellikleri**

**📚 Hikaye Kütüphanesi**
- Mevcut hikayeleri görüntüleme ve düzenleme
- Paragraf düzeyinde gerçek zamanlı düzenleme
- Sesli içerik yeniden oluşturma
- Hikaye devam ettirme sistemi

**✨ Yeni Hikaye Oluştur**
- Sesli sorgu kaydetme ve metin girişi
- Çoklu AI sağlayıcı desteği (OpenAI, Gemini, ElevenLabs)
- Gelişmiş yapılandırma seçenekleri
- Gerçek zamanlı ses sentezi

**⚙️ Sistem Ayarları**
- Çoklu AI sağlayıcı yönetimi
- Ses kalitesi ve donanım kontrolleri  
- Türkçe/İngilizce dinamik dil desteği
- Profesyonel yapılandırma arayüzü

### 🔧 Gelişmiş Yapılandırma

#### **Ortam Değişkenleri (.env dosyası)**
```bash
# Gerekli: OpenAI API anahtarı
OPENAI_API_KEY=sk-openai-api-anahtariniz

# İsteğe bağlı: Ek sağlayıcılar
ELEVENLABS_API_KEY=elevenlabs-anahtariniz
GEMINI_API_KEY=gemini-anahtariniz
DEEPSEEK_API_KEY=deepseek-anahtariniz
```

#### **Komut Satırı Seçenekleri**

**📝 Hikaye Üretimi**
- `--model` - AI model seçimi
  - `gpt-4o` - OpenAI GPT-4o (en yüksek kalite)
  - `gpt-4o-mini` - OpenAI GPT-4o Mini (hızlı, uygun maliyetli)
  - `gemini-1.5-pro` - Google Gemini Pro (yaratıcı)
  - `deepseek-chat` - DeepSeek Chat (ekonomik)

- `--voice` - Metin-ses sesi seçimi
  - OpenAI: `openai:nova`, `openai:alloy`, `openai:echo`
  - ElevenLabs: `elevenlabs:rachel`, `elevenlabs:adam`

- `--paragraphs` - Hikaye paragraf sayısı (1-10, varsayılan: 6)

**🎙️ Ses Ayarları**
- `--noise-reduction` - Gelişmiş gürültü filtreleme
- `--noise-sensitivity` - Gürültü geçidi hassasiyeti (0.1-10.0)
- `--auto-calibrate` - Oda gürültüsünü otomatik ölçme
- `--voice-cycle` - Çeşitlilik için farklı sesler arasında geçiş

**🔄 Hikaye Devamı**
- `--continue HIKAYE_ADI` - Mevcut hikayeyi devam ettir

**🎯 Hikaye İstemleri**
- `--story-request` - Belirli bir hikaye konusu iste

**🎙️ Uyandırma Kelimesi**
- `--wakeword-engine` - Wakeword motoru (ppn, onnx, tflite)
- `--wakeword-model` - Wakeword model dosya yolu
- `--wakeword-sensitivity` - Algılama hassasiyeti (0.0-1.0)

**🔘 GPIO Kontrolleri**
- `--gpio-button` - GPIO button'u wakeword alternatifi olarak etkinleştir
- `--button-gpio-pin` - GPIO pin numarası (varsayılan: 17)

**🎛️ Sistem Kontrolleri**
- `--loop` - Etkileşimli ses komut modu
- `--web-app` - Web arayüzünü başlat
- `--list-voices` - Tüm mevcut sesleri göster
- `--list-stories` - Tüm kayıtlı hikayeleri göster

**🎯 Hikaye İstemleri**
- `--story-request` - Belirli bir hikaye konusu iste

### 🏠 Raspberry Pi Kurulumu

#### **Donanım Gereksinimleri**
- **Raspberry Pi Zero 2W** (önerilen) veya Pi 4
- **reSpeaker 2-Mic HAT** (en iyi ses kalitesi için)
- **MicroSD kart** (32GB+, Class 10)

#### **Donanım Kurulumu**
```bash
# Otomatik kurulumu çalıştır (her şeyi halleder)
./setup.sh

# Ses kurulumunu test et
aplay /usr/share/sounds/alsa/Front_Center.wav
```

#### **Otomatik Başlatma Servisi**
```bash
# Otomatik başlatmayı etkinleştir
sudo systemctl enable fably.service
sudo systemctl start fably.service

# Durumu kontrol et
sudo systemctl status fably.service
```

#### **Donanım Kontrolleri**
- **Düğme Basımı** - Ses kaydını başlat
- **LED Göstergeleri**:
  - 🔵 Mavi - Sistem hazır
  - 🟢 Yeşil - Ses dinliyor
  - 🟡 Sarı - Hikaye işleniyor
  - 🔴 Kırmızı - Hata

### 🎯 Hikaye İstek Sistemi

#### **Belirli Hikaye Talepleri**
```bash
# Belirli bir konu hakkında hikaye iste
fably --story-request "Uzayda yaşayan bir kedi hakkında"
fably --story-request "Sihirli orman macerası"
fably --story-request "Prenses ve ejder dostluğu"

# Web arayüzünden
# Hikaye İsteği: "Denizin dibinde yaşayan balık prenses"
```

### 🎙️ Uyandırma Kelimesi (Wakeword) Sistemi

#### **Desteklenen Formatlar**
- **PPN (Picovoice)** - Profesyonel, düşük RAM (ÖNERİLEN Pi Zero 2W için)
- **ONNX** - Kendi eğitilen model
- **TFLite** - TensorFlow Lite model (opsiyonel)

#### **Wakeword Kullanımı**
```bash
# PPN wakeword ile (önerilen)
fably --wakeword-engine ppn --wakeword-model "fably.ppn" --loop

# ONNX wakeword ile
fably --wakeword-engine onnx --wakeword-model "fably.onnx" --loop

# Wakeword hassasiyeti ayarı
fably --wakeword-engine ppn --wakeword-model "fably.ppn" --wakeword-sensitivity 0.7 --loop
```

### 🔘 GPIO Button Sistemi

#### **Button İşlevleri**
- **Tek basış**: Ses kaydı başlat (wakeword alternatifi)
- **Çift basış**: Ses değiştir (voice-cycle aktifse)
- **Uzun basış**: Sistem kapatma

#### **GPIO Button Kullanımı**
```bash
# GPIO button aktif et
fably --gpio-button --loop

# GPIO button + ses değiştirme
fably --gpio-button --voice-cycle --loop

# Button pin değiştir
fably --gpio-button --button-gpio-pin 18 --loop
```

## 🛠️ Geliştirme

### **Geliştirme Kurulumu**
```bash
# Depoyu klonla
git clone https://github.com/sarpel/fably.git
cd fably

# Geliştirme modunda kur
pip install --editable .

# Kod biçimlendirme
./setup.sh format

# Kod kalite kontrolü
./setup.sh check
```

### **Proje Yapısı**
```
fably/
├── fably/                    # Ana uygulama paketi
│   ├── cli.py               # Komut satırı arayüzü
│   ├── fably.py             # Temel hikaye mantığı
│   ├── utils.py             # Yardımcı fonksiyonlar
│   ├── voice_manager.py     # Ses tanıma sistemi
│   ├── tts_service.py       # Metin-ses servisi
│   └── sounds/              # Ses dosyaları
├── tools/                   # Geliştirme araçları
│   └── gradio_app/         # Web arayüzü
├── servers/                 # Bağımsız sunucular
├── tests/                  # Test suite
├── setup.sh               # Komple kurulum scripti
└── README.md              # Bu kılavuz
```

## 🔧 Sorun Giderme

### **Yaygın Sorunlar**

#### **"API anahtarı bulunamadı"**
```bash
# .env dosyasının varlığını ve doğru formatını kontrol et
cat .env
# Şunları içermeli: OPENAI_API_KEY=sk-anahtariniz
```

#### **"Ses cihazı bulunamadı"**
```bash
# Mevcut ses cihazlarını listele
python -c "import sounddevice; print(sounddevice.query_devices())"

# Mikrofonu test et
python tools/capture_voice_query.py
```

#### **"Ses komutları tanınmıyor"**
```bash
# Gürültü azaltma olmadan test et
fably --loop

# Gürültü hassasiyetini artır
fably --noise-reduction --noise-sensitivity 3.0 --auto-calibrate --loop
```

#### **"Hikayeler yavaş üretiliyor"**
```bash
# Daha hızlı model kullan
fably --model gpt-4o-mini "Hızlı hikaye"

# Paragraf sayısını azalt
fably --paragraphs 3 "Kısa hikaye"
```

### **Hata Ayıklama Modu**
```bash
# Ayrıntılı günlükleme etkinleştir
fably --debug "test hikayesi"

# Sistem durumunu kontrol et
fably --system-info
```

## 🎯 Örnek Kullanım

### **Tipik Günlük Kullanım**
```bash
# Sabah hikayesi
fably "Günaydın hikayesi - neşeli bir hayvan macerası"

# Öğle sonrası
fably --continue "sabah_hikayesi" "Kahramanımız yeni arkadaşlarla ne yapıyor?"

# Yatmadan önce
fably --voice "openai:echo" --paragraphs 4 "Huzurlu uyku hikayesi"
```

### **Web Arayüzü ile**
1. `fably --web-app` ile başlat
2. "Hikaye Üretimi" sekmesine git
3. "Bir prenses ve sihirli kedi hikayesi" yaz
4. Ses: "elevenlabs:rachel" seç
5. "Hikaye Oluştur" butonuna bas
6. Hikayeyi dinle ve keyif al!

---

**Fably ile hayal dünyası sınırsız! 🎭✨**

*Bu proje, 5 yaşındaki çocuğun güvenli teknoloji deneyimi ve yaratıcılığını geliştirmek amacıyla sevgiyle geliştirilmiştir.*
