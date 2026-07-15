# core/theme.py

# --- 1. PREMIUM DARK ELEVATION LAYERS ---

COLOR_BACKGROUND = "#000000"       # Deepest level (Main Window canvas)
COLOR_SIDEBAR_BG = "#09090B"       # Level 1 (Slightly lighter translucent feel)
COLOR_CONTAINER_BG = "#121214"     # Level 2 (The main chat bounding surface)
COLOR_SURFACE_ELEVATED = "#1C1C1F" # Level 3 (Input bars, context menus, code headers)

# --- 2. THE CHOSEN BRAND PALETTE ---
COLOR_PRIMARY = "#9929EA"          # Purple Accent (Borders, AI Identity, Primary Buttons)
COLOR_ACCENT = "#FF5FCF"           # Pink Accent (Destructive items, active alerts, error glows)
COLOR_HIGHLIGHT = "#FAEB92"        # Soft Gold (User interaction, Action triggers, sending icons)

# --- 3. STATE AND NEUTRAL TINTS ---
COLOR_TEXT_MAIN = "#F4F4F5"        # Premium off-white to reduce eye strain
COLOR_TEXT_MUTED = "#8E8E93"       # Secondary text for timestamps and thinking labels
COLOR_BORDER_SUBTLE = "#27272A"    # Minimal separation lines for fields

# --- 4. PREMIUM TYPOGRAPHY MATRIX ---
FONT_DISPLAY = ("Helvetica", 32, "bold")
FONT_TITLE = ("Helvetica", 20, "bold")
FONT_HEADING = ("Helvetica", 16, "bold")
FONT_BODY = ("Helvetica", 15, "normal")
FONT_CODE = ("Courier", 14, "normal")
# --- 5. UNIFIED SPACING & RADIUS SYSTEM ---
RADIUS_PREMIUM = 16                # Standard corner smoothing across UI blocks
RADIUS_PILL = 28                   # Perfect capsule shape for inputs/login pills

PADDING_SMALL = 8
PADDING_MEDIUM = 16
PADDING_LARGE = 24