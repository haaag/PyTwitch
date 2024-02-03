# markup.py
# https://docs.gtk.org/Pango/pango_markup.html

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PangoSpan:
    text: str
    alpha: str | None = None
    background: str | None = None
    background_alpha: str | None = None
    baseline_shift: str | None = None
    bgalpha: str | None = None
    bgcolor: str | None = None
    color: str | None = None
    face: str | None = None
    fallback: str | None = None
    fgalpha: str | None = None
    fgcolor: str | None = None
    font: str | None = None
    font_desc: str | None = None
    font_family: str | None = None
    font_features: str | None = None
    font_scale: str | None = None
    font_size: str | None = None
    font_stretch: str | None = None
    font_style: str | None = None
    font_variant: str | None = None
    font_weight: str | None = None
    foreground: str | None = None
    gravity: str | None = None
    gravity_hint: str | None = None
    lang: str | None = None
    letter_spacing: str | None = None
    overline: str | None = None
    overline_color: str | None = None
    rise: str | None = None
    show: str | None = None
    size: str | None = None
    stretch: str | None = None
    strikethrough: str | None = None
    strikethrough_color: str | None = None
    style: str | None = None
    sub: bool = False
    underline: str | None = None
    underline_color: str | None = None
    variant: str | None = None
    weight: str | None = None
    markup: bool = True

    def __hash__(self):
        attrs = tuple(self.__dict__[attr] for attr in sorted(self.__dict__.keys()) if attr not in ('text', 'sub'))
        return hash((self.text, attrs))

    def __str__(self) -> str:
        if not self.markup:
            return self.text

        attrs = []
        for attr in self.__dict__:
            if attr != 'text' and attr != 'markup' and attr != 'sub' and self.__dict__[attr] is not None:
                attrs.append(f'{attr}="{self.__dict__[attr]}"')

        text = self.text
        if self.sub:
            text = f'<sub>{text}</sub>'
        return f'<span {"".join(attrs)}>{text}</span>'
