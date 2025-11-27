import os
import tempfile

from atlassian import Confluence

from app.core.config import settings
from app.core.logging import logger


class ConfluenceClient:
    def __init__(self) -> None:
        self._client: Confluence | None = None

        if not (
            settings.CONFLUENCE_URL
            and settings.CONFLUENCE_USER
            and settings.CONFLUENCE_API_TOKEN
        ):
            logger.warning(
                "Confluence settings are not fully configured. "
                "Publishing will fail until you set env vars."
            )
        else:
            self._client = Confluence(
                url=settings.CONFLUENCE_URL,
                username=settings.CONFLUENCE_USER,
                password=settings.CONFLUENCE_API_TOKEN,
                cloud=True,
            )

    def _get_client(self) -> Confluence:
        if self._client is None:
            raise RuntimeError(
                "Confluence is not configured. "
                "Please set CONFLUENCE_URL / CONFLUENCE_USER / CONFLUENCE_API_TOKEN."
            )
        return self._client

    # 👇 ищем страницу по title в space
    def get_page_id_by_title(self, title: str) -> str | None:
        client = self._get_client()
        page_id = client.get_page_id(settings.CONFLUENCE_SPACE_KEY, title)
        if page_id:
            logger.info("Found existing page for title '%s': %s", title, page_id)
            return str(page_id)
        return None

    def get_or_create_root_page(self, title: str) -> str:
        client = self._get_client()
        logger.info("Ensuring root page exists: %s", title)

        page_id = client.get_page_id(settings.CONFLUENCE_SPACE_KEY, title)
        if page_id:
            logger.info("Root page already exists: %s", page_id)
            return str(page_id)

        response = client.create_page(
            space=settings.CONFLUENCE_SPACE_KEY,
            title=title,
            body="<p>Root page for project requirements.</p>",
            parent_id=None,
            representation="storage",
        )
        created_id = str(response.get("id"))
        logger.info("Root page created: %s", created_id)
        return created_id

    def create_page(self, title: str, html_body: str, parent_id: str | None = None) -> dict:
        client = self._get_client()
        logger.info("Creating Confluence page: %s", title)
        response = client.create_page(
            space=settings.CONFLUENCE_SPACE_KEY,
            title=title,
            body=html_body,
            parent_id=parent_id,
            representation="storage",
        )
        logger.info("Confluence page created: %s", response.get("id"))
        return response

    # 👇 обновление существующей страницы
    def update_page(
            self,
            page_id: str,
            title: str,
            html_body: str,
            parent_id: str | None = None,
    ) -> dict:
        client = self._get_client()
        logger.info("Updating Confluence page: %s", page_id)

        response = client.update_page(
            page_id=page_id,
            title=title,
            body=html_body,
            parent_id=parent_id,
            type="page",
            representation="storage",
            minor_edit=True,
        )

        logger.info("Confluence page updated: %s", response.get("id"))
        return response

    def upload_mermaid_file(self, page_id: str, filename: str, mermaid_source: str) -> None:
        """
        Загружает (или перезаливает) .mmd-файл с Mermaid-кодом как вложение страницы.

        Важно:
        - Confluence.attach_file ожидает путь к файлу на диске, а не BytesIO.
        - Плагин Mermaid Diagrams for Confluence использует имя файла из параметра `filename`.
        """
        client = self._get_client()

        # гарантируем расширение .mmd
        if not filename.lower().endswith(".mmd"):
            filename = filename + ".mmd"

        # создаём временный файл с mermaid-кодом
        tmp_path = None
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mmd", mode="w", encoding="utf-8") as tmp:
                tmp.write(mermaid_source)
                tmp_path = tmp.name

            # attach_file в atlassian-python-api:
            # attach_file(filename=<path>, page_id=<id>, content_type=...)
            # Если файл с таким именем уже есть на странице, он создаст новую версию
            client.attach_file(
                filename=tmp_path,          # путь к временному файлу на диске
                page_id=page_id,
                content_type="text/plain",
            )
        finally:
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except OSError:
                    # не критично, если не удалится
                    pass



confluence_client = ConfluenceClient()
