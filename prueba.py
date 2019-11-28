
import requests
res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "GOv5GE123S6v9stJnks7BA", "isbns": "9781632168146"})
print(res.json())
