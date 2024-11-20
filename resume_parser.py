from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from translate import Translator
import requests


def get_usd_rate_nbu():
    url = "https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?json"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        for currency in data:
            if currency["cc"] == "USD":
                return currency["rate"]
    else:
        print(f"Error: Unable to fetch data. Status code: {response.status_code}")
        return None


def parse_experience_range_work_ua(experience_range):
    """
    Converts an experience range or a single experience value into corresponding experience codes.

    :param experience_range: A string representing a single experience value (e.g., "1")
                             or a range (e.g., "2-5").
    :return: A set of experience codes corresponding to the input range.
    """
    # Mapping of experience years to corresponding codes
    experience_mapping = {
        0: 0,  # "No experience" (code 0)
        1: 1,  # "Up to 1 year" (code 1)
        2: 164,  # "1 to 2 years" (code 164)
        3: 165,  # "1 to 2 years" (code 164)
        4: 165,  # "2 to 5 years" (code 165)
        5: 165,  # "2 to 5 years" (code 165)
        6: 166,  # "More than 5 years" (code 166)
    }

    # Initialize an empty set to store experience codes (set to ensure uniqueness)
    experience_values = set()

    # Check if the input contains a hyphen indicating a range
    if "-" in experience_range:
        try:
            # Split and map the range values to integers
            start, end = map(int, experience_range.split("-"))

            # Ensure that the start value is not greater than the end value
            if start > end:
                raise ValueError("Start value cannot be greater than the end value.")

            # Loop through the range and map experience years to experience codes
            for i in range(start, end + 1):
                if i >= 0:
                    experience_values.add(
                        experience_mapping.get(i, 166)
                    )  # Default to "More than 5 years" (code 166)

        except ValueError as e:
            # Handle invalid input (non-integer or invalid range)
            raise ValueError(f"Invalid experience range: {e}")
    else:
        # If it's a single experience value, convert it to an integer and map it to the code
        try:
            experience = int(experience_range)
            if experience >= 0:
                experience_values.add(
                    experience_mapping.get(experience, 166)
                )  # Default to "More than 5 years" (code 166)
            else:
                raise ValueError("Experience cannot be negative.")
        except ValueError:
            # Handle non-integer input
            raise ValueError(
                "Invalid experience input. Please provide a valid number or range."
            )

    return experience_values


def parse_salary_range_work_ua(salary):
    """
    Converts a salary range or a single salary value into a tuple of corresponding salary range IDs.

    :param salary: A string representing a salary value (e.g., "20000", "20000-50000").
    :return: A tuple with two integers corresponding to the salary range IDs, defaulting to (0, 0).
    """
    salary_mapping = {
        20000: 4,  # from 20,000
        30000: 5,  # from 30,000
        40000: 6,  # from 40,000
        50000: 7,  # up to 50,000
        100000: 8,  # up to 100,000
    }

    # Check if the input contains a range (e.g., "20000-50000")
    if salary and "-" in salary:
        try:
            start, end = map(int, salary.split("-"))
            # Get the corresponding range IDs from the mapping
            start_value = salary_mapping.get(start, 0)
            end_value = salary_mapping.get(end, 0)
            return start_value, end_value
        except ValueError:
            # Handle case where the input is not a valid range
            return 0, 0

    # If it's a single salary value, look up its corresponding ID
    else:
        try:
            salary_value = int(salary)
            salary_value = salary_mapping.get(salary_value, 0)
            return salary_value, salary_value
        except:
            # Handle case where the input is not a valid salary
            return 0, 0


