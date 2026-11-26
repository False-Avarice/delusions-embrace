# Delusions Embrace

**Delusions Embrace** is an atmospheric, text-based psychological horror game. You play as a protagonist grappling with sanity.



## Getting Started

Follow these instructions to get the game running on your local machine.

### Prerequisites

- Python 3.x installed on your system.

### Installation

1.  **Clone the repository** (or download the source code):
    ```bash
    https://github.com/False-Avarice/delusions-embrace
    cd delusions-embrace
    ```

2.  **Create a virtual environment** (recommended to avoid dependency conflicts):
    ```bash
    python3 -m venv venv
    ```

3.  **Activate the virtual environment**:
    -   On macOS/Linux:
        ```bash
        source venv/bin/activate
        ```
    -   On Windows:
        ```bash
        venv\Scripts\activate
        ```

4.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

### Playing the Game

#### Web Version (Recommended)
The web version includes CRT effects and animated text. Select **Reveal passage** to read the full passage immediately.
Use the **Sound** button to enable or mute the rain, room ambience, and story effects.

1.  Start the Flask development server. It listens on localhost with debug mode disabled.
    ```bash
    python3 app.py
    ```
2.  Open your web browser and navigate to:
    `http://127.0.0.1:8000`

#### Terminal Version
A pure text-based experience running directly in your command line.

1.  Run the main script:
    ```bash
    python3 main.py
    ```

    Use `python3 main.py --instant` to show each passage immediately.

## Audio credits

The rain was recorded by alex36917 and edited for Blanket by Porrumentzio under Creative Commons Attribution (CC BY). For this game, a stereo excerpt was trimmed, equalized, crossfaded into a loop, and encoded as MP3. [Original recording](https://freesound.org/people/alex36917/sounds/524605/) · [Blanket credits and licensing](https://github.com/rafaelmardojai/blanket/blob/2eaca9ba5a1b624adf90b6ccee1008efc46f0273/SOUNDS_LICENSING.md)
