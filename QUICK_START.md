# 🚀 Warp Engine - Quick Start Guide

## Installation (2 minutes)

### Step 1: Run the installer
```bash
./install.sh
```

### Step 2: Enter your OpenAI API key when prompted
The installer will ask:
```
Enter API Key: [paste your key here]
```

**Example API key format:**
- `sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
- `sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

Get your API key from: https://platform.openai.com/api-keys

### Step 3: Start Warp Engine
```bash
./warp-engine
```

That's it! You're ready to create AI agents.

---

## Your First Agent (1 minute)

1. Run `./warp-engine`
2. Select option `2` (New Agent)
3. Choose a template:
   - 🔬 Research Agent
   - 💻 Code Generator
   - 📊 Data Analyst
4. Give it a name
5. Done! Your agent is created and ready to use

---

## Test Your Setup

Run the test script to verify everything is working:
```bash
python test_setup.py
```

You should see all green checkmarks ✅

---

## Need Help?

- **Reset everything:** `./reset.sh`
- **View all agents:** `warp-engine agent list`
- **Run an agent:** `warp-engine agent run --name [agent-name]`
- **Start web UI:** `warp-engine serve`

---

## Common Issues

### "API key not set"
Run `./install.sh` and paste your OpenAI API key when prompted.

### "Module not found"
Make sure you're in the virtual environment:
```bash
source .venv/bin/activate
```

### "Permission denied"
Make scripts executable:
```bash
chmod +x install.sh warp-engine
```

---

## Example: Create a Research Agent

```bash
# Start the builder
./warp-engine

# Select: 2 (New Agent)
# Select: 1 (Research Agent)
# Name: "Linux Expert"

# Use it
echo "Analyze Linux kernel memory management" | ./bin/linux_expert
```

You'll get a comprehensive research report!

---

Ready to build amazing AI agents? Start with `./install.sh` 🎉
