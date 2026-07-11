"""
Audio Device Handler
Enumerates available audio devices and handles recording/playback
Useful for demonstrating audio capabilities to recruiters
"""

import pyaudio
import wave
import json
from datetime import datetime
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AudioDeviceManager:
    """Manage audio devices and recording/playback operations"""
    
    def __init__(self):
        self.p = pyaudio.PyAudio()
        self.recordings_dir = Path('./recordings')
        self.recordings_dir.mkdir(exist_ok=True)
    
    def enumerate_devices(self):
        """List all available audio input/output devices"""
        devices = []
        
        for i in range(self.p.get_device_count()):
            device_info = self.p.get_device_info_by_index(i)
            devices.append({
                'index': i,
                'name': device_info['name'],
                'input_channels': device_info['maxInputChannels'],
                'output_channels': device_info['maxOutputChannels'],
                'sample_rate': int(device_info['defaultSampleRate']),
                'host_api': device_info['hostApi']
            })
        
        return devices
    
    def print_devices(self):
        """Pretty print available devices"""
        devices = self.enumerate_devices()
        print("\n" + "="*70)
        print("AVAILABLE AUDIO DEVICES")
        print("="*70)
        
        for device in devices:
            print(f"\n[{device['index']}] {device['name']}")
            print(f"    Input Channels: {device['input_channels']}")
            print(f"    Output Channels: {device['output_channels']}")
            print(f"    Sample Rate: {device['sample_rate']} Hz")
        
        print("\n" + "="*70 + "\n")
    
    def get_default_input_device(self):
        """Get default input device index"""
        return self.p.get_default_input_device_info()['index']
    
    def get_default_output_device(self):
        """Get default output device index"""
        return self.p.get_default_output_device_info()['index']
    
    def record_audio(self, device_index=None, duration=5, sample_rate=44100, channels=1):
        """
        Record audio from specified device
        
        Args:
            device_index: Audio device index (uses default if None)
            duration: Recording duration in seconds
            sample_rate: Sample rate in Hz
            channels: Number of channels (1=mono, 2=stereo)
        
        Returns:
            Path to recorded file
        """
        if device_index is None:
            device_index = self.get_default_input_device()
        
        chunk = 1024
        frames = []
        
        try:
            stream = self.p.open(
                format=pyaudio.paFloat32,
                channels=channels,
                rate=sample_rate,
                input=True,
                input_device_index=device_index,
                frames_per_buffer=chunk
            )
            
            logger.info(f"Recording from device {device_index} for {duration} seconds...")
            print(f"\n🎤 Recording... ({duration}s)")
            
            for _ in range(0, int(sample_rate / chunk * duration)):
                data = stream.read(chunk)
                frames.append(data)
            
            stream.stop_stream()
            stream.close()
            
            # Save recording
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = self.recordings_dir / f'recording_{timestamp}.wav'
            
            with wave.open(str(filename), 'wb') as wf:
                wf.setnchannels(channels)
                wf.setsampwidth(self.p.get_sample_size(pyaudio.paFloat32))
                wf.setframerate(sample_rate)
                wf.writeframes(b''.join(frames))
            
            logger.info(f"Recording saved: {filename}")
            print(f"✅ Recording saved: {filename}\n")
            
            return str(filename)
        
        except Exception as e:
            logger.error(f"Recording error: {e}")
            print(f"❌ Error during recording: {e}\n")
            return None
    
    def playback_audio(self, filename, device_index=None, sample_rate=44100, channels=1):
        """
        Playback audio file to specified device
        
        Args:
            filename: Path to audio file
            device_index: Audio device index (uses default if None)
            sample_rate: Sample rate in Hz
            channels: Number of channels
        """
        if device_index is None:
            device_index = self.get_default_output_device()
        
        chunk = 1024
        
        try:
            with wave.open(filename, 'rb') as wf:
                stream = self.p.open(
                    format=self.p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True,
                    output_device_index=device_index
                )
                
                logger.info(f"Playing {filename} to device {device_index}...")
                print(f"\n🔊 Playing audio...\n")
                
                data = wf.readframes(chunk)
                while len(data) > 0:
                    stream.write(data)
                    data = wf.readframes(chunk)
                
                stream.stop_stream()
                stream.close()
                
                logger.info("Playback complete")
                print("✅ Playback complete\n")
        
        except Exception as e:
            logger.error(f"Playback error: {e}")
            print(f"❌ Error during playback: {e}\n")
    
    def get_device_stats(self):
        """Get comprehensive device statistics"""
        devices = self.enumerate_devices()
        input_devices = [d for d in devices if d['input_channels'] > 0]
        output_devices = [d for d in devices if d['output_channels'] > 0]
        
        stats = {
            'total_devices': len(devices),
            'input_devices': len(input_devices),
            'output_devices': len(output_devices),
            'default_input': self.get_default_input_device(),
            'default_output': self.get_default_output_device(),
            'devices': devices
        }
        
        return stats
    
    def export_device_info(self, filename='device_info.json'):
        """Export device information to JSON file"""
        stats = self.get_device_stats()
        
        with open(filename, 'w') as f:
            json.dump(stats, f, indent=2)
        
        logger.info(f"Device info exported to {filename}")
        print(f"✅ Device info exported to {filename}\n")
        
        return filename
    
    def cleanup(self):
        """Clean up PyAudio resources"""
        self.p.terminate()

def main():
    """Demo: Enumerate devices and perform test recording"""
    manager = AudioDeviceManager()
    
    try:
        # Enumerate and display devices
        manager.print_devices()
        
        # Export device info
        manager.export_device_info()
        
        # Get device statistics
        stats = manager.get_device_stats()
        print(f"Device Statistics:")
        print(f"  Total: {stats['total_devices']}")
        print(f"  Input: {stats['input_devices']}")
        print(f"  Output: {stats['output_devices']}\n")
        
        # Optional: Record demo audio
        # Uncomment to enable:
        # recording_file = manager.record_audio(duration=3)
        # if recording_file:
        #     manager.playback_audio(recording_file)
    
    finally:
        manager.cleanup()

if __name__ == '__main__':
    main()
