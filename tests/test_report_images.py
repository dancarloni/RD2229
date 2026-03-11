"""Test gestione immagini report (Q.5)."""

from pathlib import Path

from src.report.images import image_html_block, image_markdown_block
from src.report.utils import encode_image_base64


def test_encode_image_base64_and_html_block(tmp_path: Path):
    image_path = tmp_path / "test.png"
    image_path.write_bytes(b"fakepng")

    encoded = encode_image_base64(image_path)
    html = image_html_block(image_path, caption="Immagine test")

    assert encoded
    assert "data:image/png;base64," in html
    assert "Immagine test" in html


def test_image_markdown_block(tmp_path: Path):
    image_path = tmp_path / "diag.svg"
    image_path.write_text("<svg></svg>", encoding="utf-8")
    md = image_markdown_block(image_path, caption="Schema")

    assert "![Schema]" in md
    assert "diag.svg" in md
