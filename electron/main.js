const { app, BrowserWindow } = require('electron');
const { spawn } = require('child_process');
const path = require('path');

let mainWindow;
let streamlitProcess;

function startStreamlit() {
    const pythonCmd = process.platform === 'win32' ? 'python' : 'python3';
    const venvPath = process.platform === 'win32'
        ? path.join(__dirname, '..', 'venv', 'Scripts', 'python.exe')
        : path.join(__dirname, '..', 'venv', 'bin', 'python');

    streamlitProcess = spawn(pythonCmd, [
        '-m', 'streamlit', 'run',
        path.join(__dirname, '..', 'app.py'),
        '--server.headless', 'true',
        '--server.port', '8501',
        '--browser.gatherUsageStats', 'false'
    ], {
        cwd: path.join(__dirname, '..'),
        stdio: 'pipe'
    });

    streamlitProcess.stdout.on('data', (data) => {
        console.log(`Streamlit: ${data}`);
    });

    streamlitProcess.stderr.on('data', (data) => {
        console.error(`Streamlit: ${data}`);
    });
}

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 1200,
        height: 800,
        title: 'SQL随身教练',
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true
        }
    });

    setTimeout(() => {
        mainWindow.loadURL('http://localhost:8501');
    }, 3000);

    mainWindow.on('closed', () => {
        mainWindow = null;
    });
}

app.whenReady().then(() => {
    startStreamlit();
    createWindow();
});

app.on('window-all-closed', () => {
    if (streamlitProcess) {
        streamlitProcess.kill();
    }
    app.quit();
});

app.on('before-quit', () => {
    if (streamlitProcess) {
        streamlitProcess.kill();
    }
});
