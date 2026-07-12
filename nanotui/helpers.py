FILE_ICONS = {
    # System & Ordner
    "dir":         {"icon": "", "color": "\033[34m"},   # Blau
    "default":     {"icon": "󰈔", "color": "\033[37m"},   # Weiß
    
    # Programmiersprachen
    ".py":         {"icon": "", "color": "\033[33m"},   # Gelb (Python)
    ".js":         {"icon": "", "color": "\033[33m"},   # Gelb (JavaScript)
    ".ts":         {"icon": "", "color": "\033[34m"},   # Blau (TypeScript)
    ".jsx":        {"icon": "", "color": "\033[36m"},   # Cyan (React JS)
    ".tsx":        {"icon": "", "color": "\033[36m"},   # Cyan (React TS)
    ".c":          {"icon": "", "color": "\033[34m"},   # Blau (C)
    ".cpp":        {"icon": "", "color": "\033[34m"},   # Blau (C++)
    ".h":          {"icon": "", "color": "\033[35m"},   # Magenta (Header)
    ".cs":         {"icon": "󰌛", "color": "\033[35m"},   # Magenta (C#)
    ".java":       {"icon": "", "color": "\033[31m"},   # Rot (Java)
    ".kt":         {"icon": "", "color": "\033[35m"},   # Magenta (Kotlin)
    ".rs":         {"icon": "", "color": "\033[31m"},   # Rot (Rust)
    ".go":         {"icon": "", "color": "\033[36m"},   # Cyan (Go)
    ".php":        {"icon": "", "color": "\033[35m"},   # Magenta (PHP)
    ".rb":         {"icon": "", "color": "\033[31m"},   # Rot (Ruby)
    ".swift":      {"icon": "", "color": "\033[31m"},   # Rot (Swift)
    ".lua":        {"icon": "", "color": "\033[34m"},   # Blau (Lua)
    ".sh":         {"icon": "", "color": "\033[32m"},   # Grün (Shell)
    ".bash":       {"icon": "", "color": "\033[32m"},   # Grün (Bash)
    ".zsh":        {"icon": "", "color": "\033[32m"},   # Grün (Zsh)

    # Web & Style
    ".html":       {"icon": "", "color": "\033[31m"},   # Rot
    ".css":        {"icon": "", "color": "\033[34m"},   # Blau
    ".scss":       {"icon": "", "color": "\033[35m"},   # Magenta
    ".vue":        {"icon": "󰡄", "color": "\033[32m"},   # Grün

    # Bilder / Grafiken
    ".png":        {"icon": "󰋩", "color": "\033[35m"},   # Magenta
    ".jpg":        {"icon": "󰋩", "color": "\033[35m"},   # Magenta
    ".jpeg":       {"icon": "󰋩", "color": "\033[35m"},   # Magenta
    ".gif":        {"icon": "󰋩", "color": "\033[35m"},   # Magenta
    ".svg":        {"icon": "󰜡", "color": "\033[33m"},   # Gelb
    ".ico":        {"icon": "󰋩", "color": "\033[33m"},   # Gelb
    ".webp":       {"icon": "󰋩", "color": "\033[35m"},   # Magenta

    # Dokumente & Text
    ".txt":        {"icon": "󰈙", "color": "\033[37m"},   # Weiß
    ".md":         {"icon": "", "color": "\033[36m"},   # Cyan (Markdown)
    ".pdf":        {"icon": "󰈦", "color": "\033[31m"},   # Rot
    ".doc":        {"icon": "󰈬", "color": "\033[34m"},   # Blau
    ".docx":       {"icon": "󰈬", "color": "\033[34m"},   # Blau
    ".xls":        {"icon": "󰈛", "color": "\033[32m"},   # Grün
    ".xlsx":       {"icon": "󰈛", "color": "\033[32m"},   # Grün
    ".ppt":        {"icon": "󰈔", "color": "\033[31m"},   # Rot
    ".pptx":       {"icon": "󰈔", "color": "\033[31m"},   # Rot

    # Konfiguration & Daten
    ".json":       {"icon": "", "color": "\033[33m"},   # Gelb
    ".yaml":       {"icon": "⚙",  "color": "\033[35m"},   # Magenta
    ".yml":        {"icon": "⚙",  "color": "\033[35m"},   # Magenta
    ".toml":       {"icon": "⚙",  "color": "\033[37m"},   # Weiß
    ".xml":        {"icon": "󰗀", "color": "\033[33m"},   # Gelb
    ".ini":        {"icon": "⚙",  "color": "\033[37m"},   # Weiß
    ".env":        {"icon": "", "color": "\033[33m"},   # Gelb

    # Archive / Komprimiert
    ".zip":        {"icon": "", "color": "\033[33m"},   # Gelb
    ".tar":        {"icon": "", "color": "\033[33m"},   # Gelb
    ".gz":         {"icon": "", "color": "\033[33m"},   # Gelb
    ".7z":         {"icon": "", "color": "\033[33m"},   # Gelb
    ".rar":        {"icon": "", "color": "\033[33m"},   # Gelb

    # Audio & Video
    ".mp3":        {"icon": "󰎈", "color": "\033[36m"},   # Cyan
    ".wav":        {"icon": "󰎈", "color": "\033[36m"},   # Cyan
    ".flac":       {"icon": "󰎈", "color": "\033[36m"},   # Cyan
    ".mp4":        {"icon": "󰕧", "color": "\033[35m"},   # Magenta
    ".mkv":        {"icon": "󰕧", "color": "\033[35m"},   # Magenta
    ".avi":        {"icon": "󰕧", "color": "\033[35m"},   # Magenta

    # Datenbanken & Sonstiges
    ".db":         {"icon": "", "color": "\033[33m"},   # Gelb
    ".sql":        {"icon": "", "color": "\033[33m"},   # Gelb
    ".dockerfile": {"icon": "󰡨", "color": "\033[34m"},   # Blau
    ".gitignore":  {"icon": "", "color": "\033[31m"},   # Rot
}

def get_file_icon(filename: str, is_dir=False):
    if is_dir:
        item = FILE_ICONS["dir"]
    else:
        ext = "." + filename.split(".")[-1] if "." in filename else ""
        item = FILE_ICONS.get(ext, FILE_ICONS["default"])

    return (item["icon"], item["color"])