def parse_experience_range_robota_ua(experience_range):
    """
    Converts an experience range into a list of corresponding experience IDs.

    :param experience_range: A string representing an experience range (e.g., "0", "2-3", "4-5").
    :return: A list of experience IDs corresponding to the input range.
    """
    experience_values = []

    # Check if the input contains a range (e.g., "2-3")
    if "-" in experience_range:
        try:
            start, end = map(int, experience_range.split("-"))
            # Iterate through the range and append corresponding experience IDs
            for i in range(start, end + 1):
                if i < 1:
                    experience_values.append("%220%22")  # No experience
                elif 1 <= i < 2:
                    experience_values.append("%221%22")  # Up to 1 year
                elif 2 <= i < 5:
                    experience_values.append("%223%22")  # 2 to 5 years
                elif 5 <= i <= 10:
                    experience_values.append("%224%22")  # 5 to 10 years
                elif i > 10:
                    experience_values.append("%225%22")  # More than 10 years
        except ValueError:
            # Handle case where the range is not valid (non-integer values)
            return []
    else:
        try:
            experience = int(experience_range)
            # Handle a single experience value
            if experience < 1:
                experience_values.append("%220%22")  # No experience
            elif 1 <= experience < 2:
                experience_values.append("%221%22")  # Up to 1 year
            elif 2 <= experience < 5:
                experience_values.append("%223%22")  # 2 to 5 years
            elif 5 <= experience < 10:
                experience_values.append("%224%22")  # 5 to 10 years
            elif experience >= 10:
                experience_values.append("%225%22")  # More than 10 years
        except ValueError:
            # Handle case where the input is not a valid integer
            return []

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
        """
        Parses job resumes from work.ua based on given filters like job position, location, experience, and salary.

        :param job_position: Job title to search for.
        :param location: Optional location to filter resumes by.
        :param experience: Optional experience range to filter resumes by.
        :param salary: Optional salary range to filter resumes by.
        :return: List of resumes with job title, salary, personal info, location, and link.
        """
        # Construct URL with optional location and job position
        url = f"https://www.work.ua/resumes-{f'{location.lower()}-' if location else ''}{job_position.replace(' ', '+').lower()}/"

        # Add experience filter to URL if provided
        if experience:
            experience_value = parse_experience_range_work_ua(experience)
            experience_filter = "+".join(map(str, experience_value))
            url += f"?experience={experience_filter}"

        # Add salary filter to URL if provided
        if salary:
            start, end = 0, 0
            salary_result = parse_salary_range_work_ua(salary)

            if len(salary_result) == 2:
                start, end = salary_result
            else:
                start = salary_result

            # Add salary range to URL
            if "?" not in url and "&" not in url:
                url += f"?salaryfrom={start}"
            else:
                url += f"&salaryfrom={start}"

            if end:
                url += f"&salaryto={end}"

        try:
            # Attempt to load the constructed URL
            print(f"Loading URL: {url}.")
            self.driver.get(url)
        except Exception as e:
            print(f"Error loading URL: {e}.")
            return []

        resumes = []
        try:
            # Wait for resume cards to be loaded on the page
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "resume-link"))
            )
            cards = self.driver.find_elements(By.CSS_SELECTOR, ".card.resume-link")

            for card in cards:
                try:
                    # Extract resume details from each card
                    title = card.find_element(By.CSS_SELECTOR, "h2 a").text.strip()

                    # Extract personal details (name, age, city) if available
                    name = self._extract_element_text(card, "p.mt-xs.mb-0 .strong-600")
                    age = self._extract_element_text(
                        card, "p.mt-xs.mb-0 span:nth-child(2)"
                    )
                    city = self._extract_element_text(
                        card, "p.mt-xs.mb-0 span:nth-child(3)"
                    )

                    # Extract salary information
                    salary_text = self._extract_element_text(
                        card, "p.h5.strong-600.mt-xs.mb-0.nowrap"
                    )

                    # Get the resume link
                    resume_link = card.find_element(
                        By.CSS_SELECTOR, "h2 a"
                    ).get_attribute("href")

                    # Output the resume details
                    # print(f"Title: {title}")
                    # print(f"Salary: {salary_text}")
                    # print(f"Info: {name}, {age}")
                    # print(f"Location: {city}")
                    # print(f"Link: {resume_link}")
                    # print()

                    # Add resume data to the results list
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

    def _extract_element_text(self, card, selector):
        """
        Extracts text from an element, returns None if the element is not found.

        :param card: The card element containing the target information.
        :param selector: The CSS selector for the target element.
        :return: The text of the element or None if the element is not found.
        """
        try:
            # Attempt to find the element using the provided selector and extract its text.
            element = card.find_element(By.CSS_SELECTOR, selector)
            return element.text.strip()
        except Exception:
            # Return None if the element is not found or an error occurs.
            return None

    def parse_robota_ua(
        self, job_position, location=None, experience=None, salary=None
    ):
        url = f"https://robota.ua/candidates/{job_position.replace(' ', '-').lower()}/{f'{location.lower()}' if location else 'ukraine'}"

        # Checking and adding parameters
        if experience:
            experience_values = parse_experience_range_robota_ua(experience)
            experience_filter = "%2C".join(experience_values)
            if "?" not in url:
                url += f"?experienceIds=%5B{experience_filter}%5D"
            else:
                url += f"&experienceIds=%5B{experience_filter}%5D"

        if salary:
            if "-" in salary:
                start, end = map(int, salary.split("-"))
            else:
                start = salary
                end = "null"
            if "?" not in url and "&" not in url:
                url += f"?salary=%7B%22from%22%3A{start}%2C%22to%22%3A{end}%7D"
            else:
                url += f"&salary=%7B%22from%22%3A{start}%2C%22to%22%3A{end}%7D"

        try:
            print(f"Loading URL: {url}")
            self.driver.get(url)
        except Exception as e:
            print(f"Error loading URL: {e}")
            return []

        resumes = []

        # Input search criteria and submit the search
        try:
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, "cv-card"))
            )
            cards = self.driver.find_elements(By.CSS_SELECTOR, ".cv-card")

            for card in cards:
                try:
                    title = card.find_element(
                        By.CSS_SELECTOR, "p.santa-m-0.santa-typo-h3.santa-pb-10"
                    ).text.strip()

                    try:
                        name = card.find_element(
                            By.CSS_SELECTOR, '[data-id="cv-speciality"] + div p'
                        ).text
                    except Exception:
                        name = None

                    try:
                        city = card.find_element(
                            By.CSS_SELECTOR, '[data-id="cv-city-tag"]'
                        ).text
                    except Exception:
                        city = None

                    try:
                        age = card.find_element(
                            By.XPATH,
                            './/*[contains(text(), " років") or contains(text(), " роки") or contains(text(), " рік")]',
                        ).text.strip()
                    except Exception:
                        age = None

                    try:
                        salary_text = card.find_element(
                            By.XPATH,
                            './/*[contains(text(), "$") or contains(text(), "грн")]',
                        ).text.strip()
                    except Exception:
                        salary_text = None

                    try:
                        resume_link = card.find_element(By.TAG_NAME, "a").get_attribute(
                            "href"
                        )
                    except Exception:
                        resume_link = None

                    # print("Title: ", title)
                    # print("Salary: ", salary_text)
                    # print(f"Info: {name}, {age}")
                    # print("Location: ", city)
                    # print("Link: ", resume_link)
                    # print()

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
            print(f"Error while parsing robota.ua: {e}")

        return resumes

    def close(self):
        # Close the browser instance
        self.driver.quit()


