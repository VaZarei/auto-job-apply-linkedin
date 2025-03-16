
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
3. **The content after clone:(Project Structure)**
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
   │   |── discard_company/  # Blacklisted companies
   |   |__ uncover_questions # collect uncover questions
   |── README.md             # This file
   |__ css_documents/        # All documents about CSS code locations used
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

You can find `config.yaml.example` in the root directory; please rename it to `config.yaml`.
The bot relies on a `config.yaml` file to define its behavior. Below is a brief overview of key sections:

- **Credentials**:
  ```yaml
  email: your.email@example.com
  password: yourpassword
  ```
  > **Warning**: Keep the item unchanged because logging in is done manually after opening the Chrome instance for debugging.
  
- **Job Filters**:
  ```yaml
  positions:
    - Python Developer
    - Django Developer
  locations:
    - England
  experienceLevel:
    entry: False
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
    AI: 2
    Artificial Intelligence: 2
    Full Stack Developer: 5
    Fast API: 4
    MySql: 7
    
    default: 1
  ```

- **Uploads**:
  ```yaml
  uploads:
    resume: F:\Path\To\Resume.pdf
    coverLetter: F:\Path\To\CoverLetter.pdf
  ```

For a full list of configurable options, refer to `config.yaml.example` in te root.




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
  - Check  `config.yaml` for missing or incorrect data.
  - Enable `self.log_main_functions_flag = True` in `linkedinZero.py` for detailed debugging logs about main functions.
  - Enable `self.log_submain_functions_flag` in `linkedinZero.py` for detailed debugging logs about submain functions.
  - Enable `self.log_more_informations_flag` in `linkedinZero.py` for checking the apply process in the background with details.
  - Enable `self.log_error_message_flag` in `linkedinZero.py` for printing detailed debugging logs in the console.
  - Check  `error_log.txt` file in `export_data\errors\` for tracking lines with error

- **"Too many requests"**:
  - LinkedIn may detect automation. please continue in the next day.

---
Here’s the refined **Future Works** section in GitHub Markdown format, based on your README, with lines 2 and 3 swapped as requested. I’ve kept the structure clean and consistent with GitHub styling.

---

## Future Works

The LinkedIn Easy Apply Bot is poised for exciting enhancements, and I’m eager to expand its capabilities with these goals. These features aim to make the bot smarter, more engaging, and accessible—whether developed by me or with the help of contributors. Here’s what’s on the horizon:

1. **AI-Powered Question Answering**: Integrate a local AI to answer job application questions intelligently, requiring minimal hardware resources. (I’m actively working on this for an upcoming release—stay tuned for a new version!)
2. **Personalized Outreach**: Automatically send tailored messages to hiring managers, including a dedicated cover letter based on the job description and the applicant’s resume, to boost engagement and visibility.
3. **Smarter Job Matching**: Enhance job collection by matching opportunities more closely to the user’s resume, storing links, company names, and job descriptions in the `export_data` folder for better tracking and analysis.
4. **Networking Automation**: Identify two employees from the target company in related roles and send them personalized messages about the job application, highlighting the applicant’s resume and fit for the position.
5. **Mobile Deployment**: Enable the bot to run on a smartphone as a lightweight server via Termux, minimizing hardware demands for broader accessibility. (I’m currently exploring this to make the project as portable as possible.)

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




## Acknowledgments

A heartfelt thank you to everyone who has inspired and supported the development of the **LinkedIn Easy Apply Bot**. This project wouldn’t be possible without:

- **The Open-Source Community**: For the incredible tools that power this bot, especially [Python](https://www.python.org/) for its versatility, [Selenium](https://selenium.dev/) for robust web automation, and [PyYAML](https://pyyaml.org/) for seamless configuration management.
- **Contributors**: To those who will join this journey, your ideas, code, and feedback will shape the future of this tool. Your contributions are deeply valued.
- **Job Seekers & Developers**: Your real world needs and curiosity about automation sparked this project. This bot is built for you.
- **LinkedIn Team**: For providing a platform that connects job seekers with opportunities, making tools like this bot possible and meaningful.
- **Original Developer**: [Nathan Duma](https://github.com/NathanDuma) with [NathanDuma/LinkedIn-Easy-Apply-Bot](https://github.com/NathanDuma/LinkedIn-Easy-Apply-Bot). I initially worked with Nathan’s bot, but after it stopped functioning, I drew inspiration from his work to create this new version. About 10% of the current codebase builds on his foundation, though I’ve added my own ideas and plan to fully reimagine it in future releases. Huge thanks to Nathan Duma.

Special appreciation goes to the countless cups of coffee ☕ and late-night coding sessions that fueled version 1.0.0. Here’s to building something impactful together!


---
