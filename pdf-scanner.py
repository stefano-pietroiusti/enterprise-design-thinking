import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import os
import re


def sanitize_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "", name).strip()


def download_ibm_named_pdfs(url, output_folder="ibm_named_pdfs"):
    os.makedirs(output_folder, exist_ok=True)

    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    headings = soup.find_all("c4d-card-heading")
    downloads = soup.find_all("c4d-text-cta", href=True)

    print(f"Found {len(downloads)} download links.")

    for i, download in enumerate(downloads):
        link = urljoin(url, download["href"])

        # Try to get the corresponding heading if available
        title = None
        if i < len(headings):
            title = headings[i].get_text(strip=True)

        # Use heading if found, else fallback to document ID
        if title:
            filename = sanitize_filename(title) + ".pdf"
        else:
            doc_id = os.path.basename(urlparse(link).path)
            filename = f"{doc_id}.pdf"

        filepath = os.path.join(output_folder, filename)

        try:
            pdf_response = requests.get(link)
            pdf_response.raise_for_status()
            with open(filepath, "wb") as f:
                f.write(pdf_response.content)
            print(f"Saved: {filename}")
        except Exception as e:
            print(f"Failed to download {link}: {e}")


# Run the function
download_ibm_named_pdfs(
    "https://www.ibm.com/training/enterprise-design-thinking/toolkit"
)
