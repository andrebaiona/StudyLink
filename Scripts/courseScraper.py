
from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
import time

# List of course URLs
course_urls = [
    "https://www.iscte-iul.pt/curso/codigo/0387/licenciatura-tecnologias-digitais-inteligencia-artificial/planoestudos",
    "https://www.iscte-iul.pt/curso/codigo/0430/licenciatura-tecnologias-digitais-seguranca-de-informacao/planoestudos",
    "https://www.iscte-iul.pt/curso/codigo/0385/licenciatura-desenvolvimento-software-aplicacoes/planoestudos",
    "https://www.iscte-iul.pt/curso/codigo/0426/licenciatura-matematica-aplicada-tecnologias-digitais/planoestudos",
    "https://www.iscte-iul.pt/curso/codigo/0426/licenciatura-matematica-aplicada-tecnologias-digitais/planoestudos",
    "https://www.iscte-iul.pt/curso/codigo/0389/licenciatura-tecnologias-digitais-automacao/planoestudos",
    "https://www.iscte-iul.pt/curso/codigo/0391/licenciatura-tecnologias-digitais-gestao/planoestudos",
    "https://www.iscte-iul.pt/curso/codigo/0387/licenciatura-tecnologias-digitais-inteligencia-artificial/planoestudos",
    "https://www.iscte-iul.pt/curso/codigo/0392/licenciatura-tecnologias-digitais-saude/planoestudos",
    "https://www.iscte-iul.pt/curso/codigo/0386/licenciatura-tecnologias-digitais-educativas/planoestudos",
    "https://www.iscte-iul.pt/curso/codigo/0429/licenciatura-tecnologias-digitais-edificios-construcao-sustentavel/planoestudos"
]

# Set up the webdriver
driver = webdriver.Chrome()

# List to store all extracted data
all_data = []

# Loop through each course URL
for url in course_urls:
    driver.get(url)
    print(f"Extracting data from: {url}")
    
    # Wait for the page to load
    time.sleep(5)

    # Extract course name (adjusted selector)
    try:
        course_name = driver.find_element(By.CSS_SELECTOR, "h1").text
    except:
        course_name = "Course name not found"

    # Extract curricular units
    course_units = driver.find_elements(By.CSS_SELECTOR, 'a.curricular-course-text')

    for unit in course_units:
        try:
            unit_name = unit.text.strip()  # Curricular unit name
            all_data.append({
                "Course": course_name,
                "Curricular Unit": unit_name
            })
        except Exception as e:
            print(f"Error extracting data: {e}")


driver.quit()

# Convert all extracted data into a DataFrame
df = pd.DataFrame(all_data)

# Save to CSV
df.to_csv('ScriptFiles/iscte_courses_units.csv', index=False, encoding='utf-8')
print("Scraping completed. Data saved to 'ScriptFiles/iscte_courses_units.csv'.")
