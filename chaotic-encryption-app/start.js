#!/usr/bin/env node
/**
 * Robust startup for Chaotic Image Encryption
 * - Prefers activated venv → ./.venv → ./backend/venv
 * - Uses `python -m pip` (no PATH issues)
 * - Cross-platform npm (npm.cmd on Windows)
 */

const { spawn, exec } = require('child_process');
const path = require('path');
const fs = require('fs');

const isWin = process.platform === 'win32';
const npmCmd = isWin ? 'npm' : 'npm';

function run(cmd, args, opts = {}) {
  return new Promise((resolve, reject) => {
    const p = spawn(cmd, args, { stdio: 'inherit', shell: false, ...opts });
    p.on('close', code => code === 0 ? resolve() : reject(new Error(`${cmd} exited with ${code}`)));
  });
}

function pythonFromVenvDir(venvDir) {
  if (!venvDir) return null;
  const exe = path.join(venvDir, isWin ? 'Scripts' : 'bin', isWin ? 'python.exe' : 'python');
  return fs.existsSync(exe) ? exe : null;
}

function resolvePython() {
  // 1) activated venv
  if (process.env.VIRTUAL_ENV) {
    const p = pythonFromVenvDir(process.env.VIRTUAL_ENV);
    if (p) return { py: p, venvDir: process.env.VIRTUAL_ENV };
  }
  // 2) repo .venv
  const repoVenv = path.join(__dirname, '.venv');
  const pyRepo = pythonFromVenvDir(repoVenv);
  if (pyRepo) return { py: pyRepo, venvDir: repoVenv };

  // 3) backend venv (create if needed)
  const backendDir = path.join(__dirname, 'backend');
  const backendVenv = path.join(backendDir, 'venv');
  const pyBackend = pythonFromVenvDir(backendVenv);
  return { py: pyBackend, venvDir: backendVenv, needsCreate: !pyBackend, backendDir };
}

async function ensureBackendVenv(ctx) {
  if (!ctx.needsCreate) return;
  console.log('📦 Creating backend virtual environment at', ctx.venvDir);
  const pyBootstrap = isWin ? 'py' : 'python3';
  await run(pyBootstrap, ['-m', 'venv', 'venv'], { cwd: ctx.backendDir });
}

async function pipInstall(py, reqPath, cwd) {
  console.log('📥 Installing Python dependencies…');
  await run(py, ['-m', 'pip', 'install', '--disable-pip-version-check', '-U', 'pip', 'setuptools', 'wheel'], { cwd });
  await run(py, ['-m', 'pip', 'install', '-r', reqPath], { cwd });
}

async function startBackend(py) {
  console.log('🌐 Starting backend on http://localhost:5001');
  // Choose one: app.py (dev) or gunicorn (prod-ish). Default to app.py.
  const backendDir = path.join(__dirname, 'backend');
  const appPath = path.join(backendDir, 'app.py');
  return spawn(py, [appPath], { cwd: backendDir, stdio: 'inherit' });
  // For gunicorn:
  // return spawn(py, ['-m', 'gunicorn', 'app:app', '--bind', '127.0.0.1:5001', '--chdir', 'backend'], { stdio: 'inherit' });
}

async function startFrontend() {
  console.log('🚀 Starting Frontend…');
  const frontendDir = path.join(__dirname, 'frontend');
  console.log('📥 Installing Node.js dependencies…');
  // On Windows, spawn npm via shell to avoid EINVAL in some environments
  await run(npmCmd, ['install'], { cwd: frontendDir, shell: isWin });
  console.log('🌐 Starting React dev server on http://localhost:3000');
  return spawn(npmCmd, ['start'], { cwd: frontendDir, stdio: 'inherit', shell: isWin });
}

function killTree(proc) {
  if (!proc) return;
  if (isWin) {
    spawn('taskkill', ['/pid', String(proc.pid), '/T', '/F']);
  } else {
    try { process.kill(-proc.pid, 'SIGTERM'); } catch {}
    try { proc.kill('SIGTERM'); } catch {}
  }
}

(async () => {
  try {
    console.log('🔐 Chaotic Image Encryption - Universal Startup');
    console.log('================================================');

    // Quick prerequisite check for Node/npm
    await new Promise((resolve) => {
      exec('node --version', (err) => {
        if (err) {
          console.error('❌ Node.js is not available on PATH. Please install Node.js 18+');
          process.exit(1);
        }
        resolve();
      });
    });
    await new Promise((resolve) => {
      exec(isWin ? 'npm -v' : 'npm -v', (err) => {
        if (err) {
          console.error('❌ npm is not available on PATH. Ensure Node.js installation added npm to PATH.');
          process.exit(1);
        }
        resolve();
      });
    });

    // Resolve Python
    const ctx = resolvePython();
    if (ctx.needsCreate && !ctx.backendDir) {
      throw new Error('No usable Python venv found and no backend dir to create one.');
    }
    if (ctx.needsCreate) await ensureBackendVenv(ctx);

    const py = pythonFromVenvDir(ctx.venvDir);
    if (!py) throw new Error('Failed to resolve Python executable from venv.');

    console.log('🐍 Using Python:', py);

    // Pip install (idempotent)
    await pipInstall(py, 'requirements.txt', path.join(__dirname, 'backend'));

    // Start backend
    const backendProc = await startBackend(py);

    // Give backend a moment (or poll health endpoint if you add one)
    await new Promise(r => setTimeout(r, 2000));

    // Start frontend
    const frontendProc = await startFrontend();

    console.log('\n🎉 Both servers launching!');
    console.log('📱 Frontend: http://localhost:3000');
    console.log('🔧 Backend:  http://localhost:5001\n');
    console.log('Press Ctrl+C to stop both.\n');

    // Graceful shutdown
    const shutdown = () => {
      console.log('\n🛑 Shutting down…');
      killTree(frontendProc);
      killTree(backendProc);
      process.exit(0);
    };
    process.on('SIGINT', shutdown);
    process.on('SIGTERM', shutdown);

  } catch (e) {
    console.error('❌ Error:', e.message);
    process.exit(1);
  }
})();
