# Local Profile Management

This fork of LessPass CLI adds local CSV-based profile management with fzf integration, optimized for Termux.

## Features

- **Local CSV storage**: No cloud connection needed
- **fzf integration**: Quick, interactive profile selection
- **Termux clipboard**: Automatic copy to clipboard on Termux
- **Backward compatible**: Traditional CLI usage still works

## Quick Start

### 1. Create your profiles file

```bash
vim ~/.config/lesspass/profiles.csv
```

Example CSV format:
```csv
site,login,lowercase,uppercase,digits,symbols,length,counter,exclude
github.com,user@email.com,true,true,true,true,16,1,
example.org,admin,true,true,true,false,20,1,
bank.com,myaccount,true,true,true,true,24,1,!@#
```

### 2. Install fzf (if not already installed)

```bash
pkg install fzf
```

### 3. Install the package

```bash
cd /data/data/com.termux/files/home/.local/lesspass/cli
pip install -e .
```

## Usage

### Interactive Mode (with fzf)

```bash
# Show fzf menu to select a profile
lesspass
```

- Use arrow keys or fuzzy search to select a profile
- Press Enter to select
- Enter your master password
- Password is generated, printed, and copied to clipboard

### Quick Search

```bash
# Search for profiles matching "github"
lesspass github
```

- If **one match**: Auto-selects and prompts for master password
- If **multiple matches**: Shows fzf menu to select
- If **no matches**: Falls back to traditional mode (treats "github" as site name)

### List Profiles

```bash
# View all saved profiles
lesspass --list
```

### Traditional Mode (Backward Compatible)

```bash
# Generate password without using profiles
lesspass site login masterpassword

# With options
lesspass github.com user@email.com mymaster --length 20 --no-symbols
```

## CSV Fields

| Field     | Type    | Description                          | Default |
|-----------|---------|--------------------------------------|---------|
| site      | string  | Website/service name (required)      | -       |
| login     | string  | Username/email                       | ""      |
| lowercase | boolean | Include lowercase (a-z)              | true    |
| uppercase | boolean | Include uppercase (A-Z)              | true    |
| digits    | boolean | Include digits (0-9)                 | true    |
| symbols   | boolean | Include symbols (!@#$%...)           | true    |
| length    | integer | Password length (5-35)               | 16      |
| counter   | integer | Password counter (for rotation)      | 1       |
| exclude   | string  | Characters to exclude from password  | ""      |

## Clipboard Support

The tool automatically detects and uses the best clipboard command:

1. **termux-clipboard-set** (Termux on Android) ← **Prioritized**
2. pbcopy (macOS)
3. wl-copy (Wayland on Linux)
4. xsel or xclip (X11 on Linux)
5. clip (Windows)

In profile selection mode, passwords are **automatically copied** to clipboard.

## Advanced Tips

### Editing Profiles

Just edit the CSV file directly:

```bash
vim ~/.config/lesspass/profiles.csv
```

### Custom Profiles Path

```bash
lesspass --profiles ~/my-custom-profiles.csv
```

### Using with Scripts

```bash
# Generate password and pipe to another command
PASSWORD=$(lesspass github.com user@email.com master123)
echo "Password: $PASSWORD"
```

### Version Control

```bash
# You can version control your profiles (but be careful!)
cd ~/.config/lesspass
git init
git add profiles.csv
git commit -m "Add password profiles"
```

**Warning**: Profiles don't contain actual passwords (LessPass is stateless), but they reveal which sites you use.

## Migration from Cloud

If you have profiles saved in the cloud (old LessPass):

1. Export from cloud: `lesspass --save` (saves to `profiles.json`)
2. Manually convert to CSV format
3. Edit `~/.config/lesspass/profiles.csv`

## Troubleshooting

### fzf not found

```bash
pkg install fzf  # Termux
```

### Clipboard not working

Install Termux:API:

```bash
pkg install termux-api
```

### No profiles found

Check file location:

```bash
ls -la ~/.config/lesspass/profiles.csv
```

Create from example:

```bash
cp ~/.config/lesspass/profiles.csv.example ~/.config/lesspass/profiles.csv
```

## Examples

### Basic workflow

```bash
# 1. Edit profiles
vim ~/.config/lesspass/profiles.csv

# 2. Select and generate
lesspass
# (select with fzf, enter master password)

# 3. Paste password where needed
# (already in clipboard!)
```

### Multiple accounts for same site

```csv
github.com,personal@email.com,true,true,true,true,16,1,
github.com,work@company.com,true,true,true,true,20,1,
```

When you run `lesspass github`, fzf will let you choose which account.

### Password rotation

To rotate a password, increment the counter:

```csv
bank.com,myaccount,true,true,true,true,24,2,
```

This generates a different password with the same master password.

## Architecture

```
~/.config/lesspass/
├── profiles.csv          # Your local profiles
├── profiles.csv.example  # Example file (reference)
└── config.json          # Old cloud auth tokens (not used in local mode)
```

New modules:
- `csv_storage.py` - CSV reading and searching
- `fzf_selector.py` - fzf integration
- Modified `core.py` - Profile selection logic
- Modified `clipboard.py` - Termux support
