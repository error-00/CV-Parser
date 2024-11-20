# Job Resume Finder Telegram Bot

This project is a Telegram bot that allows users to search for resumes based on job position, location, experience, and salary range. The bot fetches resumes from popular Ukrainian job sites (Work.ua, Robota.ua) and provides the relevant information such as title, salary, personal info, location, and more.

## Features

- Allows users to select a job site (Work.ua, Robota.ua, or All).
- Prompts users to enter details such as job position, location, experience level, and salary range.
- Fetches resumes based on the user’s input and displays the results.
- Provides a simple and interactive way to search for resumes.

## Requirements

- Python 3.7+
- Required Python libraries (listed below)

## Libraries:

  - `python-telegram-bot` — For interacting with the Telegram API.
  - `requests` — For sending HTTP requests to fetch resume data from job sites.
  - `selenium` — For web scraping of job listings that may require interaction with dynamic pages (e.g., JavaScript rendering).
  - `resume-parser` — For parsing and processing resumes from fetched data.
  - `config` — For securely storing sensitive information like the Telegram bot token.

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/your-repository/job-resume-finder-bot.git
cd job-resume-finder-bot
```

### 2. Install Required Libraries

Ensure you have pip installed and then install the required dependencies:
```bash
pip install -r requirements.txt
```

### 3. Set Up Your Telegram Bot

To interact with the bot, you need to create a bot using **BotFather** on Telegram and get your bot’s token:

1. Go to Telegram and search for **BotFather**.
2. Start a conversation with **BotFather** and type `/newbot`.
3. Follow the instructions to create your bot.
4. Once your bot is created, you will receive a token. Copy this token.
5. In the `config.py` file, replace `TELEGRAM_TOKEN` with the token you received from **BotFather**:

### 4. Configure the Token

In the config.py file, replace TELEGRAM_TOKEN with the token you received from BotFather:

```bash
TELEGRAM_TOKEN = 'your-bot-token-here'
```

### 5. Run the Bot

Once the configuration is complete, you can run the bot using:

```bash
python bot.py
```

The bot will start running and will respond to users as they interact with it.

## Usage

1. **Start the Bot**  
   Type `/start` to begin interacting with the bot. You’ll be prompted to choose a job site (Work.ua, Robota.ua, or All).

2. **Enter Job Details**  
   The bot will ask you for the following details:
   - Job position
   - Location
   - Experience level
   - Salary range

   You can skip any field by typing `-`.

3. **View Resumes**  
   Once all the information is provided, the bot will search for relevant resumes and display the results. Each resume will show:
   - Job title
   - Salary
   - Personal information
   - Location
   - Link to the resume
   - Score of relevance

4. **Help Command**  
   Use `/help` for basic instructions on how to start the bot.

## Example Interaction

1. **Bot:** Choose a job site:
   - Work.ua
   - Robota.ua
   - All

2. **User:** Select a job site, e.g., “Work.ua”

3. **Bot:** Please enter the job position you are looking for:  
   **User:** Software Developer

4. **Bot:** Please enter the location (optional, write `-`):  
   **User:** Kyiv

5. **Bot:** Please enter the experience level/range (optional, write `-`):  
   **User:** 2-5

6. **Bot:** Please enter the salary range (optional, write `-`):  
   **User:** 30000-50000
### 7.	Bot: Fetching resumes for “Software Developer”…
Bot: Displays the top resumes
