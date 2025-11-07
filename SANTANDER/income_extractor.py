#!/usr/bin/env python3
"""Income extractor for Santander statements (moved into SANTANDER folder).

This is a copy of the extractor previously at the repo root. Use the README in this folder
for Santander-specific instructions.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from dataclasses import dataclass, asdict
from typing import List, Optional

import pdfplumber
from typing import Union

try:
    from pdf2image import convert_from_path
    from PIL import Image
    import pytesseract
    _OCR_AVAILABLE = True
except Exception:
    convert_from_path = None  # type: ignore
    Image = None  # type: ignore
    pytesseract = None  # type: ignore
    _OCR_AVAILABLE = False


AMOUNT_RE = re.compile(r"(\d{1,3}(?:\.\d{3})*,\d{2})")
DATE_RE = re.compile(r"\b(\d{2}/\d{2}/(?:\d{2,4}))\b")


def br_to_float(s: str) -> float:
    s = s.replace('.', '').replace(',', '.')
    try:
        return float(s)
    except Exception:
        raise ValueError(f"Não foi possível converter '{s}' para float")


def is_incoming(line: str) -> bool:
    line_up = line.upper()
    inc_positive = ['RECEBIDO', 'RECEBIMENTO', 'DEP', 'DEPÓSITO', 'DEPOSITO', 'CRÉDITO', 'CRED', 'CREDITO', 'CR\b']
    inc_loose = ['TRANSFERÊNCIA RECEBIDA', 'TRANSFERENCIA RECEBIDA', 'TED RECEBIDO', 'DOC RECEBIDO']
    exc_keywords = ['SAQUE', 'PAGAMENTO', 'COMPRA', 'TARIFA', 'TAXA', 'DEBITO', 'DÉBITO', 'PAGTO', 'ESTORNO', 'ENVIADO', 'LIMITE']

    if any(e in line_up for e in exc_keywords):
        return False

    if any(k in line_up for k in inc_positive):
        return True

    if any(k in line_up for k in inc_loose):
        return True

    return False


@dataclass
class IncomeEntry:
    date: Optional[str]
    description: str
    amount: float
    raw_line: str
    page: int


def _ocr_pdf_to_text(path: str, poppler_path: Optional[str] = None, tesseract_cmd: Optional[str] = None) -> List[str]:
    if not _OCR_AVAILABLE:
        raise RuntimeError('OCR dependencies (pdf2image/pytesseract/Pillow) are not installed')

    if tesseract_cmd:
        pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

    images = convert_from_path(path, poppler_path=poppler_path) if poppler_path else convert_from_path(path)
    texts: List[str] = []
    for img in images:
        txt = pytesseract.image_to_string(img, lang='por')
        texts.append(txt)
    return texts


def extract_incomes_from_pdf(path: str, ocr: bool = False, poppler_path: Optional[str] = None, tesseract_cmd: Optional[str] = None) -> List[IncomeEntry]:
    incomes: List[IncomeEntry] = []

    with pdfplumber.open(path) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            text = page.extract_text()

            if not text and ocr:
                try:
                    ocr_texts = _ocr_pdf_to_text(path, poppler_path=poppler_path, tesseract_cmd=tesseract_cmd)
                except Exception as exc:
                    raise RuntimeError(f'OCR failed: {exc}')

                if i - 1 < len(ocr_texts):
                    text = ocr_texts[i - 1]

            if not text:
                continue

            lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
            for ln in lines:
                amounts = AMOUNT_RE.findall(ln)
                if not amounts:
                    continue

                if not is_incoming(ln):
                    continue

                if len(amounts) >= 2:
                    amt_str = amounts[-2]
                else:
                    amt_str = amounts[0]
                try:
                    amt = br_to_float(amt_str)
                except ValueError:
                    continue

                date_match = DATE_RE.search(ln)
                date = date_match.group(1) if date_match else None

                cleaned = ln
                cleaned = AMOUNT_RE.sub('', cleaned)
                cleaned = re.sub(r"\b\d{5,}\b", '', cleaned)
                cleaned = re.sub(r"N\s*[°º]\s*DOCUMENTO", '', cleaned, flags=re.IGNORECASE)
                cleaned = re.sub(r"\s+", ' ', cleaned).strip(' -–—:;,.')

                incomes.append(IncomeEntry(date=date, description=cleaned, amount=amt, raw_line=cleaned, page=i))

    return incomes


def save_csv(entries: List[IncomeEntry], outpath: str) -> None:
    with open(outpath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['date', 'description', 'amount', 'raw_line', 'page'])
        for e in entries:
            writer.writerow([e.date or '', e.description, f"{e.amount:.2f}", e.raw_line, e.page])


def save_json(entries: List[IncomeEntry], outpath: str) -> None:
    with open(outpath, 'w', encoding='utf-8') as f:
        json.dump([asdict(e) for e in entries], f, ensure_ascii=False, indent=2)


def main():
    parser = argparse.ArgumentParser(description='Extrai entradas (PIX/DEP/CRÉDITO) de um PDF de extrato')
    parser.add_argument('pdf', help='Caminho para o arquivo PDF do extrato')
    parser.add_argument('--out', '-o', help='Arquivo de saída (csv ou json). Se omitido, imprime no stdout')
    parser.add_argument('--format', '-f', choices=['csv', 'json'], default='csv')
    parser.add_argument('--ocr', action='store_true', help='Ativa fallback por OCR quando o PDF for escaneado (requer tesseract+poppler)')
    parser.add_argument('--poppler-path', help='Caminho para binários do poppler (somente Windows). Ex: C:/poppler/bin')
    parser.add_argument('--tesseract-cmd', help='Caminho para executável do tesseract (ex: C:/Program Files/Tesseract-OCR/tesseract.exe)')
    parser.add_argument('--amounts-only', action='store_true', help='Imprime/salva somente os valores (um por linha) para copiar/colar no Excel')
    parser.add_argument('--decimal-comma', '--br', action='store_true', dest='decimal_comma', help='Usa vírgula como separador decimal (ex: 768,00)')
    args = parser.parse_args()

    try:
        entries = extract_incomes_from_pdf(args.pdf, ocr=args.ocr, poppler_path=args.poppler_path, tesseract_cmd=args.tesseract_cmd)
    except RuntimeError as e:
        print(f'Erro durante extração: {e}')
        return

    if not entries:
        print('Nenhuma entrada encontrada com as heurísticas aplicadas. Tente revisar o arquivo ou usar OCR se o PDF for escaneado.')
        return

    if args.amounts_only:
        amounts = [f"{e.amount:.2f}" for e in entries]
        if getattr(args, 'decimal_comma', False):
            amounts = [a.replace('.', ',') for a in amounts]
        if args.out:
            with open(args.out, 'w', encoding='utf-8') as f:
                for a in amounts:
                    f.write(a + '\n')
            print(f'Salvo {len(amounts)} valores em {args.out}')
        else:
            for a in amounts:
                print(a)
        return

    if args.out:
        if args.format == 'csv' or args.out.lower().endswith('.csv'):
            save_csv(entries, args.out)
            print(f'Salvo {len(entries)} entradas em {args.out}')
        else:
            save_json(entries, args.out)
            print(f'Salvo {len(entries)} entradas em {args.out}')
    else:
        for e in entries:
            print(f"{e.date or '-'} | R$ {e.amount:.2f} | {e.description}")


if __name__ == '__main__':
    main()