def translate_location(location, source_lang="uk", target_lang="en"):
    translator = Translator(from_lang=source_lang, to_lang=target_lang)
    try:
        return translator.translate(location).replace(" city", "").strip()
    except Exception as e:
        print(f"Error in translation: {e}")
        return location


def calculate_score(candidate, job_position, location, salary_range):
    """
    Calculate relevance score for a candidate based on defined criteria.

    :param candidate: Dictionary with candidate details.
    :param job_position: Desired job position (e.g., "Python Developer").
    :param location: Desired location (e.g., "Київ").
    :param salary_range: Desired salary range (e.g., "20000-50000").
    :return: Relevance score (int).
    """
    score = 0

    # Keyword matching in title
    title_keywords = job_position.lower().split()
    score += sum(
        5 for keyword in title_keywords if keyword in candidate["title"].lower()
    )

    # Location match
    if (
        location
        and candidate.get("location", "")
        and location.lower() in candidate.get("location", "").lower()
    ):
        score += 10

    # Salary match
    usd_rate = get_usd_rate_nbu()
    candidate_salary = candidate.get("salary")
    if salary_range and candidate_salary:
        try:
            min_salary, max_salary = map(int, salary_range.split("-"))
            if "$" in candidate_salary:
                salary_value = (
                    int(candidate_salary.replace(" ", "").replace("$", "").strip())
                    * usd_rate
                )
            else:
                salary_value = int(
                    candidate_salary.replace(" ", "")
                    .replace("грн", "")
                    .replace(".", "")
                    .strip()
                )
            if min_salary <= salary_value <= max_salary:
                score += 15
        except ValueError:
            pass  # Ignore non-numeric salary values

    return score


