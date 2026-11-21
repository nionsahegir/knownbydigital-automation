import os
import sys
import time
import json
import requests
from pathlib import Path
from config import (
    META_PAGE_ACCESS_TOKEN,
    FACEBOOK_PAGE_ID,
    INSTAGRAM_ACCOUNT_ID,
    THREADS_USER_ID,
    THREADS_ACCESS_TOKEN,
    THREADS_APP_ID,
    THREADS_APP_SECRET
)
from content_engine import assemble_seo_caption


if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

GRAPH_API_VERSION = "v21.0"
GRAPH_URL = f"https://graph.facebook.com/{GRAPH_API_VERSION}"
THREADS_URL = "https://graph.threads.net/v1.0"

def upload_media_to_public_url(local_path: str) -> str:
    """
    Instagram & Threads Graph API requires public HTTPS URLs for media ingestion.
    Uploads local image/video to public storage with zero retention issues.
    """
    if str(local_path).startswith("http://") or str(local_path).startswith("https://"):
        return local_path

    path_obj = Path(local_path)
    if not path_obj.exists():
        raise FileNotFoundError(f"Media file not found: {local_path}")

    # 1. Try Freeimage.host CDN (Works 100% reliably from cloud servers & GitHub Actions)
    try:
        with open(path_obj, "rb") as f:
            resp = requests.post(
                "https://freeimage.host/api/1/upload",
                data={"key": "6d207e02198a847aa98d0a2a901485a5", "action": "upload"},
                files={"source": f},
                timeout=60
            )
            if resp.status_code == 200:
                data = resp.json()
                img_url = data.get("image", {}).get("url")
                if img_url:
                    print(f"[Public Upload] Uploaded {path_obj.name} -> {img_url}")
                    return img_url
    except Exception as e:
        print(f"[Upload Warning] Freeimage CDN error: {e}")

    # 2. Try Catbox.moe
    try:
        with open(path_obj, "rb") as f:
            resp = requests.post(
                "https://catbox.moe/user/api.php",
                data={"reqtype": "fileupload"},
                files={"fileToUpload": (path_obj.name, f)},
                timeout=60
            )
            if resp.status_code == 200 and resp.text.startswith("https://"):
                url = resp.text.strip()
                print(f"[Public Upload] Uploaded {path_obj.name} -> {url}")
                return url
    except Exception as e:
        print(f"[Upload Warning] Catbox upload error: {e}")

    # 3. Fallback: tmpfiles.org
    try:
        with open(path_obj, "rb") as f:
            resp = requests.post(
                "https://tmpfiles.org/api/v1/upload",
                files={"file": (path_obj.name, f)},
                timeout=60
            )
            if resp.status_code == 200:
                data = resp.json()
                orig_url = data.get("data", {}).get("url", "")
                if orig_url:
                    dl_url = orig_url.replace("tmpfiles.org/", "tmpfiles.org/dl/")
                    print(f"[Public Upload] Fallback uploaded {path_obj.name} -> {dl_url}")
                    return dl_url
    except Exception as e:
        print(f"[Upload Warning] tmpfiles fallback error: {e}")

    raise RuntimeError(f"Could not upload {local_path} to public storage for Instagram API.")

