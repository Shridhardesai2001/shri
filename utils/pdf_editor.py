from PyPDF2 import PdfReader, PdfWriter
from io import BytesIO


def edit_pdf_text(pdf_bytes, old_text, new_text):
	reader = PdfReader(BytesIO(pdf_bytes))
	writer = PdfWriter()
	for page in reader.pages:
		content = page.extract_text() or ""
		# Placeholder: Real text replacement in PDFs is non-trivial. This is a stub.
		if old_text and new_text and old_text in content:
			_ = content.replace(old_text, new_text)
		writer.add_page(page)
	output = BytesIO()
	writer.write(output)
	output.seek(0)
	return output.read()

