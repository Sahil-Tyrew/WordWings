WordWings - Reading Support Tool

    WordWings is a desktop application that is built with Python and Tkinter that provides reading assistance for users with dyslexia or other reading difficulties. It offers text simplification, text chunking, text-to-speech with word highlighting, voice command support, and OCR extraction from images and PDFs. 


Features:

    Text Simplification:

        Rule based simplification using a custom dictionary.

        AI-based simplification - used with OpenAI GPT-3.5-turbo (toggleable).


    Chunking Text (Split Paragraph)

        Splits long text into smaller chunks at sentence boundaries, with fallback to word-level splitting when needed.


    Reading Aloud:

        Text-to-speech playback of the text.

        Word-by-word highlighting with adjustable highlight color (Available for more with simple code additions)


    Voice Commands:

        Start and Stop recording voice commands to trigger “simplify” or “read” actions.

    OCR Extraction (Gets Text from Image/PDF provided by user):

        Extracts text from image files (PNG, JPG, JPEG, BMP, TIFF) and PDFs using Tesseract and Poppler.


    Customizable GUI (user interface)

        Change font between Arial, Times New Roman, and OpenDyslexic (if installed, has intruction to install)

        Switch background color between White, Light Blue, Soft Yellow, and Pastel Pink.

        (More options can be added with very easy additional code)


    Chrome Extension Integration:

        WordWings is also available as a Chrome Extension, which allows users to read aloud, chunk, and simplify selected text directly within web pages. Also has a pop up menu when extension is clicked by the user, where they can write or paste text that allows them to simplify, read, or chunk, right on Google Chrome

        The extension uses similar AI-based and rule-based simplification engines and communicates with the core Python backend when needed.

        Supports highlighting and easy integration with browser workflows.


Installation:

    1. CLone the Repository:

        # Replace <your_github_username> with your GitHub username or organization name

        git clone https://github.com/<your_github_username>/wordwings.git
        cd wordwings


    2. Create and Activate the Virtual Enviornment:

        ```bash
        python3 -m venv venv
        source venv/bin/activate   # macOS/Linux
        venv\Scripts\activate    # Windows
        ```

    3. Install the Python Dependencies 

        pip install -r requirements.txt

    
    4. Install System Dependencies:

        Tesseract OCR:
            macOS: brew install tesseract
            Windows: Download installer from https://github.com/tesseract-ocr/tesseract
    
        Poppler (for PDF OCR):
            macOS: brew install poppler
            Windows: Download binaries from http://blog.alivate.com.au/poppler-windows/ and add to your PATH.


Usage: 

    Desktop App:

    python wordwings.py OR wordwings_app.py - in the terminal or code app that is being used - i.e. Visual Studio Code

            1. Enter or paste text into the main text box.

            2. Click Simplify Text for rule-based simplification, or check Use AI Simplification and click again to use GPT-3.5.

            3. Click Split Text to break long paragraphs into manageable chunks.

            4. Click Read Aloud to hear the text with word-by-word highlighting.

            5. Use Start Voice Recording / Stop Voice Recording and say “simplify” or “read” to control actions by voice.

            6. Click Extract Text from Image to select an image or PDF and load its text via OCR.

    Chrome Extension:

        1. Navigate to chrome://extensions in your browser.

        2. Enable Developer mode.

        3. Click Load unpacked and select the chrome_extension folder.

        4. Highlight text on any webpage and click the extension to simplify or read aloud.

        5. Ensure your backend is running locally if connected to Python APIs.


Configuration:

    User - Set your OpenAI API key:
        # Replace with your own OpenAI API key
        export OPENAI_API_KEY=your_actual_api_key


    - If Poppler is installed in a non-default location, update the `poppler_path` variable inside `image_to_text()`.

