"""
Fix OpenCV DLL Issues on Windows
Completely removes opencv-python and installs opencv-python-headless
"""

import subprocess
import sys

def run_command(cmd, description):
    """Run a command and print the result"""
    print(f"\n[{description}]")
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    return result.returncode == 0

def fix_opencv():
    """Fix OpenCV installation for Windows"""
    print("="*80)
    print("FIXING OPENCV FOR WINDOWS")
    print("="*80)

    # Step 1: Uninstall all opencv packages
    print("\n[STEP 1] Removing all OpenCV packages...")
    packages_to_remove = [
        'opencv-python',
        'opencv-contrib-python',
        'opencv-python-headless',
        'opencv-contrib-python-headless'
    ]

    for package in packages_to_remove:
        run_command(f'pip uninstall {package} -y', f'Uninstalling {package}')

    # Step 2: Install opencv-python-headless only
    print("\n[STEP 2] Installing opencv-python-headless...")
    success = run_command('pip install opencv-python-headless==4.9.0.80', 'Installing opencv-python-headless')

    if not success:
        print("\n❌ Installation failed!")
        return False

    # Step 3: Verify installation
    print("\n[STEP 3] Verifying installation...")
    try:
        import cv2
        print(f"✅ SUCCESS! OpenCV version: {cv2.__version__}")
        print(f"✅ OpenCV is now working without DLL issues!")
        return True
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False

if __name__ == "__main__":
    success = fix_opencv()

    if success:
        print("\n" + "="*80)
        print("✅ OPENCV FIXED SUCCESSFULLY!")
        print("="*80)
        print("\nYou can now run:")
        print("  python quick_test.py")
        print("  python app.py")
        sys.exit(0)
    else:
        print("\n" + "="*80)
        print("❌ FIX FAILED")
        print("="*80)
        print("\nPlease manually run:")
        print("  pip uninstall opencv-python opencv-python-headless -y")
        print("  pip install opencv-python-headless")
        sys.exit(1)
