

# ALANX: Intelligent Desktop AI Assistant

ALANX is a premium, AI-powered desktop application designed for seamless interaction with local and remote language models. Built using Python and CustomTkinter, it offers a modern, minimalist interface inspired by industry-leading AI tools.

## Key Features

* **Intelligent History Management:** Persistent conversation threads stored locally, featuring session search, pinning, renaming, and deletion capabilities.


* **Adaptive UI:** A responsive, auto-expanding input field that grows with your text and supports multi-line formatting via `Shift + Enter`.


* **Markdown Support:** Advanced rendering engine that automatically parses Markdown headers and inline bold text, providing a clean, distraction-free reading experience.


* **Smart Layout:** Intelligent auto-scrolling engine ensures your latest messages are always in view during active conversation.


* **Contextual Sidebar:** A dedicated history panel for managing multiple chat threads, featuring right-click context menus for thread maintenance.



## Technical Architecture

ALANX follows a clean MVC-like separation to maintain project scalability:

* **UI Layer (`workspace_view.py`, `ui/chat/history.py`):** Utilizes `customtkinter` for a high-performance, GPU-accelerated modern interface.


* **Data Persistence (`core/database.py`):** Uses SQLite (`alanx_local.db`) to manage sessions and messages with support for lazy-loading and thread state persistence.


* **Rendering Logic:** Implements custom regex parsing to handle complex Markdown structures natively within standard Tkinter widgets.



## Installation & Setup

1. **Clone the Repository:**
```bash
git clone <your-repository-url>
cd ALANX

```


2. **Environment Setup:**
Ensure you are using a Python 3.14+ environment.
```bash
python -m venv venv
source venv/bin/activate  # On Linux/macOS
pip install -r requirements.txt

```


3. **Run the Application:**
```bash
python main.py

```



## Project Structure

* `/core/`: Contains database handlers, configuration, and theme management modules.
* `/ui/`: Contains the interface components, including chat bubbles, sidebar panels, and authentication views.


* `/alanx_local.db`: Local SQLite database file for conversation persistence.

## Troubleshooting

* **Scrolling Issues:** If the interface fails to snap to the bottom, the `_parent_canvas` region is likely being updated before the message card fully renders; ensure `update_idletasks()` is called before `yview_moveto(1.0)`.


* **Rendering Asterisks:** Ensure your Markdown regex (`\*\*(.*?)\*\*`) is set to match across all alphanumeric and punctuation characters to prevent raw symbol leakage in headers.