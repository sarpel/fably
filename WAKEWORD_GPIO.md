# Wakeword ve GPIO Button Eklentileri

## Wakeword Desteği

Raspberry Pi Zero 2W için optimize edilmiş wakeword sistemi:

### Desteklenen Formatlar:
1. **PPN (Picovoice)** - Profesyonel, düşük RAM kullanımı (ÖNERİLEN)
2. **ONNX** - Kendi eğitilmiş model
3. **TFLite** - TensorFlow Lite model (opsiyonel)

### Kurulum:
```bash
# Picovoice PPN için
pip install pvporcupine

# ONNX için  
pip install onnxruntime

# TFLite için (opsiyonel)
pip install tflite-runtime
```

### Kullanım:
```bash
# PPN wakeword ile (önerilen)
fably --wakeword-engine ppn --wakeword-model "path/to/fably.ppn" --loop

# ONNX wakeword ile
fably --wakeword-engine onnx --wakeword-model "path/to/fably.onnx" --loop

# GPIO button alternatif olarak
fably --gpio-button --loop
```

## GPIO Button Sistemi

Wakeword alternatifi olarak fiziksel button:

- **Tek basış**: Ses kaydı başlat
- **Çift basış**: Ses değiştir (voice-cycle aktifse)  
- **Uzun basış**: Sistem kapatma

### Avantajlar:
- Sıfır RAM kullanımı
- %100 güvenilir tetikleme
- Çocuklar için basit kullanım
