from fastapi.testclient import TestClient
from app.main import app
import io

client = TestClient(app)

def test_upload_pdf():
    file_content = b"%PDF-1.4 test pdf"
    response = client.post(
        "/upload",
        files={"file": ("test.pdf", io.BytesIO(file_content), "application/pdf")}
    )
    assert response.status_code == 200
    assert "file_id" in response.json()
