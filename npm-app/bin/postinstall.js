#!/usr/bin/env node

const { spawn, spawnSync } = require('child_process');
const path = require('path');
const fs = require('fs');

const pythonDir = path.join(__dirname, '..', 'python');
const venvDir = path.join(pythonDir, 'venv');
const requirementsFile = path.join(pythonDir, 'requirements.txt');

// Determine Python executable
function getPythonCommand() {
  // Try python3 first, then python
  const python3 = spawnSync('python3', ['--version'], { stdio: 'pipe' });
  if (python3.status === 0) return 'python3';

  const python = spawnSync('python', ['--version'], { stdio: 'pipe' });
  if (python.status === 0) return 'python';

  return null;
}

async function setup() {
  console.log('Setting up Python environment...');

  const pythonCmd = getPythonCommand();
  if (!pythonCmd) {
    console.error('Warning: Python not found in PATH');
    console.error('Please install Python 3.x from https://python.org');
    process.exit(0); // Don't fail npm install
  }

  // Create venv if it doesn't exist
  if (!fs.existsSync(venvDir)) {
    console.log('Creating virtual environment...');
    const venv = spawnSync(pythonCmd, ['-m', 'venv', venvDir], {
      stdio: 'inherit',
      cwd: pythonDir,
    });

    if (venv.status !== 0) {
      console.error('Warning: Failed to create virtual environment');
      process.exit(0);
    }
  }

  // Determine pip path
  const isWindows = process.platform === 'win32';
  const pipPath = isWindows
    ? path.join(venvDir, 'Scripts', 'pip.exe')
    : path.join(venvDir, 'bin', 'pip');

  // Install dependencies
  console.log('Installing Python dependencies...');
  const pip = spawn(pipPath, ['install', '-r', requirementsFile], {
    stdio: 'inherit',
    cwd: pythonDir,
  });

  pip.on('error', (err) => {
    console.error('Warning: Failed to install Python dependencies');
    process.exit(0);
  });

  pip.on('close', (code) => {
    if (code === 0) {
      console.log('✓ Python environment ready');
    } else {
      console.warn('Warning: Some dependencies may not have installed correctly');
    }
    process.exit(0);
  });
}

setup();
