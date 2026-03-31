import re

from docx import Document
from pypdf import PdfReader


def extract_text_from_docx(file_path):
    document = Document(file_path)
    paragraphs = [paragraph.text.strip() for paragraph in document.paragraphs if paragraph.text.strip()]
    return '\n'.join(paragraphs), False, 'Word document parsed successfully.'


def extract_text_from_pdf(file_path):
    reader = PdfReader(file_path)
    pages = []
    for page in reader.pages:
        pages.append((page.extract_text() or '').strip())

    extracted_text = '\n'.join(page for page in pages if page)
    avg_chars = len(extracted_text.strip()) / max(len(pages), 1)
    scanned_detected = len(extracted_text.strip()) < 50 or avg_chars < 20
    note = (
        'Little or no extractable text was found. This looks like a scanned PDF and should be uploaded to Past Papers only.'
        if scanned_detected
        else 'PDF text extracted successfully.'
    )
    return extracted_text, scanned_detected, note


def parse_questions_from_text(raw_text):
    if not raw_text.strip():
        return []

    answer_map = {}
    for question_number, answer_label in re.findall(r'(\d+)\s*[\.\):-]?\s*([A-D])\b', raw_text, flags=re.IGNORECASE):
        answer_map[int(question_number)] = answer_label.upper()

    lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
    questions = []
    current_question = None

    question_pattern = re.compile(r'^(?:Q(?:uestion)?\s*)?(\d+)[\.\):-]\s*(.+)$', re.IGNORECASE)
    choice_pattern = re.compile(r'^([A-D])[\.\):-]\s*(.+)$', re.IGNORECASE)
    inline_answer_pattern = re.compile(r'^Answer\s*[:\-]\s*([A-D])$', re.IGNORECASE)

    for line in lines:
        question_match = question_pattern.match(line)
        choice_match = choice_pattern.match(line)
        answer_match = inline_answer_pattern.match(line)

        if question_match:
            if current_question and len(current_question['choices']) >= 2:
                questions.append(current_question)
            order = int(question_match.group(1))
            current_question = {
                'order': order,
                'text': question_match.group(2).strip(),
                'choices': [],
                'detected_answer_label': answer_map.get(order, ''),
            }
            continue

        if current_question and choice_match:
            current_question['choices'].append(
                {'label': choice_match.group(1).upper(), 'text': choice_match.group(2).strip()}
            )
            continue

        if current_question and answer_match:
            current_question['detected_answer_label'] = answer_match.group(1).upper()
            continue

        if current_question and not current_question['choices']:
            current_question['text'] += f' {line}'

    if current_question and len(current_question['choices']) >= 2:
        questions.append(current_question)

    return questions