class MetaPublisher:
    def __init__(self):
        self.page_token = str(META_PAGE_ACCESS_TOKEN or "").strip()
        self.page_id = str(FACEBOOK_PAGE_ID or "").strip()
        self.ig_user_id = str(INSTAGRAM_ACCOUNT_ID or "").strip()
        self.threads_user_id = str(THREADS_USER_ID or "").strip()
        self.threads_token = str(THREADS_ACCESS_TOKEN or "").strip()

    def is_configured(self) -> bool:
        """Returns True if Meta tokens are present."""
        return bool(self.page_token and self.page_id and self.ig_user_id)

    # ---------------------------------------------
    # 1. FACEBOOK PAGE PUBLISHING
    # ---------------------------------------------
    def publish_facebook_post(self, message: str, image_path: str = None) -> dict:
        """Publishes text or photo post to Facebook Page."""
        if not self.is_configured():
            print(f"[Simulation Mode - FB] Post simulated: '{message[:60]}...'")
            return {"status": "simulated", "platform": "facebook"}

        url = f"{GRAPH_URL}/{self.page_id}/feed"
        if image_path and os.path.exists(image_path):
            url = f"{GRAPH_URL}/{self.page_id}/photos"
            with open(image_path, "rb") as img_file:
                payload = {"caption": message, "access_token": self.page_token}
                files = {"source": img_file}
                resp = requests.post(url, data=payload, files=files, timeout=45)
                return resp.json()
        else:
            payload = {"message": message, "access_token": self.page_token}
            resp = requests.post(url, data=payload, timeout=30)
            return resp.json()

    def publish_facebook_carousel(self, image_paths_or_urls: list, caption: str) -> dict:
        """Publishes a real multi-photo album post to Facebook Page with all slides."""
        if not self.is_configured():
            return {"status": "simulated", "platform": "facebook_carousel"}

        media_fbids = []
        for i, img in enumerate(image_paths_or_urls):
            try:
                url = f"{GRAPH_URL}/{self.page_id}/photos"
                if os.path.exists(str(img)):
                    with open(img, "rb") as f:
                        resp = requests.post(
                            url,
                            data={"published": "false", "access_token": self.page_token},
                            files={"source": f},
                            timeout=45
                        ).json()
                else:
                    img_url = upload_media_to_public_url(img)
                    resp = requests.post(
                        url,
                        data={"url": img_url, "published": "false", "access_token": self.page_token},
                        timeout=30
                    ).json()

                fbid = resp.get("id")
                if fbid:
                    media_fbids.append({"media_fbid": fbid})
                else:
                    print(f"[Facebook Multi-Photo Note] Slide {i+1} upload: {resp}")
            except Exception as e:
                print(f"[Facebook Multi-Photo Error] Slide {i+1}: {e}")

        if not media_fbids:
            return self.publish_facebook_post(caption)

        feed_url = f"{GRAPH_URL}/{self.page_id}/feed"
        feed_payload = {
            "message": caption,
            "attached_media": json.dumps(media_fbids),
            "access_token": self.page_token
        }
        res_feed = requests.post(feed_url, data=feed_payload, timeout=30).json()
        if "id" in res_feed:
            print(f"[Facebook Carousel Album Published] Post ID: {res_feed.get('id')}")
        return res_feed

    def publish_facebook_video(self, video_path_or_url: str, description: str, title: str = None) -> dict:
        """Publishes video or Reel to Facebook Page via direct multipart binary upload or public URL."""
        if not self.is_configured():
            return {"status": "simulated", "platform": "facebook_video"}

        url = f"{GRAPH_URL}/{self.page_id}/videos"
        data = {
            "description": description,
            "access_token": self.page_token
        }
        if title:
            data["title"] = title

        # Direct file upload if local file exists (100% reliable, zero CDN dependency)
        if os.path.exists(str(video_path_or_url)):
            try:
                with open(video_path_or_url, "rb") as f:
                    resp = requests.post(url, data=data, files={"source": f}, timeout=120).json()
                    if "id" in resp:
                        print(f"[Facebook Video Published] Post ID: {resp.get('id')}")
                    else:
                        print(f"[Facebook Video Note] {resp.get('error', {}).get('message', resp)}")
                    return resp
            except Exception as e:
                print(f"[Facebook Video Error] {e}")
                return {"error": str(e)}

        # Fallback to public URL
        video_url = upload_media_to_public_url(video_path_or_url)
        data["file_url"] = video_url
        try:
            resp = requests.post(url, data=data, timeout=60).json()
            if "id" in resp:
                print(f"[Facebook Video Published] Post ID: {resp.get('id')}")
            else:
                print(f"[Facebook Video Note] {resp.get('error', {}).get('message', resp)}")
            return resp
        except Exception as e:
            print(f"[Facebook Video Error] {e}")
            return {"error": str(e)}


    # ---------------------------------------------
    # 2. INSTAGRAM PUBLISHING (Single, Carousel, Reel)
    # ---------------------------------------------
    def publish_instagram_photo(self, image_path_or_url: str, caption: str) -> dict:
        """Publishes a single photo post to Instagram Business Account."""
        if not self.is_configured():
            print(f"[Simulation Mode - IG Photo] Simulated: '{caption[:60]}...'")
            return {"status": "simulated", "platform": "instagram_photo"}

        # Get public URL
        image_url = upload_media_to_public_url(image_path_or_url)

        # Step 1: Create Container
        container_url = f"{GRAPH_URL}/{self.ig_user_id}/media"
        c_payload = {
            "image_url": image_url,
            "caption": caption,
            "access_token": self.page_token
        }
        c_res = requests.post(container_url, data=c_payload, timeout=30).json()
        creation_id = c_res.get("id")

        if not creation_id:
            return {"error": "Failed to create IG photo container", "details": c_res}

        # Step 2: Ensure Container is ready before publishing (poll up to 60s)
        status_url = f"{GRAPH_URL}/{creation_id}?fields=status_code,status&access_token={self.page_token}"
        for attempt in range(20):
            time.sleep(3)
            s_res = requests.get(status_url, timeout=15).json()
            code = s_res.get("status_code")
            if code == "FINISHED":
                break
            elif code == "ERROR":
                print(f"[Instagram Container Error] {s_res}")
                return {"error": "Instagram container processing failed", "details": s_res}

        # Step 3: Publish Container (with auto-retry if Meta is still processing)
        pub_url = f"{GRAPH_URL}/{self.ig_user_id}/media_publish"
        for pub_attempt in range(5):
            p_res = requests.post(pub_url, data={"creation_id": creation_id, "access_token": self.page_token}, timeout=30).json()
            media_id = p_res.get("id")
            if media_id:
                info = requests.get(f"{GRAPH_URL}/{media_id}?fields=permalink&access_token={self.page_token}", timeout=15).json()
                p_res["permalink"] = info.get("permalink")
                print(f"[Instagram Photo Published] Live URL: {p_res['permalink']}")
                return p_res
            elif "not ready" in str(p_res).lower():
                print(f"[Instagram Note] Container not ready yet. Retrying in 5s... ({pub_attempt+1}/5)")
                time.sleep(5)
            else:
                print(f"[Instagram Publish Error] Meta returned: {p_res}")
                break

        return p_res

    def publish_instagram_carousel(self, image_paths_or_urls: list, caption: str) -> dict:
        """Publishes a multi-slide carousel post to Instagram."""
        if not self.is_configured():
            print(f"[Simulation Mode - IG Carousel] Simulated {len(image_paths_or_urls)} slides: '{caption[:60]}...'")
            return {"status": "simulated", "platform": "instagram_carousel", "slides": len(image_paths_or_urls)}

        # Upload slides if local
        image_urls = [upload_media_to_public_url(p) for p in image_paths_or_urls]

        # Step 1: Create child item containers
        children = []
        for img_url in image_urls:
            c_url = f"{GRAPH_URL}/{self.ig_user_id}/media"
            res = requests.post(c_url, data={"image_url": img_url, "is_carousel_item": True, "access_token": self.page_token}, timeout=30).json()
            if "id" in res:
                children.append(res["id"])
            else:
                print(f"[Carousel Child Error] Failed for {img_url}: {res}")

        if not children:
            return {"error": "Failed to create carousel items"}

        # Step 1.5: Ensure all child containers are FINISHED before creating parent
        for child_id in children:
            status_url = f"{GRAPH_URL}/{child_id}?fields=status_code,status&access_token={self.page_token}"
            for _ in range(8):
                s_res = requests.get(status_url, timeout=15).json()
                if s_res.get("status_code") == "FINISHED":
                    break
                time.sleep(2)

        # Step 2: Create parent carousel container
        parent_url = f"{GRAPH_URL}/{self.ig_user_id}/media"
        parent_res = requests.post(parent_url, data={
            "media_type": "CAROUSEL",
            "children": ",".join(children),
            "caption": caption,
            "access_token": self.page_token
        }, timeout=30).json()

        creation_id = parent_res.get("id")
        if not creation_id:
            return {"error": "Failed to create parent carousel", "details": parent_res}

        # Step 2.5: Ensure parent container is FINISHED before publishing (poll up to 60s)
        status_url = f"{GRAPH_URL}/{creation_id}?fields=status_code,status&access_token={self.page_token}"
        for _ in range(20):
            time.sleep(3)
            s_res = requests.get(status_url, timeout=15).json()
            if s_res.get("status_code") == "FINISHED":
                break

        # Step 3: Publish Carousel (with auto-retry)
        pub_url = f"{GRAPH_URL}/{self.ig_user_id}/media_publish"
        for pub_attempt in range(5):
            p_res = requests.post(pub_url, data={"creation_id": creation_id, "access_token": self.page_token}, timeout=30).json()
            media_id = p_res.get("id")
            if media_id:
                time.sleep(2)
                info = requests.get(f"{GRAPH_URL}/{media_id}?fields=permalink&access_token={self.page_token}", timeout=15).json()
                p_res["permalink"] = info.get("permalink")
                print(f"[Instagram Carousel Published] Live URL: {p_res['permalink']}")
                return p_res
            elif "not ready" in str(p_res).lower():
                print(f"[Instagram Carousel Note] Parent container not ready yet. Retrying in 5s... ({pub_attempt+1}/5)")
                time.sleep(5)
            else:
                print(f"[Instagram Carousel Publish Error] Meta returned: {p_res}")
                break

        return p_res

    def publish_instagram_reel(self, video_path_or_url: str, caption: str, cover_path_or_url: str = None) -> dict:
        """
        Publishes a vertical video as an Instagram Reel.
        Utilizes Meta's official direct resumable upload protocol for local files,
        streaming video bytes directly to rupload.facebook.com to bypass any 3rd party host blocks.
        """
        if not self.is_configured():
            print(f"[Simulation Mode - IG Reel] Simulated: '{caption[:60]}...'")
            return {"status": "simulated", "platform": "instagram_reel"}

        local_video = Path(video_path_or_url) if os.path.exists(str(video_path_or_url)) else None

        # Prepare optional cover thumbnail (uploaded to public CDN)
        cover_url = None
        if cover_path_or_url:
            cover_url = upload_media_to_public_url(cover_path_or_url)
            print(f"[Instagram Reel] Cover thumbnail public URL ready: {cover_url}")

        if local_video:
            # -------------------------------------------------------------
            # DIRECT RESUMABLE UPLOAD TO META RUPLOAD INFRASTRUCTURE
            # -------------------------------------------------------------
            file_size = os.path.getsize(local_video)
            print(f"[Instagram Reel] Initializing direct resumable upload session ({file_size} bytes)...")
            
            init_url = f"{GRAPH_URL}/{self.ig_user_id}/media"
            init_payload = {
                "access_token": self.page_token,
                "upload_type": "resumable",
                "media_type": "REELS",
                "caption": caption,
                "thumb_offset": 2500,
                "share_to_feed": True,
            }
            if cover_url:
                init_payload["cover_url"] = cover_url

            init_res = requests.post(init_url, data=init_payload, timeout=30).json()
            creation_id = init_res.get("id")
            upload_uri = init_res.get("uri")

            if not creation_id or not upload_uri:
                return {"error": "Failed to initialize Reel resumable upload container", "details": init_res}

            print(f"[Instagram Reel] Uploading video binary directly to Meta rupload ({creation_id})...")
            upload_headers = {
                "Authorization": f"OAuth {self.page_token}",
                "offset": "0",
                "file_size": str(file_size),
                "Content-Type": "application/octet-stream",
            }
            with open(local_video, "rb") as f:
                up_res = requests.post(upload_uri, headers=upload_headers, data=f, timeout=120)

            if up_res.status_code != 200:
                return {"error": "Direct video binary upload to Meta rupload failed", "details": up_res.text}

        else:
            # Fallback for already-public URLs
            video_url = upload_media_to_public_url(video_path_or_url)
            container_url = f"{GRAPH_URL}/{self.ig_user_id}/media"
            c_payload = {
                "media_type": "REELS",
                "video_url": video_url,
                "caption": caption,
                "thumb_offset": 2500,
                "share_to_feed": True,
                "access_token": self.page_token
            }
            if cover_url:
                c_payload["cover_url"] = cover_url

            c_res = requests.post(container_url, data=c_payload, timeout=30).json()
            creation_id = c_res.get("id")
            if not creation_id:
                return {"error": "Failed to create IG Reel container", "details": c_res}

        print(f"[Instagram Reel] Container {creation_id} ready. Awaiting Meta video encoding...")

        # Step 2: Poll container status until FINISHED
        status_url = f"{GRAPH_URL}/{creation_id}?fields=status_code,status&access_token={self.page_token}"
        max_attempts = 24  # 24 * 5s = 2 minutes max
        for attempt in range(max_attempts):
            time.sleep(5)
            s_res = requests.get(status_url, timeout=20).json()
            code = s_res.get("status_code", "")
            print(f"[Instagram Reel Status] Check {attempt+1}/{max_attempts}: {code}")
            
            if code == "FINISHED":
                break
            elif code == "ERROR":
                return {"error": "Instagram Reel encoding failed on Meta servers", "details": s_res}
        else:
            return {"error": "Instagram Reel processing timed out on Meta servers"}

        # Step 3: Publish Reel Container
        pub_url = f"{GRAPH_URL}/{self.ig_user_id}/media_publish"
        p_res = requests.post(pub_url, data={"creation_id": creation_id, "access_token": self.page_token}, timeout=30).json()

        media_id = p_res.get("id")
        if media_id:
            info = requests.get(f"{GRAPH_URL}/{media_id}?fields=permalink&access_token={self.page_token}", timeout=15).json()
            p_res["permalink"] = info.get("permalink")
            print(f"[Instagram Reel Published] Live URL: {p_res['permalink']}")

        return p_res

    def publish_instagram_story(self, media_path_or_url: str) -> dict:
        """Publishes an Instagram Story (1080x1920 vertical image or video)."""
        if not self.is_configured():
            print(f"[Simulation Mode - IG Story] Simulated: {media_path_or_url}")
            return {"status": "simulated", "platform": "instagram_story"}

        media_url = upload_media_to_public_url(media_path_or_url)
        print(f"[Instagram Story] Media public URL ready: {media_url}")

        is_video = str(media_path_or_url).lower().endswith((".mp4", ".mov", ".webm"))
        container_url = f"{GRAPH_URL}/{self.ig_user_id}/media"
        payload = {
            "media_type": "STORIES",
            "access_token": self.page_token
        }
        if is_video:
            payload["video_url"] = media_url
        else:
            payload["image_url"] = media_url

        c_res = requests.post(container_url, data=payload, timeout=30).json()
        creation_id = c_res.get("id")
        if not creation_id:
            return {"error": "Failed to create Instagram Story container", "details": c_res}

        if is_video:
            status_url = f"{GRAPH_URL}/{creation_id}?fields=status_code&access_token={self.page_token}"
            for _ in range(24):
                time.sleep(5)
                s_res = requests.get(status_url, timeout=20).json()
                if s_res.get("status_code") == "FINISHED":
                    break
                elif s_res.get("status_code") == "ERROR":
                    return {"error": "Story video encoding failed", "details": s_res}

        pub_url = f"{GRAPH_URL}/{self.ig_user_id}/media_publish"
        p_res = requests.post(pub_url, data={"creation_id": creation_id, "access_token": self.page_token}, timeout=30).json()
        media_id = p_res.get("id")
        if media_id:
            p_res["status"] = "published"
            p_res["story_id"] = media_id
            print(f"[Instagram Story Published] Story Media ID: {media_id}")
        return p_res

    # ---------------------------------------------
    # 3. THREADS PUBLISHING
    # ---------------------------------------------
    def refresh_threads_token(self) -> dict:
        """Refreshes the long-lived Threads access token for another 60 days."""
        if not self.threads_token:
            return {"error": "No Threads access token found"}
        try:
            r = requests.get("https://graph.threads.net/refresh_access_token", params={
                "grant_type": "th_refresh_token",
                "access_token": self.threads_token
            }, timeout=30)
            if r.status_code == 200:
                data = r.json()
                new_token = data.get("access_token")
                if new_token:
                    self.threads_token = new_token
                    print(f"[Threads Token Refreshed] Valid for {data.get('expires_in', 0)} seconds (~60 days).")
                return data
            return r.json()
        except Exception as e:
            return {"error": str(e)}

    def publish_threads_post(self, text: str, image_url: str = None, video_url: str = None) -> dict:
        """Publishes text, image, or video post to Meta Threads."""
        if not (self.threads_user_id and self.threads_token):
            print(f"[Simulation Mode - Threads] Simulated: '{text[:60]}...'")
            return {"status": "simulated", "platform": "threads"}

        # Upload local files to public URL if needed
        if image_url and not (str(image_url).startswith("http://") or str(image_url).startswith("https://")):
            image_url = upload_media_to_public_url(image_url)

        if video_url and not (str(video_url).startswith("http://") or str(video_url).startswith("https://")):
            video_url = upload_media_to_public_url(video_url)

        media_type = "TEXT"
        if video_url:
            media_type = "VIDEO"
        elif image_url:
            media_type = "IMAGE"

        # Step 1: Create Threads Container
        container_url = f"{THREADS_URL}/{self.threads_user_id}/threads"
        payload = {
            "media_type": media_type,
            "text": text,
            "access_token": self.threads_token
        }
        if video_url:
            payload["video_url"] = video_url
        elif image_url:
            payload["image_url"] = image_url

        c_res = requests.post(container_url, data=payload, timeout=30).json()
        creation_id = c_res.get("id")
        if not creation_id:
            return {"error": "Failed to create Threads container", "details": c_res}

        # Step 2: Ensure Container is ready (poll for video, brief sleep for image)
        if media_type == "VIDEO":
            status_url = f"{THREADS_URL}/{creation_id}?fields=status,error_message&access_token={self.threads_token}"
            for _ in range(24):
                time.sleep(5)
                s_res = requests.get(status_url, timeout=20).json()
                if s_res.get("status") == "FINISHED":
                    break
                elif s_res.get("status") == "ERROR":
                    return {"error": "Threads video processing failed", "details": s_res}
        else:
            time.sleep(3)

        # Step 3: Publish Threads Container
        pub_url = f"{THREADS_URL}/{self.threads_user_id}/threads_publish"
        p_res = requests.post(pub_url, data={"creation_id": creation_id, "access_token": self.threads_token}, timeout=30).json()
        media_id = p_res.get("id")
        if media_id:
            try:
                time.sleep(1)
                info = requests.get(f"{THREADS_URL}/{media_id}?fields=permalink&access_token={self.threads_token}", timeout=15).json()
                p_res["permalink"] = info.get("permalink")
                print(f"[Threads Post Published] Live URL: {p_res['permalink']}")
            except Exception:
                pass
        return p_res

    # ---------------------------------------------
    # 4. SIMULTANEOUS DISPATCH
    # ---------------------------------------------
    def broadcast_daily_pack(self, pack: dict, generated_media: dict) -> dict:
        """Publishes Reel, Single Post, and Carousel across Instagram and Facebook."""
        results = {}

        single_post = pack.get("single_post", {})
        carousel = pack.get("carousel", {})
        reel = pack.get("reel", {})

        # 1. Single Post (Instagram Only during initial review phase)
        post_img = generated_media.get("single_post_image")
        if post_img:
            caption = assemble_seo_caption(single_post) if single_post else ""
            results["instagram_single_post"] = self.publish_instagram_photo(post_img, caption)
            # Facebook & Threads paused until user review approval
            results["facebook_post"] = {"status": "paused_awaiting_user_approval"}
            results["threads_post"] = {"status": "paused_awaiting_user_approval"}

        # 2. Carousel
        carousel_imgs = generated_media.get("carousel_slides", [])
        if carousel_imgs:
            caption = assemble_seo_caption(carousel) if carousel else ""
            results["instagram_carousel"] = self.publish_instagram_carousel(carousel_imgs, caption)

        # 3. Faceless Reel
        reel_video = generated_media.get("reel_video")
        reel_cover = generated_media.get("reel_cover")
        if isinstance(reel_video, (list, tuple)):
            reel_cover = reel_video[1] if len(reel_video) > 1 else reel_cover
            reel_video = reel_video[0]

        if reel_video:
            caption = assemble_seo_caption(reel) if reel else ""
            results["instagram_reel"] = self.publish_instagram_reel(reel_video, caption, cover_path_or_url=reel_cover)

        # 4. Instagram Story
        story_img = generated_media.get("story_image")
        if story_img:
            results["instagram_story"] = self.publish_instagram_story(story_img)

        return results

if __name__ == "__main__":
    pub = MetaPublisher()
    print("Meta Publisher configured:", pub.is_configured())
