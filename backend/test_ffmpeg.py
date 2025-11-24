"""
Quick test to check if ffmpeg is installed and working
"""
import subprocess
import shutil
import sys


def test_ffmpeg():
    """Test if ffmpeg is available"""
    print("=" * 60)
    print("Testing ffmpeg Installation")
    print("=" * 60)
    
    # Check if ffmpeg is in PATH
    print("\n1. Checking if ffmpeg is in PATH...")
    ffmpeg_path = shutil.which("ffmpeg")
    
    if ffmpeg_path:
        print(f"   ✓ ffmpeg found at: {ffmpeg_path}")
    else:
        print("   ✗ ffmpeg NOT FOUND in PATH")
        print("\n   This is the problem! Voice mode needs ffmpeg.")
        print("\n   SOLUTION:")
        print("   1. Install ffmpeg:")
        print("      - Chocolatey: choco install ffmpeg")
        print("      - Or download from: https://www.gyan.dev/ffmpeg/builds/")
        print("   2. Restart your terminal")
        print("   3. Restart backend server")
        print("\n   See FIX_VOICE_MODE.md for detailed instructions")
        return False
    
    # Try to run ffmpeg
    print("\n2. Testing ffmpeg execution...")
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print(f"   ✓ ffmpeg works: {version_line}")
            return True
        else:
            print(f"   ✗ ffmpeg returned error code: {result.returncode}")
            print(f"   Error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("   ✗ ffmpeg command timed out")
        return False
    except Exception as e:
        print(f"   ✗ Error running ffmpeg: {e}")
        return False


def main():
    success = test_ffmpeg()
    
    print("\n" + "=" * 60)
    if success:
        print("✓ ffmpeg is installed and working!")
        print("\nVoice mode should work now.")
        print("If you still see errors, restart your backend server.")
    else:
        print("✗ ffmpeg is NOT working")
        print("\nPlease install ffmpeg and try again.")
        print("See FIX_VOICE_MODE.md for instructions.")
    print("=" * 60)
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
