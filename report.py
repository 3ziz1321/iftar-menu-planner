# report.py - terminal helper: asks Flask for the dishes, a Thread writes the report
import json
import threading
from urllib.error import URLError
from urllib.request import urlopen

URL = "http://127.0.0.1:5050/dishes"
REPORT_FILE = "report.txt"


def write_report(data, status):
    """Runs inside the thread. Writes the file and records success in 'status'."""
    try:
        with open(REPORT_FILE, "w", encoding="utf-8") as file:
            file.write("IFTAR MENU REPORT\n")
            file.write("=================\n")
            for dish in data["dishes"]:
                file.write(f"{dish['id']}. {dish['name']} ({dish['category']}) - {dish['price']} SAR\n")
            file.write(f"\nTotal estimated cost: {data['total']} SAR\n")
        status["saved"] = True
    except OSError:
        status["saved"] = False


try:
    with urlopen(URL, timeout=5) as reply:
        data = json.loads(reply.read().decode("utf-8"))
except (URLError, OSError):
    print("Cannot reach Flask. Start server.py first.")
else:
    status = {"saved": False}
    worker = threading.Thread(target=write_report, args=(data, status))
    worker.start()      # begin the thread
    worker.join()       # wait until it finishes
    if status["saved"]:
        print("Report saved to", REPORT_FILE)
    else:
        print("Could not save the report.")
