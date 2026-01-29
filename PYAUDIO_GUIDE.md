# PyAudio Installation Guide for Windows

## The Issue

PyAudio requires **PortAudio** C library to compile, which is problematic on Windows without Visual Studio Build Tools.

## ✅ Solution 1: Use Pre-built Wheel (Easiest)

### Step 1: Download PyAudio Wheel
1. Go to: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
2. Find your Python version (check with `python --version`)
3. Download the `.whl` file matching your Python version

**Example for Python 3.13 (64-bit):**
- Download: `PyAudio‑0.2.11‑cp313‑cp313‑win_amd64.whl`

### Step 2: Install the Wheel
```powershell
# Navigate to where you downloaded the file
cd "C:\Users\YourUsername\Downloads"

# Install the wheel
pip install PyAudio-0.2.11-cp313-cp313-win_amd64.whl
```

### Step 3: Verify Installation
```powershell
python -c "import pyaudio; print('✅ PyAudio installed!')"
```

---

## ✅ Solution 2: Use Anaconda (If you have it)

```powershell
conda install pyaudio
```

---

## ✅ Solution 3: Skip Voice, Use Text Only (Quickest)

If you don't want to install PyAudio:
1. ✅ App still works perfectly
2. ✅ Use **Text input** instead
3. ✅ Get all corrections and feedback
4. ✅ No voice needed

---

## ✅ Solution 4: Use WSL (Advanced)

If you're on Windows 10/11, use Windows Subsystem for Linux:

```bash
# In WSL terminal
sudo apt-get install portaudio19-dev
pip install pyaudio
```

---

## Verify Your Python Version

Before downloading the wheel, check your Python version:

```powershell
python --version
```

**Match the wheel to your version:**
- Python 3.13 → `cp313`
- Python 3.12 → `cp312`
- Python 3.11 → `cp311`
- Python 3.10 → `cp310`

Also check if 32-bit or 64-bit:

```powershell
python -c "import struct; print(f'{struct.calcsize(\"P\") * 8}-bit')"
```

**Result:**
- 64-bit → `win_amd64.whl`
- 32-bit → `win32.whl`

---

## Troubleshooting

### ❌ "Wheel file is not compatible"
- Download the correct version matching your Python
- Use `python --version` to verify

### ❌ "No module named 'portaudio'"
- This is normal - PyAudio bundles PortAudio
- If wheel installation worked, try restarting Python

### ❌ "Failed building wheel for pyaudio"
- This means pip tried to compile from source
- Use the pre-built wheel method instead

---

## App Without PyAudio

The app works perfectly without PyAudio:
- ✅ Text input works 100%
- ✅ AI analysis works 100%
- ✅ All corrections work 100%
- ❌ Voice input unavailable

**Use Text input instead:**
1. Open http://localhost:8501
2. Settings → Input Method → "Text"
3. Type your sentence
4. Click "🔍 Analyze"
5. Get feedback! 🌟

---

## Recommended Approach

### For Learning English:
- 👍 Use **Text input** - More accurate typing practice
- 👍 Use **Audio feedback** - Listen to corrections
- This is actually better for learning!

### When You Need Voice:
- Follow Solution 1 above
- Use pre-built wheel
- 5-minute installation

---

## Support

Having issues? Try these:

1. **Check Python version match** - Most common issue
2. **Use Text input** - Works perfectly
3. **Try WSL** - Easiest alternative
4. **Restart the app** - After installing PyAudio

The app is fully functional with Text input! 🎉
