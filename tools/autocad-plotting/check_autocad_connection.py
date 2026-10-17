"""
Quick check that Python can talk to AutoCAD (via pyautocad / COM).

Run this first if plot_points_to_autocad.py fails to connect.
Open AutoCAD with a drawing before running:  python check_autocad_connection.py

Common fixes if it fails:
    - AutoCAD must be the full version (AutoCAD LT has no COM API).
    - Run Python and AutoCAD as the same user (both normal, or both "as admin").
    - Click into the AutoCAD window and press Esc so no command is in progress.
    - pip install --upgrade pyautocad comtypes
"""

from pyautocad import Autocad

print("START")
try:
    # create_if_not_exists=False -> don't launch a new AutoCAD, use the open one
    acad = Autocad(create_if_not_exists=False)
    acad.prompt("Hello from Python\n")
    doc = acad.ActiveDocument
    print("Connected. Active drawing:", doc.Name)
    try:
        model = doc.ModelSpace
        print("ModelSpace available, objects in drawing:", model.Count)
    except Exception as e:
        print("ModelSpace error:", e)
except Exception as e:
    print("Connection ERROR:", e)
print("END")
