# Testing the Village npm package

## Local Testing (before publishing)

### 1. Link package globally
```bash
cd npm-app
npm link
```

This creates a global symlink to your local package.

### 2. Test commands
```bash
# Test help
village help

# Test setup
village setup

# Test register
village register "My Test Device"

# Test status
village status

# Test send (requires another device running listen)
village send "echo hello"

# Test listen
village listen
```

### 3. Unlink when done
```bash
npm unlink -g village
```

## Publishing to npm

### 1. Login to npm
```bash
npm login
```

### 2. Publish
```bash
cd npm-app
npm publish
```

### 3. Test published package
```bash
npm install -g village
village --help
```

## Testing on Different Platforms

**Windows:**
```powershell
npm link
village help
```

**macOS/Linux:**
```bash
npm link
village help
```

## Troubleshooting

**"Python not found"**
- Make sure Python 3.x is installed and in PATH
- Try `python --version` or `python3 --version`

**"Module not found"**
- Run `pip install -r npm-app/python/requirements.txt` manually

**Permission errors**
- On Unix: `sudo npm install -g village`
- On Windows: Run as Administrator
