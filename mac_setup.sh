#!/bin/bash

# ============================== CONFIGURAÇÕES PADRÃO ==============================
ZED_SETTINGS=$(cat << 'EOF'
// Zed settings
//
// For information on how to configure Zed, see the Zed
// documentation: https://zed.dev/docs/configuring-zed
//
// To see all of Zed's default settings without changing your
// custom settings, run `zed: open default settings` from the
// command palette (cmd-shift-p / ctrl-shift-p)
{
  "minimap": {
    "show": "auto"
  },
  "git": {
    "inline_blame": {
      "enabled": false,
      "delay_ms": 0,
      "padding": 7,
      "min_column": 0,
      "show_commit_summary": false
    }
  },
  "buffer_font_family": "CommitMono Nerd Font Mono",
  "ui_font_family": "CommitMono Nerd Font",
  "telemetry": {
    "metrics": false
  },
  "ui_font_size": 14.0,
  "buffer_font_size": 15,
  "theme": {
    "mode": "system",
    "light": "Catppuccin Mocha",
    "dark": "Catppuccin Mocha"
  },
  "autosave": {
    "after_delay": {
      "milliseconds": 2000
    }
  }
}
EOF
)

EDITOR_KEYMAPS=$(cat << 'EOF'
[
  {
    "context": "Pane",
    "bindings": {
      "ctrl-[": "pane::GoBack",
      "ctrl-]": "pane::GoForward"
    }
  }
]
EOF
)

GHOSTTY_SETTINGS=$(cat << 'EOF'
theme = catppuccin-mocha.conf
font-family = CommitMono Nerd Font
font-size = 14
background-opacity= 0.9
cursor-click-to-move = true
maximize = true
title = ""
bell-features = system, attention
auto-update = download
EOF
)

TMUX_SETTINGS=$(cat << 'EOF'
# List of plugins =============================================================
set -g @plugin 'tmux-plugins/tpm'
set -g @plugin 'tmux-plugins/tmux-sensible'
set -g @plugin 'catppuccin/tmux#v2.1.3'

# General config ==============================================================
set -g mouse on

set -g base-index 1
set -g pane-base-index 1
set-window-option -g pane-base-index 1
set-option -g renumber-windows on

# Visual Config ===============================================================
set -g @catppuccin_window_number_position "left"
set -g @catppuccin_window_middle_separator ""
set -g @catppuccin_status_left_separator "█"
set -g @catppuccin_status_right_separator "█"

set -g @catppuccin_window_current_text " #{window_name}"
set -g @catppuccin_window_text " #{window_name}"

set -g @catppuccin_window_default_fill "number"
set -g @catppuccin_window_current_fill "number"

set -g status-right "#{E:@catppuccin_status_session}#{E:@catppuccin_status_date_time}#{E:@catppuccin_status_host}"

set -g @catppuccin_date_time_text "%H:%M %d/%m"

# Mappings ====================================================================
# C == ctrl
bind C-r source-file ~/.tmux.conf

bind c new-window -c "#{pane_current_path}"
bind '_' split-window -vc "#{pane_current_path}"
bind '|' split-window -hc "#{pane_current_path}"

# Initialize TPM (keep at the very bottom of tmux.conf) =======================
run '~/.tmux/plugins/tpm/tpm'
EOF
)

TMUX_AUTO_ATTACH=$(cat << 'EOF'
if [ -z "\$TMUX" ]; then
    # do nothing
elif tmux has-session -t 0 2>/dev/null; then
    if [[ "$(tmux list-clients -t 0)" == *"attached"* ]]; then
        # do nothing
    else
        ta
        # tmux attach -t 0
    fi
else
    tmux new-session -s 0 -d
    tmux split-window -h -t 0
    tmux split-window -v -t 0.1
    tmux resize-pane -t 0.1 -x 80 -y 24
    tmux send-keys -t 0.1 "btop" C-m
    tmux send-keys -t 0.2 "nu" C-m
    tmux attach-session -t 0:1.2
fi
EOF
)

# ==================================================================================

echo "Iniciando a configuração da máquina..."

CPU_CORES=$(sysctl -n hw.ncpu)
echo "CPU_CORES: $CPU_CORES"
if [[ "$(cat ~/.zshrc)" == *"HOMEBREW_MAKE_JOBS"* ]]
then
  echo "HOMEBREW_MAKE_JOBS: $HOMEBREW_MAKE_JOBS"
