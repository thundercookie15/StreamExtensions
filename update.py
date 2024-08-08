import os
import subprocess
import sys


def y_n(q):
    while True:
        ri = input("{} (y/n): ".format(q))
        if ri.lower() in ["yes", "y"]:
            return True
        elif ri.lower() in ["no", "n"]:
            return False


def update_deps():
    print("Attempting to install dependencies...")

    try:
        subprocess.check_call(
            '"{}" -m pip install --no-warn-script-location -r requirements/all.txt'.format(sys.executable)
            , shell=True)
    except subprocess.CalledProcessError:
        raise OSError("Failed to install dependencies. Please install them manually.")


def main():
    print("Starting updates...")
    if not os.path.isdir(".git"):
        raise EnvironmentError("This script must be run from the root of the repository.")

    try:
        subprocess.check_call("git --version", shell=True, stdout=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        raise OSError("Git not found. Please install it manually.")

    print("Passed Git checks...")

    sp = subprocess.check_output("git status --porcelain", shell=True, universal_newlines=True)
    if sp:
        oshit = y_n("You have uncommitted changes. Do you want to continue?")

        if oshit:
            try:
                subprocess.check_call("git reset --hard", shell=True)
            except subprocess.CalledProcessError:
                raise OSError("Failed to reset repository. Please do it manually.")
        else:
            wowee = y_n("Do you want to update dependencies?")
            if wowee:
                update_deps()

        print("Checking if we need to update the program...")

        try:
            subprocess.check_call("git pull", shell=True)
        except subprocess.CalledProcessError:
            print("Failed to update the program. Please do it manually.")

    update_deps()

    print("Done!")


if __name__ == '__main__':
    main()
