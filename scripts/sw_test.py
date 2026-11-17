import time
import win32com.client

sw = win32com.client.Dispatch("SldWorks.Application")
sw.Visible = True
for _ in range(60):
    try:
        rev = sw.RevisionNumber()
        break
    except Exception:
        time.sleep(2)
print("SolidWorks surum:", rev)
print("Varsayilan parca sablonu:", sw.GetUserPreferenceStringValue(8))
