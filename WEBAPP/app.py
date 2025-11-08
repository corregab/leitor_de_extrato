from __future__ import annotations

import os
import uuid
from decimal import Decimal, ROUND_DOWN
from typing import List, Dict, Any

from flask import Flask, render_template, request, redirect, url_for, flash

# Garante que o diretório do repositório (pai de WEBAPP) esteja no sys.path para permitir imports
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(BASE_DIR)
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

# Importa os extratores existentes sem alterar nada neles
try:
    from ITAU.itau_extractor import ItauExtractParser
except Exception:
    ItauExtractParser = None  # type: ignore

try:
    from SANTANDER.income_extractor import extract_incomes_from_pdf as santander_extract
except Exception:
    santander_extract = None  # type: ignore

try:
    from NUBANK.nubank_extractor import NubankExtractor
except Exception:
    NubankExtractor = None  # type: ignore

try:
    from PICPAY.picpay_extractor import PicPayExtractor
except Exception:
    PicPayExtractor = None  # type: ignore

try:
    from MERCADOPAGO.mercadopago_extractor import MercadoPagoExtractor
except Exception:
    MercadoPagoExtractor = None  # type: ignore


UPLOAD_DIR = os.path.join(BASE_DIR, 'uploads')
ALLOWED_EXTENSIONS = {'.pdf'}

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'dev-secret-change-in-production')
app.config['UPLOAD_FOLDER'] = UPLOAD_DIR
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limite de 16MB para uploads


def allowed_file(filename: str) -> bool:
    _, ext = os.path.splitext(filename.lower())
    return ext in ALLOWED_EXTENSIONS