else
    if [ "$CPU_CORES" -gt 8 ]; then
        echo Setting HOMEBREW_MAKE_JOBS: $(($CPU_CORES-4))
        echo export HOMEBREW_MAKE_JOBS=$(($CPU_CORES-4)) >> ~/.zshrc
    elif [ "$CPU_CORES" -gt 4 ]; then
        echo Setting HOMEBREW_MAKE_JOBS: $(($CPU_CORES-2))
        echo export HOMEBREW_MAKE_JOBS=$(($CPU_CORES-2)) >> ~/.zshrc
    else
        echo Setting HOMEBREW_MAKE_JOBS: $CPU_CORES
        echo export HOMEBREW_MAKE_JOBS=$CPU_CORES >> ~/.zshrc
    fi
    source ~/.zshrc
fi

if ! command -v xcode-select -p &> /dev/null
then
    echo "Instalando XCode cli tools"
    xcode-select --install
    sudo xcodebuild -license accept
fi

if ! command -v brew &> /dev/null
then
    echo "Homebrew não encontrado. Instalando..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    source ~/.zshrc
    echo "Homebrew instalado com sucesso!"
fi

echo "Atualizando Homebrew..."
brew update

echo "Instalando Ferramentas CLI..."
brew install git openjdk gcc uv tmux btop htop fzf nushell

echo "Configurando as variáveis de ambiente para Java..."
echo 'export PATH="/usr/local/opt/openjdk/bin:$PATH"' >> ~/.zshrc
echo 'export JAVA_HOME="/usr/local/opt/openjdk"' >> ~/.zshrc
echo 'export PATH="/usr/local/opt/openjdk/bin:$PATH"' >> ~/.zshrc
# For compilers to find openjdk you may need to set:
export CPPFLAGS="-I/usr/local/opt/openjdk/include"

source ~/.zshrc

# ==> Caveats
# For the system Java wrappers to find this JDK, symlink it.
# openjdk is keg-only, which means it was not symlinked into /usr/local,
# because macOS provides similar software and installing this software in
# parallel can cause all kinds of trouble.
java -version
if [ $? -ne 0 ]; then
    echo -e "\e[1;33m ATENÇÃO: Criado symlink do java para o OpenJDK! \a\e[0;0m"
    sudo ln -sfn /usr/local/opt/openjdk/libexec/openjdk.jdk /Library/Java/JavaVirtualMachines/openjdk.jdk
fi

if ! command -v cat .zshrc.pre-oh-my-zsh &> /dev/null
then
    echo "Instalando Oh My ZSH!..."
    sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
    sed -i 's/plugins=(git)/plugins=(git tmux)/g' ~/.zshrc
    echo "$TMUX_AUTO_ATTACH" >> ~/.zshrc
    source ~/.zshrc
fi

echo "Instalando Ferramentas de Desenvolvimento"
brew install --cask visual-studio-code zed iterm2 ghostty docker font-commit-mono-nerd-font

echo "Instalando Google Chrome..."
brew install --cask google-chrome

echo "Instalando Utilidades do MacOS"
brew install --cask raycast hiddenbar stats

echo "Verificando as instalações..."
echo "Versão do Git:"
git --version

echo "Versão do Java:"
java -version

echo "Versão do C++ (g++):"
g++ --version

source ~/.zshrc

echo "---"
echo "Instalações concluídas, iniciando configuração!"
echo "---"

echo "Configurando ZED..."
echo "$ZED_SETTINGS" >> ~/.config/zed/settings.json
echo "$EDITOR_KEYMAPS" >> ~/.config/zed/keymap.json

echo "Configurando Ghostty"
echo "$GHOSTTY_SETTINGS" >> ~/.config/ghostty/config
echo "palette = 0=#45475a
palette = 1=#f38ba8
palette = 2=#a6e3a1
palette = 3=#f9e2af
palette = 4=#89b4fa
palette = 5=#f5c2e7
palette = 6=#94e2d5
palette = 7=#a6adc8
palette = 8=#585b70
palette = 9=#f38ba8
palette = 10=#a6e3a1
palette = 11=#f9e2af
palette = 12=#89b4fa
palette = 13=#f5c2e7
palette = 14=#94e2d5
palette = 15=#bac2de
background = 1e1e2e
foreground = cdd6f4
cursor-color = f5e0dc
cursor-text = 11111b
selection-background = 353749
selection-foreground = cdd6f4" >> ~/.config/ghostty/themes/catppuccin-mocha.conf