def sort_candidates(candidates, job_position, location, salary_range):
    """
    Sort candidates based on relevance score.

    :param candidates: List of candidate dictionaries.
    :param job_position: Desired job position.
    :param location: Desired location.
    :param salary_range: Desired salary range.
    :return: Sorted list of candidates.
    """
    # Calculate scores for each candidate
    scored_candidates = [
        {
            **candidate,
            "score": calculate_score(candidate, job_position, location, salary_range),
        }
        for candidate in candidates
    ]

    # Sort by score in descending order
    return sorted(scored_candidates, key=lambda x: x["score"], reverse=True)


# Function to fetch resumes based on the site and filters
def fetch_resumes(
    site: str,
    job_position: str,
    location=None,
    experience=None,
    salary=None,
):
    try:
        # Specify the path to the Chromedriver executable
        chromedriver_path = "/usr/local/bin/chromedriver"  # Update the path if Chromedriver is not in PATH
        parser = ResumeParser(driver_path=chromedriver_path)

        # Helper function to fetch resumes for a site
        def fetch_for_site(site_name: str):
            if site_name == "work_ua":
                return parser.parse_work_ua(
                    job_position,
                    location=translate_location(location) if location else location,
                    experience=experience,
                    salary=salary,
                )
            elif site_name == "robota_ua":
                return parser.parse_robota_ua(
                    job_position,
                    location=translate_location(location) if location else location,
                    experience=experience,
                    salary=salary,
                )
            else:
                raise ValueError(f"Unsupported site: {site_name}")

        # Fetch resumes based on the selected site(s)
        if site == "work_ua" or site == "robota_ua":
            all_resumes = fetch_for_site(site)
        else:
            all_resumes = fetch_for_site("work_ua") + fetch_for_site("robota_ua")

        # Sort resumes based on the selected criteria
        sorted_candidates = sort_candidates(all_resumes, job_position, location, salary)

        return sorted_candidates

    except Exception as e:
        print(f"Error occurred while fetching resumes: {e}")
        return []  # Return an empty list in case of error
    finally:
        # Ensure the parser is always closed
        if "parser" in locals():
            parser.close()


# # Script Execution
# if __name__ == "__main__":
#     # Specify the path to the Chromedriver executable
#     chromedriver_path = (
#         "/usr/local/bin/chromedriver"  # Update the path if Chromedriver is not in PATH
#     )
#     parser = ResumeParser(driver_path=chromedriver_path)

#     # Define search criteria
#     job_position = "Python Developer"  # Job title to search for
#     location = "Київ"  # Location filter
#     salary_range = "20000-50000"
#     experience_range = "2-3"

#     # Fetch resumes from work.ua
#     print("Parsing work.ua...")
#     work_ua_resumes = parser.parse_work_ua(
#         job_position,
#         location=translate_location(location),
#         experience=experience_range,
#         salary=salary_range,
#     )

#     # Fetch resumes from robota.ua
#     print("Parsing robota.ua...")
#     robota_ua_resumes = parser.parse_robota_ua(
#         job_position,
#         location=translate_location(location),
#         experience=experience_range,
#         salary=salary_range,
#     )

#     # Combine results from both websites
#     all_resumes = work_ua_resumes + robota_ua_resumes

#     sorted_candidates = sort_candidates(
#         all_resumes, job_position, location, salary_range
#     )

#     for candidate in sorted_candidates:
#         print(
#             f"{candidate['title']} | Score: {candidate['score']} | Link: {candidate['link']}"
#         )

#     # Close the browser
#     parser.close()
