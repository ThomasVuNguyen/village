#!/usr/bin/env node

const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

// Parse command
const args = process.argv.slice(2);
const command = args[0];

// Show version
if (command === '--version' || command === '-v' || command === 'version') {
  const packageJson = require('../package.json');
  console.log(`village v${packageJson.version}`);
  process.exit(0);
}

// Command mapping to Python scripts
const commands = {
  setup: 'register_user.py',
  register: 'register_device.py',
  send: 'ask.py',
  listen: 'listen.py',
  status: 'status.py',
  logout: 'sign_out.py',
};

// Help text
const help = `
Village - Distributed inter-device communication

Usage:
  village <command> [options]

Commands:
  setup              Sign up/sign in and register this device
  register [name]    Register this device with optional name
  send <command>     Send command to idle device (auto-routes)
  listen             Start listening for incoming commands
  status             Show all your devices and their status
  logout             Sign out (keeps device_id)
  logout --reset     Full reset (deletes device_id)
  version, -v        Show version number

Examples:
  village setup
  village send "uptime"
  village send "df -h" --to device-id-here
  village listen
  village status

Environment Variables:
  TO_DEVICE_ID       Target device ID (or "auto" for auto-routing)
  COMMAND            Command to execute on remote device

More info: https://github.com/yourusername/village
`;

// Show help
if (!command || command === 'help' || command === '--help' || command === '-h') {
  console.log(help);
  process.exit(0);
}

// Validate command
if (!commands[command]) {
  console.error(`Unknown command: ${command}`);
  console.error(`Run 'village help' for usage information`);
  process.exit(1);
}

// Get Python executable from venv
function getPythonExecutable() {
  const pythonDir = path.join(__dirname, '..', 'python');
  const venvDir = path.join(pythonDir, 'venv');

  const isWindows = process.platform === 'win32';
  const pythonPath = isWindows
    ? path.join(venvDir, 'Scripts', 'python.exe')
    : path.join(venvDir, 'bin', 'python');

  // Check if venv Python exists
  if (fs.existsSync(pythonPath)) {
    return pythonPath;
  }

  // Fallback to system Python
  return 'python';
}

// Check if Python is available
function checkPython(pythonCmd) {
  return new Promise((resolve) => {
    const python = spawn(pythonCmd, ['--version'], { stdio: 'pipe' });
    python.on('error', () => resolve(false));
    python.on('close', (code) => resolve(code === 0));
  });
}

// Main execution
async function main() {
  // Get Python executable (venv or system)
  const pythonCmd = getPythonExecutable();

  // Check Python
  const hasPython = await checkPython(pythonCmd);
  if (!hasPython) {
    console.error('Error: Python is not installed or not in PATH');
    console.error('Please install Python 3.x from https://python.org');
    console.error('Or run: npm install -g @thomasthemaker/village (to reinstall)');
    process.exit(1);
  }

  // Build Python script path
  const pythonDir = path.join(__dirname, '..', 'python');
  const scriptName = commands[command];
  const scriptPath = path.join(pythonDir, scriptName);

  // Check if script exists
  if (!fs.existsSync(scriptPath)) {
    console.error(`Error: Script not found: ${scriptPath}`);
    console.error('The village package may be corrupted. Try reinstalling.');
    process.exit(1);
  }

  // Handle special command transformations
  const pythonArgs = [];

  if (command === 'send') {
    // Transform: village send "uptime" --to device-id
    // To: python ask.py with env vars
    const cmdIndex = args.findIndex((arg, i) => i > 0 && !arg.startsWith('--'));
    const toIndex = args.indexOf('--to');

    if (cmdIndex > 0) {
      process.env.COMMAND = args[cmdIndex];
    }

    if (toIndex >= 0 && args[toIndex + 1]) {
      process.env.TO_DEVICE_ID = args[toIndex + 1];
    } else {
      process.env.TO_DEVICE_ID = 'auto';
    }

    // Pass remaining flags
    const flags = args.filter(arg => arg.startsWith('--') && arg !== '--to');
    pythonArgs.push(...flags);
  } else if (command === 'register') {
    // village register "My Laptop" → python register_device.py "My Laptop"
    pythonArgs.push(...args.slice(1));
  } else if (command === 'logout') {
    // village logout --reset → python sign_out.py --reset
    pythonArgs.push(...args.slice(1));
  }

  // Spawn Python process
  const python = spawn(pythonCmd, [scriptPath, ...pythonArgs], {
    stdio: 'inherit',
    env: process.env,
  });

  python.on('error', (err) => {
    console.error('Failed to start Python:', err.message);
    process.exit(1);
  });

  python.on('close', (code) => {
    process.exit(code || 0);
  });
}

main().catch((err) => {
  console.error('Unexpected error:', err);
  process.exit(1);
});
