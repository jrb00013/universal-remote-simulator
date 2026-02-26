# 🚀 RUN NOW - Quick Commands for WSL/Linux

## You got "externally-managed-environment" error? Use Poetry!

### Step 1: Install Poetry (one-time setup)

```bash
curl -sSL https://install.python-poetry.org | python3 -
export PATH="$HOME/.local/bin:$PATH"
```

Verify:
```bash
poetry --version
```

### Step 2: Install Dependencies

```bash
cd test_simulator
poetry install
```

### Step 3: Run Web Server

```bash
poetry run web-server
```

Then open: **http://localhost:5000**

---

## That's It!

Poetry handles everything:
- ✅ Creates virtual environment automatically
- ✅ Installs all dependencies
- ✅ No system Python conflicts
- ✅ Works on WSL, Linux, Mac, Windows

---

## Need Desktop Simulator Instead?

```bash
poetry run desktop-simulator
```

---

## Using Poetry Shell (Optional)

Activate the environment to run commands directly:

```bash
poetry shell
python web_server.py
python main.py
exit  # When done
```

---

## Troubleshooting

**Poetry not found?**
```bash
# Add to ~/.bashrc permanently
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

**Still having issues?**
See `WSL_SETUP.md` for detailed guide.

