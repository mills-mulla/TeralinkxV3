#!/bin/bash

echo "╔════════════════════════════════════════════════════════════╗"
echo "║         Git Authentication Setup (Personal Token)          ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Step 1: Configure user
echo "Step 1: Configure Git User"
echo "───────────────────────────"
read -p "Enter your Git username: " git_username
read -p "Enter your Git email: " git_email

git config --global user.name "$git_username"
git config --global user.email "$git_email"

echo ""
echo "✅ Git user configured"
echo ""

# Step 2: Get token
echo "Step 2: Get Personal Access Token"
echo "──────────────────────────────────"
echo "1. Open: https://github.com/settings/tokens"
echo "2. Click 'Generate new token (classic)'"
echo "3. Name: TeralinkxV3"
echo "4. Select: ✓ repo, ✓ workflow"
echo "5. Click 'Generate token'"
echo "6. Copy the token (starts with ghp_...)"
echo ""
read -p "Paste your token here: " token

# Save token
git config --global credential.helper store
echo "https://$git_username:$token@github.com" > ~/.git-credentials
chmod 600 ~/.git-credentials

echo ""
echo "✅ Token saved!"
echo ""
echo "Now you can push:"
echo "  git add ."
echo "  git commit -m 'Your message'"
echo "  git push"