echo "Configurando Tmux..."
if [! -d ~/.tmux/plugins/tpm]
then
    git clone https://github.com/tmux-plugins/tpm ~/.tmux/plugins/tpm
fi

if [-f ~/.tmux.conf]
then
    echo "Configuração do Tmux existente, alteração não realizada"
else
    echo "$TMUX_SETTINGS" >> ~/.tmux.conf
fi

echo "Configurando Dock..."
# "docker "factory" reset":
# defaults delete com.apple.dock; killall Dock
defaults -currentHost write com.apple.dock autohide -bool TRUE
defaults -currentHost write com.apple.dock largesize -integer 128
defaults -currentHost write com.apple.dock show-recents -bool FALSE
defaults -currentHost write com.apple.dock tile-size -integer 38
defaults -currentHost write com.apple.dock magnification -bool FALSE

defaults -currentHost write com.apple.dock persistent-apps -array
# Launchpad
defaults -currentHost write com.apple.dock persistent-apps -array-add '<dict><key>tile-data</key><dict><key>file-data</key><dict><key>_CFURLString</key><string>/System/Applications/Launchpad.app</string><key>_CFURLStringType</key><integer>0</integer></dict></dict></dict>'
# Safari
defaults -currentHost write com.apple.dock persistent-apps -array-add '<dict><key>tile-data</key><dict><key>file-data</key><dict><key>_CFURLString</key><string>/Applications/Safari.app</string><key>_CFURLStringType</key><integer>0</integer></dict></dict></dict>'
# Chrome
defaults -currentHost write com.apple.dock persistent-apps -array-add '<dict><key>tile-data</key><dict><key>file-data</key><dict><key>_CFURLString</key><string>/Applications/Google Chrome.app</string><key>_CFURLStringType</key><integer>0</integer></dict></dict></dict>'
# Calendar
defaults -currentHost write com.apple.dock persistent-apps -array-add '<dict><key>tile-data</key><dict><key>file-data</key><dict><key>_CFURLString</key><string>/System/Applications/Calendar.app</string><key>_CFURLStringType</key><integer>0</integer></dict></dict></dict>'
# Reminders
defaults -currentHost write com.apple.dock persistent-apps -array-add '<dict><key>tile-data</key><dict><key>file-data</key><dict><key>_CFURLString</key><string>/System/Applications/Reminders.app</string><key>_CFURLStringType</key><integer>0</integer></dict></dict></dict>'
# Notes
defaults -currentHost write com.apple.dock persistent-apps -array-add '<dict><key>tile-data</key><dict><key>file-data</key><dict><key>_CFURLString</key><string>/System/Applications/Notes.app</string><key>_CFURLStringType</key><integer>0</integer></dict></dict></dict>'
# VS Code
defaults -currentHost write com.apple.dock persistent-apps -array-add '<dict><key>tile-data</key><dict><key>file-data</key><dict><key>_CFURLString</key><string>/Applications/Visual Studio Code.app</string><key>_CFURLStringType</key><integer>0</integer></dict></dict></dict>'
# Zed
defaults -currentHost write com.apple.dock persistent-apps -array-add '<dict><key>tile-data</key><dict><key>file-data</key><dict><key>_CFURLString</key><string>/Applications/Zed.app</string><key>_CFURLStringType</key><integer>0</integer></dict></dict></dict>'
# iTerm2
defaults -currentHost write com.apple.dock persistent-apps -array-add '<dict><key>tile-data</key><dict><key>file-data</key><dict><key>_CFURLString</key><string>/Applications/iTerm.app</string><key>_CFURLStringType</key><integer>0</integer></dict></dict></dict>'
# Restart to apply
killall Dock

echo "Personalizando o Sistema..."
sudo pmset displaysleep 10
defaults write com.apple.ScreenSaver idleTime -300
defaults write com.apple.ScreenSaver askForPassword -int 1
defaults write NSGlobalDomain AppleInterfaceStyle Dark
defaults write -g com.apple.swipescrolldirection -bool FALSE

echo -e "\e[1;33m \aATENÇÃO: CMD+Space desativado, atribua o atalho ao Raycast manualmente! \e[0;0m"
/usr/libexec/PlistBuddy -c "Delete :AppleSymbolicHotKeys:64" ~/Library/Preferences/com.apple.symbolichotkeys.plist
killall SystemUIServer
open -a raycast

echo -e "\e[0;36m---"
echo "Configuração concluída!"
echo "--- \a\e[0;0m"
