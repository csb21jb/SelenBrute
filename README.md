# Selenium Login Brute Force Tool

A Python script that uses Selenium to automate login attempts against web applications for penetration testing.

## Features

- **Automatic Setup**: Creates virtual environment and installs dependencies on first run
- **Flexible Input**: Accepts custom username and password files via command-line flags
- **Form Inspection**: Inspect mode to identify form field names and IDs
- **Custom Selectors**: Support for custom field names, IDs, or CSS selectors
- **Smart Detection**: Automatically finds login forms and detects successful logins
- **Browser Support**: Works with Firefox (default) or Chrome (with automatic fallback)
- **Flag Detection**: Automatically extracts flags from successful login pages
- **Intelligent Field Detection**: Tries multiple strategies to locate username and password fields

## Quick Start

Simply run the script - it will handle all setup automatically:

```bash
python3 brute_force.py --userfile users.txt --passfile pass.txt
```

The script will:
1. Create a virtual environment (if it doesn't exist)
2. Install Selenium (if not installed)
3. Restart itself in the virtual environment
4. Begin the brute force attack

## Usage

### Step 1: Inspect the Login Form (Optional but Recommended)

If the target uses non-standard field names, first inspect the form:

```bash
python3 brute_force.py --url http://target.com/login --inspect
```

This will show you all form fields with their names, IDs, and types. Example output:

```
[+] Found 1 form(s)

============================================================
Form #1
============================================================

Input Fields:
  - Type: text         | Name: user_login    | ID: login_user      | Placeholder: Username
  - Type: password     | Name: user_pass     | ID: login_pass      | Placeholder: Password

Buttons:
  - Type: submit       | Name: submit        | ID: login_btn       | Text: Login
```

### Step 2: Run Brute Force Attack

#### Basic Usage (Auto-detect fields)
```bash
python3 brute_force.py --userfile users.txt --passfile pass.txt
```

#### With Custom URL
```bash
python3 brute_force.py --url http://target.com/login --userfile users.txt --passfile pass.txt
```

#### With Custom Field Selectors

If the form uses non-standard field names (discovered via `--inspect`):

```bash
python3 brute_force.py --userfile users.txt --passfile pass.txt \
  --username-field user_login --password-field user_pass
```

You can also use CSS selectors:

```bash
python3 brute_force.py --userfile users.txt --passfile pass.txt \
  --username-field "#login_user" --password-field "#login_pass"
```

### Command-Line Options

- `--url`: Target URL (default: http://10.82.151.112/labs/lab1/)
- `--inspect`: Inspect form to identify field names and IDs
- `--userfile`: Path to file containing usernames (one per line) [REQUIRED for brute force]
- `--passfile`: Path to file containing passwords (one per line) [REQUIRED for brute force]
- `--username-field`: Custom username field (name, ID, or CSS selector)
- `--password-field`: Custom password field (name, ID, or CSS selector)

## File Format

### Username File (users.txt)
```
admin
administrator
root
user
```

### Password File (pass.txt)
```
password
admin123
pass123
Password1
```

## Example Output

### Inspect Mode

```bash
$ python3 brute_force.py --url http://example.com/login --inspect

[*] Checking environment setup...
[+] Environment ready

    ╔════════════════════════════════════════╗
    ║   Selenium Login Brute Force Tool     ║
    ╚════════════════════════════════════════╝
    
[*] Inspecting form at http://example.com/login
[*] Initializing browser...

[+] Found 1 form(s)

============================================================
Form #1
============================================================

Input Fields:
  - Type: text         | Name: user_login    | ID: login_user      | Placeholder: Enter username
  - Type: password     | Name: user_pass     | ID: login_pass      | Placeholder: Enter password
  - Type: submit       | Name: submit        | ID: N/A             | Placeholder: N/A

Buttons:
  - Type: submit       | Name: login_btn     | ID: btn_login       | Text: Sign In

[*] Inspection complete. Use the field names/IDs with --username-field and --password-field flags
[*] Example: python3 brute_force.py --username-field user_login --password-field user_pass ...
```

### Brute Force Mode

```bash
$ python3 brute_force.py --userfile users.txt --passfile pass.txt

[*] Checking environment setup...
[+] Environment ready

    ╔════════════════════════════════════════╗
    ║   Selenium Login Brute Force Tool     ║
    ╚════════════════════════════════════════╝
    
[*] Starting brute force attack on http://10.82.151.112/labs/lab1/
[*] Loading usernames from: users.txt
[*] Loading passwords from: pass.txt
[*] Loaded 10 usernames and 19 passwords
[*] Total attempts: 190
[*] Initializing browser...
[1] Trying admin:password ✗
[2] Trying admin:admin ✗
[3] Trying admin:123456 ✗
[4] Trying admin:admin123 ✓ SUCCESS!

============================================================
[+] Valid credentials found!
[+] Username: admin
[+] Password: admin123
============================================================

[*] Page content may contain a flag:
<!DOCTYPE html>
<html>
<head><title>Welcome</title></head>
<body>
<h1>Welcome admin!</h1>
<p>Flag: HTB{br0t3_f0rc3_succ3ss}</p>
</body>
</html>

[*] Browser closed
```
<img width="552" height="203" alt="image" src="https://github.com/user-attachments/assets/ecedb098-ade9-44bf-bf1d-3bcf7e98efa8" />

## Sample Files Included

- `users.txt` - Common usernames (admin, root, user, etc.)
- `pass.txt` - Common weak passwords

## Requirements

- Python 3.x
- Firefox or Chrome browser installed
- Corresponding WebDriver (geckodriver for Firefox, chromedriver for Chrome)

**Note**: On Kali Linux, these drivers are typically pre-installed.

## How It Works

### Setup Phase
1. The script automatically sets up a Python virtual environment (if not exists)
2. Installs Selenium if needed
3. Restarts itself in the virtual environment if necessary

### Brute Force Phase
1. Reads username and password lists from provided files
2. Initializes browser (Firefox or Chrome with headless mode)
3. For each username, tries all passwords (username:password combinations)
4. For each attempt:
   - Navigates to the target URL
   - Locates form fields using:
     - Custom selectors (if provided)
     - Common field names (username, user, password, pass, etc.)
     - Input type attributes (text, password)
   - Fills in credentials
   - Submits the form
   - Analyzes the response for success/failure indicators
5. Reports successful credentials and extracts flags if present

### Field Detection Strategy

The script uses a multi-layered approach to find form fields:

1. **Custom Selectors** (if provided via `--username-field` or `--password-field`):
   - Tries as `name` attribute
   - Tries as `id` attribute
   - Tries as CSS selector

2. **Common Identifiers** (auto-detection):
   - Username: `username`, `user`, `login`, `email`, `uname`
   - Password: `password`, `pass`, `pwd`

3. **Type-based Fallback**:
   - Username: First `input[type="text"]` element
   - Password: First `input[type="password"]` element

## Success Detection

The script detects successful logins by checking for:
- URL changes after login
- Success keywords: "welcome", "dashboard", "logout", "success", "flag{", "htb{", "congratulations"
- Absence of error messages: "invalid", "incorrect", "failed", "wrong", "error"

## Troubleshooting

### "Could not locate login form fields"

**Problem**: The script cannot find the username or password fields.

**Solution**:
1. Use `--inspect` mode to see all available form fields:
   ```bash
   python3 brute_force.py --url http://target.com/login --inspect
   ```
2. Use the discovered field names with `--username-field` and `--password-field`:
   ```bash
   python3 brute_force.py --userfile users.txt --passfile pass.txt \
     --username-field discovered_name --password-field discovered_name
   ```

### Site Uses Non-Standard Field Names

**Problem**: The site uses unusual field names like `txtUser`, `auth_username`, etc.

**Solution**: Use the `--username-field` and `--password-field` options:
```bash
python3 brute_force.py --userfile users.txt --passfile pass.txt \
  --username-field txtUser --password-field txtPass
```

### Success Detection Not Working

**Problem**: Valid credentials aren't being detected as successful.

**Solution**: The script checks for specific keywords. If your target uses different language or response patterns, you may need to modify the `success_indicators` and `failure_indicators` lists in the script (lines 191-208).

### Browser Driver Issues

**Problem**: "Failed to initialize driver" errors.

**Solution**: 
- On Kali Linux, install drivers: `sudo apt install firefox-esr geckodriver`
- For Chrome: `sudo apt install chromium-driver`
- The script automatically tries Firefox first, then falls back to Chrome

### Rate Limiting or Slow Sites

**Problem**: Site is rate limiting or responses are slow.

**Solution**: The script includes a 0.5-second delay between attempts (line 266). You may need to increase this value in the script if the site implements aggressive rate limiting.

## Advanced Usage

### Using CSS Selectors

For complex forms, you can use full CSS selectors:
```bash
python3 brute_force.py --userfile users.txt --passfile pass.txt \
  --username-field "form#login input[name='user']" \
  --password-field "form#login input[name='pass']"
```

### Attack Order

The script iterates through usernames first, then all passwords for each username:
- admin:password1
- admin:password2
- admin:password3
- user:password1
- user:password2
- ...
