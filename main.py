import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import time

# Initialize the WebDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

def login(username, password):
    try:
        driver.get('https://demo.brainyware.ai/dash/fs')  # Replace with the desired URL
        print("Opened website")

        driver.maximize_window()
        wait = WebDriverWait(driver, 20)  # Increased wait time
        email_field = wait.until(EC.presence_of_element_located((By.XPATH, '//input[@name="email"]')))
        password_field = wait.until(EC.presence_of_element_located((By.XPATH, '//input[@name="password"]')))
        print("Found email and password fields")

        email_field.send_keys(username)
        password_field.send_keys(password)
        print("Entered username and password")

        login_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Sign in")]')))
        login_button.click()
        print("Clicked login button")

        time.sleep(10)  # Increased sleep time
    except Exception as e:
        print(f"An error occurred during login: {e}")

def add_bucket_and_document():
    try:
        wait = WebDriverWait(driver, 20)  # Increased wait time

        documents_section = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div[2]/div/div[1]/div/aside/div[1]/a[2]/div/h3')))
        documents_section.click()
        print("Navigated to Documents section")

        add_bucket_button = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div/div[2]/div/div[2]/div/div[2]/div[1]/button')))
        add_bucket_button.click()
        print("Clicked Add Bucket button")

        bucket_name_field = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div/div[2]/div/div[2]/div/div[3]/div/form/div[1]/div/input')))
        bucket_name_field.send_keys("01-test")
        print("Entered bucket name")

        confirm_button = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div/div[2]/div/div[2]/div/div[3]/div/form/div[2]/button')))
        confirm_button.click()
        print("Confirmed adding bucket")

        time.sleep(10)  # Increased sleep time

        enter_bucket_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div[2]/div/div[2]/div/div[2]/div[2]/div/div[1]/div/div[2]/button[4]')))
        enter_bucket_button.click()
        print("Entered the bucket")

        # Upload files together
        if not upload_documents([
            'C:\\Users\\Overtossi\\Documents\\test.txt',
            
            
            
            
        ]):
            print("Exiting due to file upload failure.")
            delete_bucket()
            return

        # Wait for 1 minute before analyzing the status of the files
        print("Waiting for 1 minute before starting the file analysis...")
        time.sleep(60)

        # Periodically analyze the status of all files present in the bucket
        retries = 6
        for _ in range(retries):
            all_files_trained, any_files_failed = analyze_files()
            if all_files_trained:
                print("All files are successfully trained.")
                create_ai_and_translate()
                go_back()  # Navigate back before deleting AI and bucket
                delete_ai()
                delete_bucket()
                return
            if any_files_failed:
                print("One or more files failed to upload.")
                print("Exiting due to file upload failure.")
                delete_bucket()
                return
            print("Files are still processing, checking again in 5 seconds...")
            time.sleep(10)  # Increased retry interval
        else:
            print("The files are still processing after multiple retries")
            delete_bucket()
    except Exception as e:
        print(f"An error occurred: {e}")

def upload_documents(file_paths):
    try:
        wait = WebDriverWait(driver, 20)  # Increased wait time

        add_document_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div[2]/div/div[2]/div/div[3]/div[2]/div/div/button/div')))
        add_document_button.click()
        print("Clicked Add Document button")

        existing_files = []
        for file_path in file_paths:
            print(f"Checking if file exists at: {file_path}")
            if os.path.exists(file_path):
                existing_files.append(file_path)
            else:
                print(f"The file at {file_path} does not exist and will be skipped.")

        if not existing_files:
            print("No valid files to upload.")
            return False

        upload_field = wait.until(EC.presence_of_element_located((By.XPATH, '//input[@type="file"]')))
        
        # Sending all valid file paths as a single string separated by newlines
        upload_field.send_keys("\n".join(existing_files))
        print("Uploaded the files")

        time.sleep(10)  # Increased sleep time

        close_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div[2]/div/div[2]/div/div[4]/div/div[2]/a')))
        close_button.click()
        print("Clicked the close button")

        # Immediate analysis after upload
        all_files_trained, any_files_failed = analyze_files()
        if any_files_failed:
            print("One or more files failed to upload immediately after upload.")
            return False
        return True
    except Exception as e:
        print(f"An error occurred while uploading the documents: {e}")
        return False

def analyze_files():
    try:
        wait = WebDriverWait(driver, 20)  # Increased wait time
        file_statuses = []

        # Re-locate the file elements each time
        files = driver.find_elements(By.XPATH, '//*[@id="app"]/div[2]/div/div[2]/div/div[3]/div[2]/div/div')

        for index, file in enumerate(files):
            try:
                # Skip the "New" button
                if "Upload new documents" in file.text:
                    continue

                try:
                    file_name = file.find_element(By.XPATH, './/div[contains(@class, "file-name")]').text
                except:
                    file_name = f"file {index+1}"

                status = "unknown"
                try:
                    if file.find_elements(By.XPATH, './/div[@theme="error"]'):
                        status = "failed"
                    elif file.find_elements(By.XPATH, './/div[contains(@class, "rounded-xl") and contains(normalize-space(text()), "Waiting")]'):
                        status = "waiting"
                    elif file.find_elements(By.XPATH, './/div[contains(@class, "rounded-xl") and contains(normalize-space(text()), "Trained")]'):
                        status = "trained"
                except Exception as e:
                    print(f"An error occurred while determining the status of {file_name}: {e}")

                file_statuses.append((file_name, status))

            except Exception as e:
                print(f"An error occurred while processing file {index+1}: {e}")
                file_statuses.append((f"file {index+1}", "unknown"))

        all_files_trained = all(status == "trained" for _, status in file_statuses)
        any_files_failed = any(status == "failed" for _, status in file_statuses)

        for idx, (name, status) in enumerate(file_statuses):
            print(f"file {idx+1}: {name} - {status}")

        return all_files_trained, any_files_failed
    except Exception as e:
        print(f"An error occurred while analyzing files: {e}")
        raise

