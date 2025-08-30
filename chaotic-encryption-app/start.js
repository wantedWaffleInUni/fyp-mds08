#!/usr/bin/env node

/**
 * Universal Startup Script for Chaotic Image Encryption
 * Works on both macOS/Linux and Windows
 */

const { spawn, exec } = require('child_process');
const path = require('path');
const fs = require('fs');

console.log('🔐 Chaotic Image Encryption - Universal Startup Script');
console.log('======================================================');

// Check operating system
const isWindows = process.platform === 'win32';
const pythonCmd = isWindows ? 'python' : 'python3';
const npmCmd = 'npm';

// Function to check if command exists
function checkCommand(command) {
    return new Promise((resolve) => {
        exec(`${command} --version`, (error) => {
            resolve(!error);
        });
    });
}

// Function to start backend
function startBackend() {
    return new Promise((resolve, reject) => {
        console.log('🚀 Starting Backend...');
        
        const backendDir = path.join(__dirname, 'backend');
        const venvDir = path.join(backendDir, 'venv');
        const activateScript = isWindows ? 'Scripts\\activate.bat' : 'bin/activate';
        
        // Check if virtual environment exists
        if (!fs.existsSync(venvDir)) {
            console.log('📦 Creating virtual environment...');
            const venvProcess = spawn(pythonCmd, ['-m', 'venv', 'venv'], { cwd: backendDir });
            venvProcess.on('close', (code) => {
                if (code === 0) {
                    console.log('✅ Virtual environment created');
                    installBackendDependencies();
                } else {
                    reject(new Error('Failed to create virtual environment'));
                }
            });
        } else {
            installBackendDependencies();
        }
        
        function installBackendDependencies() {
            console.log('📥 Installing Python dependencies...');
            const pipCmd = isWindows ? 'venv\\Scripts\\pip' : 'venv/bin/pip';
            const pipProcess = spawn(pipCmd, ['install', '-r', 'requirements.txt'], { cwd: backendDir });
            
            pipProcess.on('close', (code) => {
                if (code === 0) {
                    console.log('✅ Dependencies installed');
                    startFlaskServer();
                } else {
                    reject(new Error('Failed to install dependencies'));
                }
            });
        }
        
        function startFlaskServer() {
            console.log('🌐 Starting Flask server on http://localhost:5001');
            const pythonPath = isWindows ? 'venv\\Scripts\\python' : 'venv/bin/python';
            const flaskProcess = spawn(pythonPath, ['app.py'], { cwd: backendDir });
            
            flaskProcess.stdout.on('data', (data) => {
                console.log(`[Backend] ${data.toString().trim()}`);
            });
            
            flaskProcess.stderr.on('data', (data) => {
                console.error(`[Backend Error] ${data.toString().trim()}`);
            });
            
            flaskProcess.on('close', (code) => {
                console.log(`Backend process exited with code ${code}`);
            });
            
            resolve(flaskProcess);
        }
    });
}

// Function to start frontend
function startFrontend() {
    return new Promise((resolve, reject) => {
        console.log('🚀 Starting Frontend...');
        
        const frontendDir = path.join(__dirname, 'frontend');
        
        console.log('📥 Installing Node.js dependencies...');
        const npmInstallProcess = spawn(npmCmd, ['install'], { cwd: frontendDir });
        
        npmInstallProcess.on('close', (code) => {
            if (code === 0) {
                console.log('✅ Dependencies installed');
                startReactServer();
            } else {
                reject(new Error('Failed to install frontend dependencies'));
            }
        });
        
        function startReactServer() {
            console.log('🌐 Starting React server on http://localhost:3000');
            const reactProcess = spawn(npmCmd, ['start'], { cwd: frontendDir });
            
            reactProcess.stdout.on('data', (data) => {
                console.log(`[Frontend] ${data.toString().trim()}`);
            });
            
            reactProcess.stderr.on('data', (data) => {
                console.error(`[Frontend Error] ${data.toString().trim()}`);
            });
            
            reactProcess.on('close', (code) => {
                console.log(`Frontend process exited with code ${code}`);
            });
            
            resolve(reactProcess);
        }
    });
}

// Main execution
async function main() {
    try {
        // Check prerequisites
        console.log('🔍 Checking prerequisites...');
        
        const pythonExists = await checkCommand(pythonCmd);
        if (!pythonExists) {
            console.error(`❌ ${pythonCmd} is not installed. Please install Python 3.8 or higher.`);
            process.exit(1);
        }
        
        const npmExists = await checkCommand(npmCmd);
        if (!npmExists) {
            console.error(`❌ ${npmCmd} is not installed. Please install Node.js 16 or higher.`);
            process.exit(1);
        }
        
        console.log('✅ Prerequisites check passed');
        
        // Start services
        const backendProcess = await startBackend();
        
        // Wait a bit for backend to start
        await new Promise(resolve => setTimeout(resolve, 3000));
        
        const frontendProcess = await startFrontend();
        
        console.log('');
        console.log('🎉 Both servers are starting up!');
        console.log('📱 Frontend: http://localhost:3000');
        console.log('🔧 Backend:  http://localhost:5001');
        console.log('');
        console.log('Press Ctrl+C to stop both servers');
        
        // Handle graceful shutdown
        process.on('SIGINT', () => {
            console.log('\n🛑 Shutting down servers...');
            backendProcess.kill();
            frontendProcess.kill();
            process.exit(0);
        });
        
    } catch (error) {
        console.error('❌ Error:', error.message);
        process.exit(1);
    }
}

main();
