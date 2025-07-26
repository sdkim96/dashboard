details = """


"""

body = {
  "work_details": details
}
import requests
resp = requests.post(
    "http://localhost:8000/api/v1/recommendations",
    json=body
)
print(resp.json())
