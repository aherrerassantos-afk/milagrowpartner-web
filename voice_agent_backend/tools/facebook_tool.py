"""
MILA Voice Agent — Facebook/Instagram Tool
Legge metriche e pubblica contenuti su Facebook e Instagram
"""

import os
import asyncio
import httpx
from dotenv import load_dotenv

load_dotenv()

META_BASE_URL = "https://graph.facebook.com/v21.0"


class FacebookTool:
    """Interfaccia Meta Graph API per il Voice Agent."""

    def __init__(self):
        self.access_token = os.getenv("META_ACCESS_TOKEN", "")
        self.pba_page_id = os.getenv("META_PBA_PAGE_ID", "")
        self.pba_ig_id = os.getenv("META_PBA_IG_ID", "")

    async def get_page_insights(self, page_id: str = None) -> str:
        """Ritorna le metriche degli ultimi post della pagina."""
        page_id = page_id or self.pba_page_id
        if not page_id:
            return "ID pagina non configurato."

        async with httpx.AsyncClient(timeout=15) as client:
            # Ultimi 5 post
            resp = await client.get(
                f"{META_BASE_URL}/{page_id}/posts",
                params={
                    "access_token": self.access_token,
                    "fields": "message,created_time,likes.summary(true),comments.summary(true)",
                    "limit": 5
                }
            )
            data = resp.json()
            posts = data.get("data", [])

            if not posts:
                return "Nessun post trovato."

            lines = []
            for post in posts:
                likes = post.get("likes", {}).get("summary", {}).get("total_count", 0)
                comments = post.get("comments", {}).get("summary", {}).get("total_count", 0)
                message = (post.get("message", "")[:80] + "...") if post.get("message") else "(no testo)"
                date = post.get("created_time", "")[:10]
                lines.append(f"• {date}: {likes}❤️ {comments}💬 — {message}")

            return "\n".join(lines)

    async def get_ig_insights(self, ig_id: str = None) -> str:
        """Ritorna le metriche dell'account Instagram."""
        ig_id = ig_id or self.pba_ig_id
        if not ig_id:
            return "ID Instagram non configurato."

        async with httpx.AsyncClient(timeout=15) as client:
            # Ultimi post Instagram
            resp = await client.get(
                f"{META_BASE_URL}/{ig_id}/media",
                params={
                    "access_token": self.access_token,
                    "fields": "caption,timestamp,like_count,comments_count,media_type",
                    "limit": 5
                }
            )
            data = resp.json()
            posts = data.get("data", [])

            if not posts:
                return "Nessun post Instagram trovato."

            lines = []
            for post in posts:
                likes = post.get("like_count", 0)
                comments = post.get("comments_count", 0)
                caption = (post.get("caption", "")[:80] + "...") if post.get("caption") else "(no caption)"
                date = post.get("timestamp", "")[:10]
                media_type = post.get("media_type", "")
                lines.append(f"• {date} [{media_type}]: {likes}❤️ {comments}💬 — {caption}")

            return "\n".join(lines)

    async def get_account_stats(self) -> str:
        """Ritorna statistiche generali dell'account."""
        async with httpx.AsyncClient(timeout=15) as client:
            ig_id = self.pba_ig_id
            if not ig_id:
                return "ID Instagram non configurato."

            resp = await client.get(
                f"{META_BASE_URL}/{ig_id}",
                params={
                    "access_token": self.access_token,
                    "fields": "name,followers_count,follows_count,media_count,biography"
                }
            )
            data = resp.json()

            return (
                f"Account: {data.get('name', '?')}\n"
                f"Followers: {data.get('followers_count', 0):,}\n"
                f"Following: {data.get('follows_count', 0):,}\n"
                f"Post totali: {data.get('media_count', 0)}"
            )
