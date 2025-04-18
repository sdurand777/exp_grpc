
const express = require('express');
const path = require('path');
const app = express();

// Servez les fichiers statiques du dossier "public"
app.use(express.static(path.join(__dirname, 'public')));

// Route principale pour servir le fichier HTML
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// Démarrez le serveur
const port = 3000;
app.listen(port, () => {
  console.log(`Server is running on http://localhost:${port}`);
});