def should_exclude_transaction(description: str, exclude_names: List[str]) -> bool:
    """Verifica se a transação deve ser excluída baseado nos nomes fornecidos."""
    if not exclude_names:
        return False
    
    description_lower = description.lower()
    for name in exclude_names:
        if name in description_lower:
            return True
    return False


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/process', methods=['POST'])
def process():
    bank = request.form.get('bank')
    file = request.files.get('statement')
    exclude_names_input = request.form.get('exclude_names', '').strip()

    # Processa os nomes para excluir
    exclude_names = []
    if exclude_names_input:
        exclude_names = [name.strip().lower() for name in exclude_names_input.split(',') if name.strip()]

    if not bank:
        flash('Selecione o banco.')
        return redirect(url_for('index'))

    if not file or file.filename == '':
        flash('Selecione um arquivo PDF para enviar.')
        return redirect(url_for('index'))

    if not allowed_file(file.filename):
        flash('Formato inválido. Envie um arquivo .pdf')
        return redirect(url_for('index'))

    # Salva upload com nome único
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    unique_name = f"{uuid.uuid4().hex}.pdf"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_name)
    file.save(filepath)

    try:
        if bank in ('itau', 'itau_new'):
            if ItauExtractParser is None:
                raise RuntimeError('Módulo ITAU.itau_extractor não disponível')
            parser = ItauExtractParser()
            credits = parser.extract_credits(filepath)

            rows: List[Dict[str, Any]] = []
            total = Decimal('0')
            excluded_count = 0
            for e in credits:
                # Verifica se deve excluir esta transação
                if should_exclude_transaction(e.description, exclude_names):
                    excluded_count += 1
                    continue
                    
                amt = e.amount.quantize(Decimal('.01'), rounding=ROUND_DOWN)
                total += amt
                rows.append({
                    'date': e.date,
                    'type': e.transaction_type,
                    'description': e.description,
                    'amount': f"R$ {str(amt).replace('.', ',')}",
                    # Coluna auxiliar para copiar facilmente apenas o número
                    'amount_plain': str(amt).replace('.', ',')
                })
            total_str = f"R$ {str(total.quantize(Decimal('.01'))).replace('.', ',')}"
            
            # Mensagem informando quantas transações foram excluídas
            if excluded_count > 0:
                flash(f'{excluded_count} transação(ões) excluída(s) pelos nomes informados.', 'info')
            
            return render_template('results.html', bank_label='Itaú', rows=rows, total=total_str)

        elif bank == 'santander':
            if santander_extract is None:
                raise RuntimeError('Módulo SANTANDER.income_extractor não disponível')
            incomes = santander_extract(filepath)

            rows: List[Dict[str, Any]] = []
            total = 0.0
            excluded_count = 0
            for e in incomes:
                # Verifica se deve excluir esta transação
                if should_exclude_transaction(e.description, exclude_names):
                    excluded_count += 1
                    continue
                    
                total += float(e.amount)
                amount_str = f"R$ {float(e.amount):.2f}".replace('.', ',')
                rows.append({
                    'date': e.date or '-',
                    'type': 'CRÉDITO',
                    'description': e.description,
                    'amount': amount_str,
                    'amount_plain': f"{float(e.amount):.2f}".replace('.', ',')
                })
            total_str = f"R$ {total:.2f}".replace('.', ',')
            
            if excluded_count > 0:
                flash(f'{excluded_count} transação(ões) excluída(s) pelos nomes informados.', 'info')
            
            return render_template('results.html', bank_label='Santander', rows=rows, total=total_str)

        elif bank == 'nubank':
            if NubankExtractor is None:
                raise RuntimeError('Módulo NUBANK.nubank_extractor não disponível')
            extractor = NubankExtractor()
            credits = extractor.extract_credits(filepath)

            rows: List[Dict[str, Any]] = []
            total = Decimal('0')
            excluded_count = 0
            for e in credits:
                # Verifica se deve excluir esta transação
                if should_exclude_transaction(e.description, exclude_names):
                    excluded_count += 1
                    continue
                    
                amt = e.amount.quantize(Decimal('.01'), rounding=ROUND_DOWN)
                total += amt
                rows.append({
                    'date': e.date,
                    'type': e.transaction_type,
                    'description': e.description,
                    'amount': f"R$ {str(amt).replace('.', ',')}",
                    'amount_plain': str(amt).replace('.', ',')
                })
            total_str = f"R$ {str(total.quantize(Decimal('.01'))).replace('.', ',')}"
            
            if excluded_count > 0:
                flash(f'{excluded_count} transação(ões) excluída(s) pelos nomes informados.', 'info')
            
            return render_template('results.html', bank_label='Nubank', rows=rows, total=total_str)

        elif bank == 'picpay':
            if PicPayExtractor is None:
                raise RuntimeError('Módulo PICPAY.picpay_extractor não disponível')
            extractor = PicPayExtractor()
            credits = extractor.extract_credits(filepath)

            rows: List[Dict[str, Any]] = []
            total = Decimal('0')
            excluded_count = 0
            for e in credits:
                # Verifica se deve excluir esta transação
                if should_exclude_transaction(e.description, exclude_names):
                    excluded_count += 1
                    continue
                    
                amt = e.amount.quantize(Decimal('.01'), rounding=ROUND_DOWN)
                total += amt
                rows.append({
                    'date': e.date,
                    'type': e.transaction_type,
                    'description': e.description,
                    'amount': f"R$ {str(amt).replace('.', ',')}",
                    'amount_plain': str(amt).replace('.', ',')
                })
            total_str = f"R$ {str(total.quantize(Decimal('.01'))).replace('.', ',')}"
            
            if excluded_count > 0:
                flash(f'{excluded_count} transação(ões) excluída(s) pelos nomes informados.', 'info')
            
            return render_template('results.html', bank_label='PicPay', rows=rows, total=total_str)

        elif bank == 'mercadopago':
            if MercadoPagoExtractor is None:
                raise RuntimeError('Módulo MERCADOPAGO.mercadopago_extractor não disponível')
            extractor = MercadoPagoExtractor()
            credits = extractor.extract_credits(filepath)

            rows: List[Dict[str, Any]] = []
            total = Decimal('0')
            excluded_count = 0
            for e in credits:
                # Verifica se deve excluir esta transação
                if should_exclude_transaction(e.description, exclude_names):
                    excluded_count += 1
                    continue
                    
                amt = e.amount.quantize(Decimal('.01'), rounding=ROUND_DOWN)
                total += amt
                rows.append({
                    'date': e.date,
                    'type': e.transaction_type,
                    'description': e.description,
                    'amount': f"R$ {str(amt).replace('.', ',')}",
                    'amount_plain': str(amt).replace('.', ',')
                })
            total_str = f"R$ {str(total.quantize(Decimal('.01'))).replace('.', ',')}"
            
            if excluded_count > 0:
                flash(f'{excluded_count} transação(ões) excluída(s) pelos nomes informados.', 'info')
            
            return render_template('results.html', bank_label='Mercado Pago', rows=rows, total=total_str)

        else:
            flash('Banco não suportado (use Itaú, Santander, Nubank, PicPay ou Mercado Pago).')
            return redirect(url_for('index'))

    except Exception as exc:
        flash(f'Erro ao processar: {exc}')
        return redirect(url_for('index'))


if __name__ == '__main__':
    # Execução local simples
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') != 'production'
    app.run(host='0.0.0.0', port=port, debug=debug)

