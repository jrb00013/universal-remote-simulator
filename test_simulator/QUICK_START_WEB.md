# Quick Start - Web 3D/VR Simulator

## 🚀 Get Started in 3 Steps

### Step 1: Install Poetry (if not installed)

```bash
curl -sSL https://install.python-poetry.org | python3 -
export PATH="$HOME/.local/bin:$PATH"
```

### Step 2: Install Dependencies

```bash
cd test_simulator
poetry install
```

**Note:** Poetry handles everything - no pip needed!

### Step 3: Start Server

```bash
poetry run web-server
```

**Or:**
```bash
poetry run python web_server.py
```

### Step 3: Open Browser

Go to: **http://localhost:5000**

That's it! You'll see a beautiful 3D TV in a virtual room.

## 🎮 Controls

- **Mouse Drag**: Rotate camera around TV
- **Scroll Wheel**: Zoom in/out  
- **Space**: Reset camera

## 🔌 Connect Remote Control

1. **Build with web support:**
   ```bash
   make clean
   make SIMULATOR=1 WEB=1
   ```

2. **Run remote control:**
   ```bash
   ./bin/remote_control
   ```

3. **Press buttons** - Watch them appear in the 3D TV!

## 🎯 What You'll See

- **3D TV Model**: Realistic TV with screen, frame, and stand
- **Virtual Room**: Immersive environment with walls, floor, ceiling
- **Real-time Updates**: TV responds instantly to button presses
- **Status Panel**: See all TV state in real-time
- **Smooth Animations**: Power on/off, screen glow effects

## 💡 Tips

- Use **fullscreen mode** (F11) for best experience
- Works on **mobile devices** too!
- **Multiple browsers** can connect simultaneously
- Great for **demos and presentations**

Enjoy your immersive 3D TV experience! 🎬

