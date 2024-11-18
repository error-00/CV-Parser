from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def parse_experience_range(experience_range):
    # Initialize an empty list to store the experience values
    experience_values = []

    # Check if the input contains a hyphen (indicating a range)
    if "-" in experience_range:
        start, end = experience_range.split("-")
        start = int(start)
        end = int(end)

        for i in range(start, end + 1):
            if i == 1:
                experience_values.append(
                    1
                )  # "До 1 року" - this corresponds to the code 1
            elif i == 2:
                experience_values.append(
                    164
                )  # "Від 1 до 2 років" - this corresponds to the code 164
            elif i == 3:
                experience_values.append(
                    165
                )  # "Від 2 до 5 років" - this corresponds to the code 165
            elif i >= 4:
                experience_values.append(
                    166
                )  # "Більше 5 років" - this corresponds to the code 166
    else:
        # If no range is provided, convert the input into an integer and add to the list
        experience_values.append(int(experience_range))

    return experience_values


class ResumeParser:
    def __init__(self, driver_path):
        # Initialize Selenium WebDriver with headless Chrome options
        self.options = Options()
        self.options.add_argument("--headless")  # No GUI
        self.options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
        self.options.add_argument("--disable-javascript")
        self.driver = webdriver.Chrome(
            service=Service(driver_path), options=self.options
        )

    def parse_work_ua(self, job_position, location=None, experience=None, salary=None):
        # Generate URL for searching resumes on work.ua based on the job position
        url = f"https://www.work.ua/resumes-{f'{location.lower()}-' if location else ''}{job_position.replace(' ', '+').lower()}/"
        if experience:
            experience_value = parse_experience_range(experience)
            experience_filter = "+".join(map(str, experience_value))
            url += f"?experience={experience_filter}"

        try:
            print(f"Loading URL: {url}")
            self.driver.get(url)
        except Exception as e:
            print(f"Error loading URL: {e}")
            return []

        resumes = []
        try:
            # Wait until resume cards are loaded on the page
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "resume-link"))
            )
            cards = self.driver.find_elements(By.CSS_SELECTOR, ".card.resume-link")

            for card in cards:
                try:
                    title = card.find_element(By.CSS_SELECTOR, "h2 a").text.strip()

                    try:
                        # Extracting name
                        name_element = card.find_element(
                            By.CSS_SELECTOR, "p.mt-xs.mb-0 .strong-600"
                        )
                        name = name_element.text.strip()
                    except:
                        name = None

                    try:
                        # Extract age, if exists
                        age_element = card.find_element(
                            By.CSS_SELECTOR, "p.mt-xs.mb-0 span:nth-child(2)"
                        )
                        age = age_element.text.strip()
                    except:
                        age = None

                    try:
                        # Extract city
                        city_element = card.find_element(
                            By.CSS_SELECTOR, "p.mt-xs.mb-0 span:nth-child(3)"
                        )
                        city = city_element.text.strip()
                    except:
                        city = None

                    try:
                        # Extract salary
                        salary_element = card.find_element(
                            By.CSS_SELECTOR, "p.h5.strong-600.mt-xs.mb-0.nowrap"
                        )
                        salary_text = salary_element.text.strip()
                    except:
                        salary_text = None

                    try:
                        # Extract experiecne
                        experience_element = card.find_element(
                            By.CSS_SELECTOR, "ul.mt-lg.mb-0 li span.text-default-7"
                        )
                        experience = experience_element.text.strip()
                    except:
                        experience = None

                    resume_link = card.find_element(
                        By.CSS_SELECTOR, "h2 a"
                    ).get_attribute("href")

                    print("Title: ", title)
                    print("Salary: ", salary)
                    print(f"Info: {name}, {age}")
                    print("Experience:", experience)
                    print("Location: ", city)
                    print("Link: ", resume_link)
                    print()

                    resumes.append(
                        {
                            "title": title,
                            "salary": salary_text,
                            "personal_info": f"{name}, {age}",
                            "location": city,
                            "link": resume_link,
                        }
                    )
                except Exception as e:
                    print(f"Error parsing a card: {e}")
                    continue

        except Exception as e:
            print(f"Error while parsing work.ua: {e}")

        return resumes

    def parse_robota_ua(
        self, job_position, location=None, experience=None, salary=None
    ):
        url = f"https://robota.ua/candidates/{job_position.replace(' ', '+').lower()}/{f'{location.lower()}' if location else 'ukraine'}"
        try:
            print(f"Loading URL: {url}")
            self.driver.get(url)
        except Exception as e:
            print(f"Error loading URL: {e}")
            return []

        resumes = []

        # Input search criteria and submit the search
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "cv-card"))
            )
            cards = self.driver.find_elements(By.CSS_SELECTOR, "cv-card")

            for card in cards:
                try:
                    print(1)
                    title = card.find_element(
                        By.CSS_SELECTOR, ".p.santa-m-0.santa-typo-h3.santa-pb-10"
                    ).text.strip()
                    print(2)
                    location_info = card.find_element(
                        By.CSS_SELECTOR, 'p[data-id="cv-city-tag"]'
                    ).text.strip()
                    print(3)
                    resume_link = card.find_element(By.CSS_SELECTOR, "a").get_attribute(
                        "href"
                    )
                    print(4)
                    try:
                        salary_text = card.find_element(
                            By.CSS_SELECTOR, ".p.santa-typo-secondary"
                        ).text.strip()
                    except:
                        salary_text = None

                    print(5)
                    personal_info = card.find_element(
                        By.CSS_SELECTOR,
                        ".p.santa-pr-20.santa-typo-regular.santa-truncate.ng-star-inserted",
                    ).text.strip()
                    print(6)

                    print("Url: ", url)
                    print("Title: ", title)
                    print("Salary: ", salary_text)
                    print("Info: ", personal_info)
                    print("Location: ", location_info)
                    print("Link: ", resume_link)
                    print()

                    resumes.append(
                        {
                            "title": title,
                            "salary": salary_text,
                            "personal_info": personal_info,
                            "location": location_info,
                            "link": resume_link,
                        }
                    )
                except Exception as e:
                    print(f"Error parsing a card: {e}")
                    continue

        except Exception as e:
            print(f"Error while parsing robota.ua: {e}")

        return resumes

    def close(self):
        # Close the browser instance
        self.driver.quit()


# Script Execution
if __name__ == "__main__":
    # Specify the path to the Chromedriver executable
    chromedriver_path = (
        "/usr/local/bin/chromedriver"  # Update the path if Chromedriver is not in PATH
    )
    parser = ResumeParser(driver_path=chromedriver_path)

    # Define search criteria
    job_position = "Python Developer"  # Job title to search for
    location = "Kyiv"  # Location filter

    # Fetch resumes from work.ua
    print("Parsing work.ua...")
    work_ua_resumes = parser.parse_work_ua(
        job_position, location=location, experience="1-3"
    )

    # Fetch resumes from robota.ua
    # print("Parsing robota.ua...")
    # robota_ua_resumes = parser.parse_robota_ua(job_position, location=location)

    # # Combine results from both websites
    # all_resumes = work_ua_resumes + robota_ua_resumes

    # # Print the parsed resumes
    # for resume in all_resumes:
    #     print(resume)

    # Close the browser
    parser.close()
