from __future__ import annotations

from catalogo_acervo.domain.entities.theme import Theme
from catalogo_acervo.domain.services.theming import slugify_theme
from catalogo_acervo.infrastructure.db.repositories.theme_repository import ThemeRepository


class AssignThemeUseCase:
    def __init__(self, repository: ThemeRepository) -> None:
        self.repository = repository

    def create_theme(self, name: str, description: str | None = None) -> int:
        theme = Theme(name=name, slug=slugify_theme(name), description=description)
        return self.repository.add(theme)

    def list_themes(self) -> list[Theme]:
        return self.repository.list_all()

    def assign_item(self, item_id: int, theme_id: int) -> None:
        self.repository.assign_item(item_id=item_id, theme_id=theme_id)
