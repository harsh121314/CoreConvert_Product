import os
import subprocess

def check_and_update_requirements():
    try:
        print("Checking for missing dependencies...")
        result = subprocess.run(['pip', 'check'], capture_output=True, text=True)

        if result.returncode == 0:
            print("No missing dependencies detected.")
        else:
            print("Missing dependencies found:")
            print(result.stdout)
            print("Attempting to install missing packages...")

            for line in result.stdout.splitlines():
                package_name = line.split()[0]
                subprocess.run(['pip', 'install', package_name])

        print("\nUpdating requirements.txt...")
        subprocess.run(['pip', 'freeze', '>', 'requirements.txt'], shell=True)
        print("requirements.txt updated successfully!")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    check_and_update_requirements()