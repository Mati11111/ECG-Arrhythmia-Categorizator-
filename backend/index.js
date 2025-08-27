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
        console.log("Esperando 10 segundos antes de actualizar el repo...");

        setTimeout(() => {
            const cmd = 'git fetch origin main && git checkout main && git reset --hard origin/main && git clean -fd';
            exec(cmd, { cwd: __dirname }, (error, stdout, stderr) => {
                if (error) {
                    console.error(`Error ejecutando actualización: ${error.message}`);
                    return res.status(500).json({ error: error.message });
                }
                if (stderr) {
                    console.error(`stderr: ${stderr}`);
                }
                console.log(`stdout: ${stdout}`);
                
                exec('git rev-parse --short HEAD', { cwd: __dirname }, (err, commitHash) => {
                    if (err) {
                        console.error(`Error obteniendo commit hash: ${err.message}`);
                        return res.json({ received: req.body, gitUpdate: stdout });
                    }
                    console.log(`Repo actualizado al commit ${commitHash.trim()}`);
                    return res.json({ 
                        received: req.body, 
                        gitUpdate: stdout, 
                        commit: commitHash.trim() 
                    });
                });
            });
        }, 10000); // 10 segundos
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
