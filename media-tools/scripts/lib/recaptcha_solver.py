"""
reCAPTCHA Solver for Playwright — audio challenge approach
Adapted from GoogleRecaptchaBypass (sarperavci) and uncaptcha2 (ecthros)
Supports both v2 checkbox and audio challenges
"""
import os, random, time, urllib.request, tempfile
from typing import Optional

class RecaptchaSolver:
    """Solve reCAPTCHA challenges using audio recognition via Playwright."""
    
    def __init__(self, page):
        self.page = page
        self.temp_dir = tempfile.gettempdir()
    
    def solve(self, timeout=30) -> bool:
        """Attempt to solve reCAPTCHA on the current page.
        
        Args:
            timeout: Max seconds to wait for captcha iframe
            
        Returns:
            True if solved, False otherwise
        """
        try:
            # Step 1: Find the reCAPTCHA iframe
            print('[CAPTCHA] Looking for reCAPTCHA iframe...')
            
            # Wait for any recaptcha iframe to appear
            iframe = self.page.locator('iframe[title="reCAPTCHA"], iframe[src*="recaptcha"]')
            if iframe.count() == 0:
                # Maybe it's already solved or not present
                print('[CAPTCHA] No reCAPTCHA iframe found — may not be needed')
                return True
            
            print(f'[CAPTCHA] Found {iframe.count()} reCAPTCHA iframe(s)')
            
            # Try clicking the checkbox first
            for attempt in range(3):
                try:
                    # Get the iframe element
                    recaptcha_iframe = iframe.first
                    
                    # Switch to the iframe
                    frame = self.page.frame_locator('iframe[title="reCAPTCHA"]')
                    if frame is None:
                        frame = self.page.frame_locator('iframe[src*="recaptcha"]')
                    
                    if frame:
                        # Try to click the checkbox
                        checkbox = frame.locator('.recaptcha-checkbox-border, .rc-anchor-content')
                        if checkbox.count() > 0:
                            checkbox.click()
                            time.sleep(2)
                            print('[CAPTCHA] Checkbox clicked')
                            
                            # Check if solved
                            if self._is_solved(frame):
                                print('[CAPTCHA] ✓ Solved by checkbox click!')
                                return True
                            
                            # If challenge appeared, try audio
                            print('[CAPTCHA] Challenge appeared, trying audio...')
                            return self._solve_audio(frame)
                    else:
                        print('[CAPTCHA] Could not access iframe content')
                        return False
                        
                except Exception as e:
                    print(f'[CAPTCHA] Attempt {attempt+1} failed: {e}')
                    time.sleep(2)
            
            return False
            
        except Exception as e:
            print(f'[CAPTCHA] Error: {e}')
            return False
    
    def _is_solved(self, frame) -> bool:
        """Check if the captcha has been solved."""
        try:
            # Check for the checkmark style
            checkmark = frame.locator('.recaptcha-checkbox-checkmark[style*="display"]')
            return checkmark.count() > 0
        except:
            return False
    
    def _solve_audio(self, frame) -> bool:
        """Solve via audio challenge using speech recognition."""
        try:
            # Click audio button
            audio_btn = frame.locator('#recaptcha-audio-button')
            if audio_btn.count() == 0:
                # Try the alternate button
                audio_btn = frame.locator('button[aria-label*="audio challenge"]')
            if audio_btn.count() == 0:
                # Try image challenge button instead
                print('[CAPTCHA] No audio button found, trying image challenge...')
                return self._solve_image(frame)
            
            audio_btn.click()
            time.sleep(1)
            print('[CAPTCHA] Audio challenge selected')
            
            # Wait for audio source
            audio_source = frame.locator('#audio-source')
            if audio_source.count() == 0:
                print('[CAPTCHA] No audio source found')
                return False
            
            src = audio_source.get_attribute('src')
            if not src:
                print('[CAPTCHA] No audio source URL')
                return False
            
            print(f'[CAPTCHA] Downloading audio from {src[:60]}...')
            
            # Download the audio file
            mp3_path = os.path.join(self.temp_dir, f'captcha_{random.randrange(1000,9999)}.mp3')
            wav_path = os.path.join(self.temp_dir, f'captcha_{random.randrange(1000,9999)}.wav')
            
            try:
                urllib.request.urlretrieve(src, mp3_path)
                print(f'[CAPTCHA] Audio downloaded ({os.path.getsize(mp3_path)} bytes)')
                
                # Convert to WAV
                from pydub import AudioSegment
                sound = AudioSegment.from_mp3(mp3_path)
                sound.export(wav_path, format='wav')
                print(f'[CAPTCHA] Converted to WAV')
                
                # Transcribe
                import speech_recognition as sr
                recognizer = sr.Recognizer()
                with sr.AudioFile(wav_path) as source:
                    audio = recognizer.record(source)
                
                text = recognizer.recognize_google(audio)
                print(f'[CAPTCHA] Transcribed: "{text}"')
                
                # Submit the answer
                response_input = frame.locator('#audio-response')
                if response_input.count() > 0:
                    response_input.fill(text.lower())
                    time.sleep(0.5)
                    
                    verify_btn = frame.locator('#recaptcha-verify-button')
                    if verify_btn.count() > 0:
                        verify_btn.click()
                        time.sleep(2)
                        
                        if self._is_solved(frame):
                            print('[CAPTCHA] ✓ Audio challenge solved!')
                            return True
                        else:
                            print('[CAPTCHA] Verification may have failed')
                            return False
                
                return False
                
            finally:
                # Clean up temp files
                for path in (mp3_path, wav_path):
                    if os.path.exists(path):
                        try:
                            os.remove(path)
                        except: pass
            
        except ImportError as e:
            print(f'[CAPTCHA] Missing dependency: {e}')
            print('[CAPTCHA] Install: pip install pydub SpeechRecognition')
            return False
        except Exception as e:
            print(f'[CAPTCHA] Audio solve error: {e}')
            return False
    
    def _solve_image(self, frame) -> bool:
        """Solve image challenge - harder, requires external service.
        For now, returns False to indicate failure."""
        print('[CAPTCHA] Image challenges need manual solving or external service')
        return False


# Convenience function
def solve_recaptcha(page, timeout=30) -> bool:
    solver = RecaptchaSolver(page)
    return solver.solve(timeout)
