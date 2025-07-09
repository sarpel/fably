"""
Wakeword detection system for Fably.
Supports PPN (Picovoice), ONNX, and TFLite models.
Optimized for Raspberry Pi Zero 2W.
"""

import logging
import threading
import time
from typing import Optional, Callable
import sounddevice as sd
import numpy as np

# Optional imports based on engine availability
try:
    import pvporcupine
    PPN_AVAILABLE = True
except ImportError:
    PPN_AVAILABLE = False
    pvporcupine = None

try:
    import onnxruntime as ort
    ONNX_AVAILABLE = True
except ImportError:
    ONNX_AVAILABLE = False
    ort = None

try:
    import tflite_runtime.interpreter as tflite
    TFLITE_AVAILABLE = True
except ImportError:
    try:
        import tensorflow.lite as tflite
        TFLITE_AVAILABLE = True
    except ImportError:
        TFLITE_AVAILABLE = False
        tflite = None


class WakewordDetector:
    """Unified wakeword detector supporting multiple engines."""
    
    def __init__(self, engine: str, model_path: str, sensitivity: float = 0.5):
        self.engine = engine.lower()
        self.model_path = model_path
        self.sensitivity = sensitivity
        self.is_listening = False
        self.detection_callback: Optional[Callable] = None
        self.audio_thread: Optional[threading.Thread] = None
        self.detector = None
        
        # Audio parameters optimized for wakeword detection
        self.sample_rate = 16000
        self.frame_length = 512
        
        self._initialize_detector()
    
    def _initialize_detector(self):
        """Initialize the specific wakeword engine."""
        if self.engine == "ppn":
            if not PPN_AVAILABLE:
                raise ImportError("Picovoice Porcupine not available. Install with: pip install pvporcupine")
            self._initialize_ppn()
        elif self.engine == "onnx":
            if not ONNX_AVAILABLE:
                raise ImportError("ONNX Runtime not available. Install with: pip install onnxruntime")
            self._initialize_onnx()
        elif self.engine == "tflite":
            if not TFLITE_AVAILABLE:
                raise ImportError("TFLite not available. Install with: pip install tflite-runtime")
            self._initialize_tflite()
        else:
            raise ValueError(f"Unsupported wakeword engine: {self.engine}")
    
    def _initialize_ppn(self):
        """Initialize Picovoice Porcupine (recommended for Pi Zero 2W)."""
        try:
            self.detector = pvporcupine.create(
                keyword_paths=[self.model_path],
                sensitivities=[self.sensitivity]
            )
            self.sample_rate = self.detector.sample_rate
            self.frame_length = self.detector.frame_length
            logging.info(f"PPN detector initialized: {self.sample_rate}Hz, frame_length={self.frame_length}")
        except Exception as e:
            raise RuntimeError(f"Failed to initialize PPN detector: {e}")
    
    def _initialize_onnx(self):
        """Initialize ONNX model."""
        try:
            self.detector = ort.InferenceSession(self.model_path)
            logging.info(f"ONNX detector initialized from {self.model_path}")
        except Exception as e:
            raise RuntimeError(f"Failed to initialize ONNX detector: {e}")
    
    def _initialize_tflite(self):
        """Initialize TensorFlow Lite model."""
        try:
            self.detector = tflite.Interpreter(model_path=self.model_path)
            self.detector.allocate_tensors()
            logging.info(f"TFLite detector initialized from {self.model_path}")
        except Exception as e:
            raise RuntimeError(f"Failed to initialize TFLite detector: {e}")
    
    def _detect_ppn(self, audio_frame: np.ndarray) -> bool:
        """Process audio frame with PPN detector."""
        try:
            # Convert to int16 if needed
            if audio_frame.dtype != np.int16:
                audio_frame = (audio_frame * 32767).astype(np.int16)
            
            keyword_index = self.detector.process(audio_frame)
            return keyword_index >= 0
        except Exception as e:
            logging.error(f"PPN detection error: {e}")
            return False
    
    def _detect_onnx(self, audio_frame: np.ndarray) -> bool:
        """Process audio frame with ONNX detector."""
        try:
            # Prepare input for ONNX model (adapt based on your model)
            input_name = self.detector.get_inputs()[0].name
            audio_input = audio_frame.astype(np.float32).reshape(1, -1)
            
            outputs = self.detector.run(None, {input_name: audio_input})
            confidence = outputs[0][0] if outputs else 0.0
            
            return confidence > self.sensitivity
        except Exception as e:
            logging.error(f"ONNX detection error: {e}")
            return False
    
    def _detect_tflite(self, audio_frame: np.ndarray) -> bool:
        """Process audio frame with TFLite detector."""
        try:
            # Get input and output details
            input_details = self.detector.get_input_details()
            output_details = self.detector.get_output_details()
            
            # Prepare input data
            audio_input = audio_frame.astype(np.float32).reshape(input_details[0]['shape'])
            self.detector.set_tensor(input_details[0]['index'], audio_input)
            
            # Run inference
            self.detector.invoke()
            
            # Get output
            output_data = self.detector.get_tensor(output_details[0]['index'])
            confidence = output_data[0] if len(output_data) > 0 else 0.0
            
            return confidence > self.sensitivity
        except Exception as e:
            logging.error(f"TFLite detection error: {e}")
            return False
    
    def _audio_callback(self, indata, frames, time, status):
        """Audio callback for real-time processing."""
        if status:
            logging.warning(f"Audio status: {status}")
        
        if not self.is_listening:
            return
        
        # Convert to numpy array and flatten
        audio_frame = indata.flatten()
        
        # Ensure correct frame length
        if len(audio_frame) != self.frame_length:
            return
        
        # Run detection based on engine
        detected = False
        if self.engine == "ppn":
            detected = self._detect_ppn(audio_frame)
        elif self.engine == "onnx":
            detected = self._detect_onnx(audio_frame)
        elif self.engine == "tflite":
            detected = self._detect_tflite(audio_frame)
        
        # Trigger callback if wakeword detected
        if detected and self.detection_callback:
            try:
                self.detection_callback()
            except Exception as e:
                logging.error(f"Detection callback error: {e}")
    
    def start_listening(self, detection_callback: Callable):
        """Start listening for wakeword."""
        if self.is_listening:
            logging.warning("Already listening for wakeword")
            return
        
        self.detection_callback = detection_callback
        self.is_listening = True
        
        try:
            # Start audio stream
            self.audio_stream = sd.InputStream(
                callback=self._audio_callback,
                channels=1,
                samplerate=self.sample_rate,
                blocksize=self.frame_length,
                dtype=np.float32
            )
            
            self.audio_stream.start()
            logging.info(f"Wakeword detection started ({self.engine})")
            
        except Exception as e:
            self.is_listening = False
            raise RuntimeError(f"Failed to start wakeword detection: {e}")
    
    def stop_listening(self):
        """Stop listening for wakeword."""
        if not self.is_listening:
            return
        
        self.is_listening = False
        
        try:
            if hasattr(self, 'audio_stream'):
                self.audio_stream.stop()
                self.audio_stream.close()
            logging.info("Wakeword detection stopped")
        except Exception as e:
            logging.error(f"Error stopping wakeword detection: {e}")
    
    def __del__(self):
        """Cleanup on destruction."""
        self.stop_listening()
        
        # Clean up detector resources
        if self.engine == "ppn" and self.detector:
            try:
                self.detector.delete()
            except:
                pass


def get_available_engines():
    """Get list of available wakeword engines."""
    engines = []
    if PPN_AVAILABLE:
        engines.append("ppn")
    if ONNX_AVAILABLE:
        engines.append("onnx")
    if TFLITE_AVAILABLE:
        engines.append("tflite")
    return engines


def create_wakeword_detector(engine: str, model_path: str, sensitivity: float = 0.5) -> WakewordDetector:
    """Factory function to create wakeword detector."""
    available_engines = get_available_engines()
    
    if not available_engines:
        raise RuntimeError("No wakeword engines available. Install pvporcupine, onnxruntime, or tflite-runtime")
    
    if engine not in available_engines:
        raise ValueError(f"Engine '{engine}' not available. Available: {available_engines}")
    
    return WakewordDetector(engine, model_path, sensitivity)
