
<p align="center"> <a href="https://www.python.org"><img src="https://www.python.org/static/img/python-logo.png" alt="Python Logo" width="350"/></a> <a href="https://selenium.dev"><img src="https://selenium.dev/images/selenium_logo_square_green.png" alt="Selenium Logo" width="100"/></a> <a href="https://www.linkedin.com"><img src="https://upload.wikimedia.org/wikipedia/commons/c/ca/LinkedIn_logo_initials.png" alt="LinkedIn Logo" width="50"/></a> </p>


# LinkedIn Easy Apply Bot



![Python](https://img.shields.io/badge/Python-3.8%2B-blue) ![Selenium](https://img.shields.io/badge/Selenium-4.0%2B-orange) ![License](https://img.shields.io/badge/License-MIT-green)

The **LinkedIn Easy Apply Bot** is an advanced automation tool designed to streamline the job application process on LinkedIn. Built with Python and Selenium, this bot automates the tedious task of applying to jobs by filling out forms, submitting applications, and managing job search preferences based on a customizable configuration file. Whether you're a job seeker looking to save time or a developer interested in web automation, this project offers a robust solution with extensive customization options.

---

## Features

- **Automated Job Applications**: Applies to jobs marked "Easy Apply" on LinkedIn with minimal user intervention.
- **Customizable Filters**: Configure job preferences such as location, position, experience level, job type, and more via a YAML file.
- **Form Handling**: Automatically fills text fields, dropdowns, radio buttons, and checkboxes based on predefined personal data and experience.
- **Error Management**: Handles form submission errors, job page refreshes, and application limits gracefully.
- **Logging**: Tracks applied and "Easy Apply" jobs, exporting details to JSON files for record-keeping.
- **Anti-Detection Measures**: Includes options to disable system lock and mimics human-like behaviour with randomized delays.
- **Minimal CSS Footprint**: Uses just ~7 core CSS selectors, dynamically deriving others as needed. This keeps maintenance low even when LinkedIn updates its interface.
- **Extensible**: Modular design allows for easy addition of new features or modifications.

---

## Prerequisites

Before using the bot, ensure you have the following installed:

- **Python 3.8+**: [Download Python](https://www.python.org/downloads/)
- **Google Chrome**: The bot uses Chrome as its browser. [Download Chrome](https://www.google.com/chrome/)
- **ChromeDriver**: Automatically managed via `webdriver_manager`, but ensure compatibility with your Chrome version.
- **Git**: For cloning the repository. [Download Git](https://git-scm.com/downloads)



---

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/linkedin-easy-apply-bot.git
   ```
3. **Content of clone**
   ```
   linkedin-easy-apply-bot/
   ├── config.yaml           # Configuration file config.yaml.example to config.yaml
   ├── main.py               # Main script
   ├── linkedinZero.py       # Core bot logic
   ├── variable_values.py    # CSS selectors for LinkedIn
   ├── requirements.txt      # Dependencies
   ├── export_data/          # Logs and output
   │   ├── apply_status/     # Applied job history
   │   ├── errors/           # Error logs
   │   ├── tempforms/        # Form analysis
   │   └── discard_company/  # Blacklisted companies
   |── README.md             # This file
   |__ css_documents/        # all documents about CSS code locations used
   ```
2. **Install Dependencies**:
   ```bash
   cd linkedin-easy-apply-bot
   ```
    ```bash
   pip install -r requirements.txt
   ```
   
   Contents of `requirements.txt`:
   ```
   selenium==4.8.0
   webdriver_manager==3.8.5
   pyautogui==0.9.53
   pyyaml==6.0
   validate_email==1.3
   ```
3. **Configure the Bot**:
   - Rename config.yaml.example to config.yaml. This file is already located in the root directory of the code, and it’s best to keep it there.
   - If you move it, update the line yaml_file_path = "config.yaml" in main.py to the new path.
   - Edit config.yaml with your LinkedIn credentials, job preferences, and personal details (see Configuration).
   - Place your resume (and optional cover letter) in a directory without spaces (e.g., F:\Myresumes\Resume.pdf).
   - For best results, upload your resume to LinkedIn manually beforehand, as the bot can reuse it and avoid path-related issues.

---

## Usage

1. **Prepare the Configuration**:
   - Edit `config.yaml` with your LinkedIn credentials, job preferences, and personal information.
   - Ensure the file is stored locally and **not uploaded** to any public repository for security.


2. **Set Up Chrome Debugging Profile**:
   - Open Chrome via the command line to enable remote debugging: (Run this code in your terminal)
     ```bash
     "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\selenium-profile"
     ```
   - Keep this Chrome instance open while running the bot.
3. **Log in manually**:
   - To minimize the risk of encountering CAPTCHAs while using the LinkedIn Easy Apply Bot, After launching the Chrome instance, log in to your LinkedIn account manually. Once logged in, navigate away from the page before starting the bot. This prevents the bot from triggering LinkedIn’s automated security checks during login.

3. **Run the Bot**:
   - Open a terminal in the project directory and execute:
     ```bash
     python main.py
     ```
   - The bot will connect to the existing Chrome session, navigate to LinkedIn, and begin applying to jobs.

4. **Monitor Progress**:
   - Check the console for real-time updates on job applications.
   - Review exported JSON files in the `export_files` directory for applied job logs.

5. **Stop the Bot**:
   - Press `Ctrl+C` in the terminal to stop the script gracefully.

---

## Configuration

The bot relies on a `config.yaml` file to define its behavior. Below is a brief overview of key sections:

- **Credentials**:
  ```yaml
  email: your.email@example.com
  password: yourpassword
  ```
  > **Warning**: Keep this file offline and never commit it to version control.

- **Job Filters**:
  ```yaml
  positions:
    - Python Developer
    - Django Developer
  locations:
    - England
  experienceLevel:
    entry: True
    mid-senior level: True
  jobTypes:
    full-time: True
    contract: True
  ```

- **Personal Info**:
  ```yaml
  personalInfo:
    First Name: YourName
    Last Name: YourLastName
    Mobile Phone Number: 1234567890
  experience:
    Python: 8
    Django: 5
    default: 1
  ```

- **Uploads**:
  ```yaml
  uploads:
    resume: F:\Path\To\Resume.pdf
    coverLetter: F:\Path\To\CoverLetter.pdf
  ```

For a full list of configurable options, refer to the [sample config.yaml](config.yaml).

---

## Project Structure

```
linkedin-easy-apply-bot/
├── config.yaml           # Configuration file config.yaml.example to config.yaml
├── main.py               # Main script
├── linkedinZero.py       # Core bot logic
├── variable_values.py    # CSS selectors for LinkedIn
├── requirements.txt      # Dependencies
├── export_data/          # Logs and output
│   ├── apply_status/     # Applied job history
│   ├── errors/           # Error logs
│   ├── tempforms/        # Form analysis
│   └── discard_company/  # Blacklisted companies
|── README.md             # This file
|__ css_documents/        # all documents about CSS code locations used
```

---

## How It Works

1. **Browser Initialization**: Connects to an existing Chrome session with remote debugging enabled.
2. **Job Search**: Constructs a LinkedIn job search URL based on `config.yaml` filters.
3. **Job Listing Scraping**: Scrolls through job listings and identifies "Easy Apply" opportunities.
4. **Form Filling**: Extracts form elements (text fields, dropdowns, etc.) and populates them with user data.
5. **Submission**: Submits applications and logs results, handling errors or verification prompts as needed.
6. **Looping**: Moves to the next job page and repeats until interrupted or no jobs remain.

---

## Troubleshooting

- **"Cannot connect to Chrome"**:
  - Ensure Chrome is running with the `--remote-debugging-port=9222` flag.
  - Verify the port is not blocked by a firewall.

- **"Element not found"**:
  - LinkedIn’s UI may have changed. Update the CSS selectors in `css_codes.py`.

- **"Form filling failed"**:
  - Check `config.yaml` for missing or incorrect data.
  - Enable `maintenance: True` in `linkedinZero.py` for detailed debugging logs.

- **"Too many requests"**:
  - LinkedIn may detect automation. Increase delays in the code or use a VPN.

---

## Contributing

Contributions are welcome! To contribute:

1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/YourFeature`).
3. Commit your changes (`git commit -m "Add YourFeature"`).
4. Push to the branch (`git push origin feature/YourFeature`).
5. Open a Pull Request.

Please ensure your code follows PEP 8 guidelines and includes appropriate comments.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Disclaimer

This tool is intended for personal use and educational purposes only. Automated job applications may violate LinkedIn’s Terms of Service. Use at your own risk. The author is not responsible for any account restrictions or legal consequences resulting from its use.

---

## Contact

For questions or suggestions, feel free to open an issue or reach out via [your.email@example.com](mailto:your.email@example.com).

Happy job hunting!

---

### Notes for Customization
- Replace `yourusername` with your GitHub username in the clone URL.
- Update the email placeholders (`your.email@example.com`) with your contact info.
- If you add a `LICENSE` file, link it in the README.
- Adjust paths (e.g., `F:\Python\Selenium\`) to reflect your local setup.

This README is professional, detailed, and user-friendly, making it suitable for a public repository. Push this along with your five files (`main.py`, `linkedinZero.py`, `config.yaml`, `css_codes.py`, and `requirements.txt`) to your GitHub repository for a polished presentation!
