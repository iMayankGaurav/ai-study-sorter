# 📱 AI Study Note Sorter (DroidRun Agent)

An intelligent automation agent that organizes Android photo galleries by using **Google Gemini 3 Flash** to visually distinguish between "Study Materials" and "Random Photos."

## 🚀 How It Works
This script acts as an autonomous agent that:
1.  **Scans** your Android device via ADB for photos taken in the last 30 days.
2.  **Opens** each photo on the device screen (emulating human interaction).
3.  **Analyzes** the screen content using the **Mobilerun Vision API**.
4.  **Classifies** the image:
    * **STUDY:** Handwritten notes, textbooks, whiteboards, code screens.
    * **OTHER:** Selfies, landscapes, screenshots, random objects.
5.  **Organizes** the files by automatically moving "Study" images to a specific folder.

## 🛠️ Tech Stack
* **Python:** Core logic and automation.
* **ADB (Android Debug Bridge):** Device control (file listing, screen interaction).
* **Mobilerun SDK:** Bridge to LLM agents for mobile UI analysis.
* **Google Gemini 3 Flash:** The Vision LLM used for high-speed, accurate image classification.

## ⚙️ Setup & Installation

1.  **Prerequisites:**
    * Python 3.x installed.
    * `adb` installed and added to your system PATH.
    * An Android device (Physical or Emulator) connected with USB Debugging enabled.

2.  **Install Dependencies:**
    ```bash
    pip install mobilerun
    ```

3.  **Configuration:**
    Open `study_sorter.py` and set your API Key:
    ```python
    os.environ["MOBILERUN_API_KEY"] = "YOUR_MOBILERUN_API_KEY"
    ```

## 🖥️ Usage
Run the script while your Android device is connected:

```bash
python study_sorter.py

The agent will:

    Wake up the device (if using an emulator).

    Launch the gallery for each image.

    Print the AI's classification decision in the console.

    Move valid study notes to /Documents/StudyNotes/.

🧠 Smart Filtering Features
    Date Filtering: Automatically ignores old photos (older than 30 days).