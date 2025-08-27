const express = require('express');
const { exec } = require('child_process');

const app = express();

app.use(express.json());

let receivedMessage = null;

app.post('/', (req, res) => {
    receivedMessage = req.body;
    console.log('Webhook recibido:', receivedMessage);
    const commitMessage = req.body.commits?.[0]?.message || "No commit message";
    console.log('Commit recibido:', commitMessage);
    
    if (commitMessage === "BACKEND MODIFIED --> URL CHANGED") {
        // Fuerza actualización desde remoto, descartando cambios locales
        const cmd = 'git fetch --all && git reset --hard origin/main';
        exec(cmd, { cwd: __dirname }, (error, stdout, stderr) => {
            if (error) {
                console.error(`Error ejecutando git reset: ${error.message}`);
                return res.status(500).json({ error: error.message });
            }
            if (stderr) {
                console.error(`stderr: ${stderr}`);
            }
            console.log(`stdout: ${stdout}`);
            return res.json({ received: req.body, gitUpdate: stdout });
        });
    } else {
        res.json({ received: req.body });
    }
});

app.get('/', (req, res) => {
    res.json({ receivedMessage });
});

app.listen(3000, () => {
    console.log('[OK] BACKEND LISTENING ON PORT 3000');
});
