import pytest
from unittest.mock import patch, MagicMock, mock_open
from app.services.pdf_extractor import extract_text_from_pdf

# ---------------------------
# Test: extract_text_from_pdf
# ---------------------------
@patch("builtins.open", new_callable=mock_open, read_data=b"%PDF-1.4 fake pdf content")
@patch("PyPDF2.PdfReader")
def test_extract_text_from_pdf(mock_pdf_reader, mock_open):
    # Mock the pages and their extract_text method
    mock_page1 = MagicMock()
    mock_page1.extract_text.return_value = "Hello "
    mock_page2 = MagicMock()
    mock_page2.extract_text.return_value = "World!"
    mock_pdf_reader.return_value.pages = [mock_page1, mock_page2]

    result = extract_text_from_pdf("fake/path.pdf")

    # Check final text
    assert result == "Hello World!"

    # Ensure open was called correctly
    mock_open.assert_called_once_with("fake/path.pdf", "rb")

    # Ensure each page's extract_text was called
    mock_page1.extract_text.assert_called_once()
    mock_page2.extract_text.assert_called_once()


# ---------------------------
# Test: page returns None
# ---------------------------
@patch("builtins.open", new_callable=mock_open, read_data=b"%PDF-1.4 fake pdf content")
@patch("PyPDF2.PdfReader")
def test_extract_text_from_pdf_none_page(mock_pdf_reader, mock_open):
    mock_page = MagicMock()
    mock_page.extract_text.return_value = None  # simulate empty page
    mock_pdf_reader.return_value.pages = [mock_page]

    result = extract_text_from_pdf("fake/path.pdf")

    # Should not fail and return empty string for None page
    assert result == ""

    mock_open.assert_called_once_with("fake/path.pdf", "rb")
    mock_page.extract_text.assert_called_once()
