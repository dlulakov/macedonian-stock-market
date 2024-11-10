from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
import time

# Define the Row and Issuer (Izdavac) classes to store data

class Rows:
    def __init__(self, date, last_price_transaction, maximum, minimum, average_price, prom, quantity, best, turnover):
        self.date = date
        self.last_price_transaction = last_price_transaction
        self.maximum = maximum
        self.minimum = minimum
        self.average_price = average_price
        self.prom = prom
        self.quantity = quantity
        self.best = best
        self.turnover = turnover

    def to_dict(self):
        return {
            "date": self.date,
            "last_price_transaction": self.last_price_transaction,
            "maximum": self.maximum,
            "minimum": self.minimum,
            "average_price": self.average_price,
            "prom": self.prom,
            "quantity": self.quantity,
            "best": self.best,
            "turnover": self.turnover
        }


class Izdavac:
    def __init__(self, code, rows):
        self.code = code
        self.rows = rows

    def to_dict(self):
        return {
            "code": self.code,
            "rows": [row.to_dict() for row in self.rows]
        }


# Define the main scraping function

def Filter1(url):
    driver = webdriver.Chrome()
    wait = WebDriverWait(driver, 3)
    driver.get(url)
    code_list = []  # This will store data for each code

    try:
        # Locate the dropdown list of codes
        codes = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#Code option")))

        # Loop through each code option
        for i in range(len(codes)):
            # Re-fetch the codes in each iteration to avoid stale element issues
            codes = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#Code option")))
            code = codes[i]
            code_text = code.text
            code.click()  # Click on the code option

            # Wait for the table to load after selecting each code
            rows = []
            try:
                results_table_rows = wait.until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#resultsTable tbody tr"))
                )

                # Extract data from each row in the table
                for row in results_table_rows:
                    columns = row.find_elements(By.CSS_SELECTOR, "td")
                    if len(columns) >= 9:  # Ensure the row has all columns
                        date = columns[0].text
                        last_price_transaction = columns[1].text
                        maximum = columns[2].text
                        minimum = columns[3].text
                        average_price = columns[4].text
                        prom = columns[5].text
                        quantity = columns[6].text
                        best = columns[7].text
                        turnover = columns[8].text
                        rows.append(Rows(date, last_price_transaction, maximum, minimum, average_price, prom, quantity, best, turnover))

                # Store the current code and its rows in the code list
                codeObject = Izdavac(code_text, rows)
                code_list.append(codeObject)

                # Click the 'Прикажи' button to refresh data for the next code
                driver.find_element(By.CSS_SELECTOR, "input[value='Прикажи']").click()

                # Pause briefly to allow the page to update
                time.sleep(1)

            except StaleElementReferenceException:
                print(f"Stale element encountered for code {code_text}. Retrying...")

        # Output the collected data
        for code_obj in code_list:
            print(f"Code: {code_obj.code}")
            for row in code_obj.rows:
                print(row.to_dict())

    except TimeoutException:
        print("Timeout waiting for elements.")
    finally:
        driver.quit()  # Ensure the browser is closed after the function completes


# Run the function with the provided URL
if __name__ == '__main__':
    url = 'https://www.mse.mk/mk/stats/symbolhistory/kmb'
    Filter1(url)