def click_element_with_js(element):
    driver.execute_script("arguments[0].click();", element)

def create_ai_and_translate():
    try:
        wait = WebDriverWait(driver, 20)  # Increased wait time

        ai_section = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div[2]/div/div[1]/div/aside/div[1]/a[1]')))
        click_element_with_js(ai_section)
        print("Navigated to AIs section")

        add_ai_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div[2]/div/div[2]/div/div[2]/div[1]/button')))
        click_element_with_js(add_ai_button)
        print("Clicked Add AI button")

        typology_dropdown = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="typology"]')))
        typology_dropdown.click()
        
        typology_dropdown.send_keys(Keys.ARROW_DOWN)
        typology_dropdown.send_keys(Keys.ENTER)
        print("Selected 'docs ai'")

        ai_name_field = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="name"]')))
        ai_name_field.send_keys("01-test")
        print("Entered AI name")

        select_bucket_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div[2]/div/div[2]/div/div[3]/div/form/div[1]/div[2]/div/div[2]/div[2]/div/div[1]/div/div[2]/button[2]')))
        click_element_with_js(select_bucket_button)
        print("Selected the bucket")

        confirm_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div[2]/div/div[2]/div/div[3]/div/form/div[2]/button')))
        click_element_with_js(confirm_button)
        print("Confirmed AI creation")

        select_file_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div[2]/div/div/div/div[2]/div/div[2]/button[2]/div[2]')))
        click_element_with_js(select_file_button)
        print("Selected the correct file")

        instruction_box = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="app"]/div[2]/div/div/div/div[1]/div/form/textarea')))
        instruction_box.send_keys("translate this text into Italian")
        print("Entered instruction")

        enter_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div[2]/div/div/div/div[1]/div/form/button')))
        click_element_with_js(enter_button)
        print("Submitted the instruction")

        print("Waiting for one minute before checking the response...")
        time.sleep(30)

        response_element = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="app"]/div[2]/div/div/div/div[1]/div/form/textarea')))
        response_text = response_element.get_attribute('value')
        print("AI response:", response_text)

        if response_text == "There is a problem with the AI, please try again later":
            print("AI creation failed, skipping deletion steps.")
            return

    except Exception as e:
        print(f"An error occurred during AI creation and translation: {e}")

def go_back():
    try:
        driver.back()
        print("Navigated back")
    except Exception as e:
        print(f"An error occurred while navigating back: {e}")       

def delete_ai():
    try:
        wait = WebDriverWait(driver, 10)

        delete_ai_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div[2]/div/div[2]/div/div[2]/div[2]/div/div/div/div[2]/button[1]')))
        click_element_with_js(delete_ai_button)
        print("Pressed the delete button for the AI")

        confirm_delete_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div[3]/div/div/button[2]')))
        click_element_with_js(confirm_delete_button)
        print("Confirmed AI deletion")

        documents_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div[2]/div/div[1]/div/aside/div[1]/a[2]/div/p')))
        click_element_with_js(documents_button)
        print("Navigated back to Documents section")

        delete_bucket_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div[2]/div/div[2]/div/div[2]/div[2]/div/div[1]/div/div[2]/button[2]')))
        click_element_with_js(delete_bucket_button)
        print("Pressed the bucket's delete button")

        confirm_delete_bucket_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div[3]/div/div/button[2]')))
        click_element_with_js(confirm_delete_bucket_button)
        print("Confirmed bucket deletion")

        time.sleep(20)

        print("Test finished without errors")

    except Exception as e:
        print(f"An error occurred during AI and bucket deletion: {e}")

def delete_bucket():
    try:
        wait = WebDriverWait(driver, 20)  # Increased wait time

        documents_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div[2]/div/div[1]/div/aside/div[1]/a[2]/div/p')))
        click_element_with_js(documents_button)
        print("Navigated back to Documents section")

        delete_bucket_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div[2]/div/div[2]/div/div[3]/div[2]/div/div/div/div[2]/button[2]')))
        click_element_with_js(delete_bucket_button)
        print("Pressed the bucket's delete button")

        confirm_delete_bucket_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div[3]/div/div/button[2]')))
        click_element_with_js(confirm_delete_bucket_button)
        print("Confirmed bucket deletion")

        time.sleep(20)

        print("Test finished without errors")

    except Exception as e:
        print(f"An error occurred during AI and bucket deletion: {e}")

    except Exception as e:
        print(f"An error occurred during bucket deletion: {e}")

def main():
    # Example usage
    login('', '')
    add_bucket_and_document()

    print("Script execution finished. The browser remains open for inspection.")

    # Infinite loop to keep the script running
    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()
