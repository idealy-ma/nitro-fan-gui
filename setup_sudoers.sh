#!/bin/bash
# Script pour configurer sudoers afin d'exécuter nbfc-safe sans mot de passe

USERNAME=$(whoami)
NBFC_PATH=$(which nbfc-safe)

if [ -z "$NBFC_PATH" ]; then
    echo "Erreur: nbfc-safe n'est pas trouvé dans le PATH"
    exit 1
fi

echo "Configuration de sudoers pour permettre l'exécution de nbfc-safe sans mot de passe"
echo "Utilisateur: $USERNAME"
echo "Chemin nbfc-safe: $NBFC_PATH"
echo ""
echo "Ajout de la règle suivante à /etc/sudoers.d/nbfc-safe:"
echo "$USERNAME ALL=(ALL) NOPASSWD: $NBFC_PATH *"
echo ""

# Créer le fichier sudoersp
SUDOERS_FILE="/etc/sudoers.d/nbfc-safe"
sudo tee "$SUDOERS_FILE" > /dev/null <<EOF
# Permettre l'exécution de nbfc-safe sans mot de passe pour $USERNAME
$USERNAME ALL=(ALL) NOPASSWD: $NBFC_PATH *
EOF

# Vérifier la syntaxe
if sudo visudo -c -f "$SUDOERS_FILE" 2>/dev/null; then
    echo "✓ Configuration réussie!"
    echo "Vous pouvez maintenant exécuter nbfc-safe sans mot de passe."
else
    echo "✗ Erreur dans la configuration sudoers"
    echo "Suppression du fichier créé..."
    sudo rm -f "$SUDOERS_FILE"
    exit 1
fi