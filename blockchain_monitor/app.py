import subprocess
import constants as const


def validate_current_manifest():
    msg = ""
    try:
        msg = subprocess.check_output(
            ['java', '-jar', const.BLF_JAR_PATH, const.BLF_VALIDATE, const.MANIFEST_PATH])
    except subprocess.CalledProcessError as e:
        msg = 'An error occurred during BLF validation.'
    return msg


def extract_current_manifest():
    msg = ""
    try:
        msg = subprocess.check_output(
            ['java', '-jar', const.BLF_JAR_PATH, const.BLF_EXTRACT, const.MANIFEST_PATH])
    except subprocess.CalledProcessError as e:
        msg = 'An error occurred during BLF exctraction.'
    return msg


if __name__ == '__main__':
    from webapp import app
    app.run(debug=True)
