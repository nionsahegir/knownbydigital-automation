import requests
from config import META_PAGE_ACCESS_TOKEN, INSTAGRAM_ACCOUNT_ID

# Let's check with Meta Graph API if this post belongs to Known By Digital!
# Shortcode DSR3McLlTNm
shortcode = "DSR3McLlTNm"

# Fetch recent media of @knownbydigital to find this post
url = f"https://graph.facebook.com/v21.0/{INSTAGRAM_ACCOUNT_ID}/media?fields=id,caption,media_type,media_url,permalink,thumbnail_url&limit=25&access_token={META_PAGE_ACCESS_TOKEN}"
res = requests.get(url).json()

found = False
for item in res.get("data", []):
    if shortcode in item.get("permalink", ""):
        print("FOUND POST ON KNOWN BY DIGITAL!")
        print("ID:", item.get("id"))
        print("Type:", item.get("media_type"))
        print("Caption:", item.get("caption", "")[:100])
        print("Media URL:", item.get("media_url"))
        print("Permalink:", item.get("permalink"))
        found = True
        break

if not found:
    print("Post shortcode not in recent 25 posts, checking details...")
