import hashlib
from typing import Any, Dict, List, Optional
import httpx
from ..base import BaseAdapter
from ...engine.models import SourceExecutionResult, ResultStatus, ConfidenceLevel

PLATFORMS = [
    {"name": "GitHub", "url_pattern": "https://github.com/{username}", "api": True},
    {"name": "GitLab", "url_pattern": "https://gitlab.com/{username}", "api": True},
    {"name": "Gravatar", "url_pattern": "https://gravatar.com/{username}", "api": True},
    {"name": "Reddit", "url_pattern": "https://www.reddit.com/user/{username}", "api": False},
    {"name": "Twitter / X", "url_pattern": "https://x.com/{username}", "api": False},
    {"name": "Instagram", "url_pattern": "https://www.instagram.com/{username}/", "api": False},
    {"name": "LinkedIn", "url_pattern": "https://www.linkedin.com/in/{username}", "api": False},
    {"name": "TikTok", "url_pattern": "https://www.tiktok.com/@{username}", "api": False},
    {"name": "Telegram", "url_pattern": "https://t.me/{username}", "api": False},
    {"name": "YouTube", "url_pattern": "https://www.youtube.com/@{username}", "api": False},
    {"name": "Medium", "url_pattern": "https://medium.com/@{username}", "api": False},
    {"name": "Dev.to", "url_pattern": "https://dev.to/{username}", "api": False},
]

class UsernameAdapter(BaseAdapter):
    adapter_id = "username_adapter"
    name = "Pesquisa de Username e Perfis Públicos"
    category = "username"
    description = "Consulta a APIs públicas oficiais (GitHub, GitLab, Gravatar) e geração de links de verificação para as principais redes sociais."
    official_url = "https://github.com"
    supported_inputs = ["username"]

    async def run(self, target: str, context: Optional[Dict[str, Any]] = None) -> SourceExecutionResult:
        username = (target or "").strip().lstrip("@")
        if not username:
            return SourceExecutionResult(
                source_id=self.adapter_id,
                source_name=self.name,
                category=self.category,
                status=ResultStatus.ERROR,
                timestamp="",
                execution_time_ms=0,
                error_message="Username não pode ser vazio.",
                confidence=ConfidenceLevel.LOW,
            )

        confirmed_profiles = []
        target_links = []

        async with self.get_client() as client:
            # 1. Consulta GitHub API pública
            github_url = f"https://api.github.com/users/{username}"
            try:
                gh_resp = await client.get(
                    github_url,
                    headers={"Accept": "application/vnd.github.v3+json", "User-Agent": "OSINT-Brazuca-Ultimate"}
                )
                if gh_resp.status_code == 200:
                    gh_data = gh_resp.json()
                    confirmed_profiles.append({
                        "plataforma": "GitHub",
                        "status": "Confirmado via API Oficial",
                        "perfil_url": gh_data.get("html_url"),
                        "nome": gh_data.get("name"),
                        "bio": gh_data.get("bio"),
                        "localizacao": gh_data.get("location"),
                        "repositorios_publicos": gh_data.get("public_repos"),
                        "seguidores": gh_data.get("followers"),
                        "criado_em": gh_data.get("created_at"),
                        "avatar_url": gh_data.get("avatar_url"),
                    })
            except Exception:
                pass

            # 2. Consulta GitLab API pública
            gitlab_url = f"https://gitlab.com/api/v4/users?username={username}"
            try:
                gl_resp = await client.get(gitlab_url)
                if gl_resp.status_code == 200:
                    gl_data = gl_resp.json()
                    if isinstance(gl_data, list) and len(gl_data) > 0:
                        u = gl_data[0]
                        confirmed_profiles.append({
                            "plataforma": "GitLab",
                            "status": "Confirmado via API Oficial",
                            "perfil_url": u.get("web_url"),
                            "nome": u.get("name"),
                            "avatar_url": u.get("avatar_url"),
                        })
            except Exception:
                pass

        # 3. Gerar links para conferência manual de outras plataformas
        for p in PLATFORMS:
            url = p["url_pattern"].format(username=username)
            is_already_confirmed = any(c["plataforma"] == p["name"] for c in confirmed_profiles)
            if not is_already_confirmed:
                target_links.append({
                    "plataforma": p["name"],
                    "url": url,
                    "status": "Não verificado via automação (conferir manualmente no navegador)",
                })

        normalized = {
            "username_pesquisado": username,
            "total_confirmados_api": len(confirmed_profiles),
            "perfis_confirmados": confirmed_profiles,
            "links_para_verificacao_manual": target_links,
        }

        status = ResultStatus.CONFIRMED if confirmed_profiles else ResultStatus.UNCONFIRMED

        return SourceExecutionResult(
            source_id=self.adapter_id,
            source_name=self.name,
            category=self.category,
            status=status,
            timestamp="",
            execution_time_ms=0,
            data=normalized,
            verification_url=f"https://github.com/{username}",
            confidence=ConfidenceLevel.HIGH if confirmed_profiles else ConfidenceLevel.MEDIUM,
            limitations=[
                "Perfis confirmados exclusivamente por APIs públicas oficiais sem contorno de restrições.",
                "Para plataformas sem API aberta, links diretos são fornecidos para conferência manual responsável.",
            ]
        )

