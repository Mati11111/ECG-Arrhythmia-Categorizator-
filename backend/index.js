const express = require('express');
const { exec } = require('child_process');
const fetch = require('node-fetch');
const fs = require('fs');

const app = express();
let backendUrl = fs.readFileSync('../processing_data/ngrok_link.txt', 'utf-8').trim();
app.use(express.json());

let receivedMessage = null;

app.post('/', (req, res) => {
    receivedMessage = req.body;
    console.log('Webhook recibido:', receivedMessage);
    const commitMessage = req.body.commits?.[0]?.message || "No commit message";
    console.log('Commit recibido:', commitMessage);
    const predictResultsStatus = receivedMessage.status;
    const predictResultsMessage = receivedMessage.uploaded;

    console.log('Status recibido:', predictResultsStatus);
    console.log('Message recibido:', predictResultsMessage);
    // MESSAGE TO TRIGGER GIT PULL
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
        }, 10000);
    } else {
        res.json({ received: req.body });
    }

    if (predictResultsStatus === "completed") {
        setTimeout(() => {
            console.log("[OK] Ciclo terminado, esperando nueva señal...");
        }, 20000);
        intervalId = setInterval(pollFastAPI, 5000);
    }
});

app.get('/', (req, res) => {
    res.json({ receivedMessage });
});

app.get('/predictionStatus', async (req, res) => {
    try {
        const response = await fetch(`${backendUrl}/predictionStatus`);
        const data = await response.json();

        res.json(data);
    } catch (error) {
        console.error("Error consultando FastAPI o enviando POST:", error);
        res.status(500).json({ error: error.message });
    }
});

app.listen(3333, () => {
    console.log('[OK] BACKEND LISTENING ON PORT 3333');
});

let intervalId = null;

async function pollFastAPI() {
    try {
        const response = await fetch(
            `${backendUrl}/predictionStatus`
        );
        const data = await response.json();
        console.log("[OK] CURRENT PREDICTION STATUS :", data.status.ok);
        console.log("[OK] CURRENT PREDICTION MESSAGE :", data.status.message);

        if (data.status.ok === "Prediction sended") {
            console.log("[OK] PREDICTION DONE, STOPPING POLLING");
        } else {
            console.log("[OK] STARTING PREDICTION");
        }


        await fetch("http://localhost:8000/doPrediction", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data)
        });

        await fetch(`${backendUrl}/resetPredictionStatus`, {
            method: "POST",
            headers: { "Content-Type": "application/json" }
        });

        clearInterval(intervalId);

    } catch (error) {
        console.error("[ERROR] ERROR CHECK BACKEND", error);
    }
}

intervalId = setInterval(pollFastAPI, 5000);
