from __future__ import annotations

import os
import uuid
from decimal import Decimal, ROUND_DOWN
from typing import List, Dict, Any

from flask import Flask, render_template, request, redirect, url_for, flash, abort

import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(BASE_DIR)
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

try:
    from ITAU.itau_extractor import ItauExtractParser
except Exception:
    ItauExtractParser = None

try:
    from SANTANDER.income_extractor import extract_incomes_from_pdf as santander_extract
except Exception:
    santander_extract = None

try:
    from NUBANK.nubank_extractor import NubankExtractor
except Exception:
    NubankExtractor = None

try:
    from PICPAY.picpay_extractor import PicPayExtractor
except Exception:
    PicPayExtractor = None

try:
    from MERCADOPAGO.mercadopago_extractor import MercadoPagoExtractor
except Exception:
    MercadoPagoExtractor = None


UPLOAD_DIR = os.path.join(BASE_DIR, 'uploads')
ALLOWED_EXTENSIONS = {'.pdf'}
MAX_FILES = 10  # Maximum number of files that can be uploaded at once

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'dev-secret-change-in-production')
app.config['UPLOAD_FOLDER'] = UPLOAD_DIR
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024


# Security headers
@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response


# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('index.html'), 404


@app.errorhandler(413)
def request_entity_too_large(error):
    flash('Arquivo muito grande. O tamanho máximo permitido é 16 MB.')
    return redirect(url_for('index'))


@app.errorhandler(500)
def internal_error(error):
    flash('Ocorreu um erro interno. Por favor, tente novamente.')
    return redirect(url_for('index'))


def allowed_file(filename: str) -> bool:
    """Validate if the file has an allowed extension and safe filename"""
    if not filename:
        return False
    
    # Check for path traversal attempts
    if '..' in filename or '/' in filename or '\\' in filename:
        return False
    
    _, ext = os.path.splitext(filename.lower())
    return ext in ALLOWED_EXTENSIONS


def should_exclude_transaction(description: str, exclude_names: List[str]) -> bool:
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
    files = request.files.getlist('statement')
    exclude_names_input = request.form.get('exclude_names', '').strip()

    exclude_names = []
    if exclude_names_input:
        exclude_names = [name.strip().lower() for name in exclude_names_input.split(',') if name.strip()]

    if not bank:
        flash('Selecione o banco.')
        return redirect(url_for('index'))

    if not files or all(f.filename == '' for f in files):
        flash('Selecione pelo menos um arquivo PDF para enviar.')
        return redirect(url_for('index'))
    
    # Check number of files
    valid_files = [f for f in files if f.filename]
    if len(valid_files) > MAX_FILES:
        flash(f'Você pode enviar no máximo {MAX_FILES} arquivos por vez.')
        return redirect(url_for('index'))

    for f in files:
        if f.filename and not allowed_file(f.filename):
            flash(f'Formato inválido: {f.filename}. Envie apenas arquivos .pdf')
            return redirect(url_for('index'))

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    filepaths = []
    for f in files:
        if f.filename:
            unique_name = f"{uuid.uuid4().hex}.pdf"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_name)
            f.save(filepath)
            filepaths.append(filepath)

    try:
        all_rows: List[Dict[str, Any]] = []
        total = Decimal('0') if bank != 'santander' else 0.0
        excluded_count = 0
        
        for filepath in filepaths:
            if bank in ('itau', 'itau_new'):
                if ItauExtractParser is None:
                    raise RuntimeError('Módulo ITAU.itau_extractor não disponível')
                parser = ItauExtractParser()
                credits = parser.extract_credits(filepath)

                for e in credits:
                    if should_exclude_transaction(e.description, exclude_names):
                        excluded_count += 1
                        continue
                        
                    amt = e.amount.quantize(Decimal('.01'), rounding=ROUND_DOWN)
                    total += amt
                    all_rows.append({
                        'date': e.date,
                        'type': e.transaction_type,
                        'description': e.description,
                        'amount': f"R$ {str(amt).replace('.', ',')}",
                        'amount_plain': str(amt).replace('.', ',')
                    })

            elif bank == 'santander':
                if santander_extract is None:
                    raise RuntimeError('Módulo SANTANDER.income_extractor não disponível')
                incomes = santander_extract(filepath)

                for e in incomes:
                    if should_exclude_transaction(e.description, exclude_names):
                        excluded_count += 1
                        continue
                        
                    total += float(e.amount)
                    amount_str = f"R$ {float(e.amount):.2f}".replace('.', ',')
                    all_rows.append({
                        'date': e.date or '-',
                        'type': 'CRÉDITO',
                        'description': e.description,
                        'amount': amount_str,
                        'amount_plain': f"{float(e.amount):.2f}".replace('.', ',')
                    })

            elif bank == 'nubank':
                if NubankExtractor is None:
                    raise RuntimeError('Módulo NUBANK.nubank_extractor não disponível')
                extractor = NubankExtractor()
                credits = extractor.extract_credits(filepath)

                for e in credits:
                    if should_exclude_transaction(e.description, exclude_names):
                        excluded_count += 1
                        continue
                        
                    amt = e.amount.quantize(Decimal('.01'), rounding=ROUND_DOWN)
                    total += amt
                    all_rows.append({
                        'date': e.date,
                        'type': e.transaction_type,
                        'description': e.description,
                        'amount': f"R$ {str(amt).replace('.', ',')}",
                        'amount_plain': str(amt).replace('.', ',')
                    })

            elif bank == 'picpay':
                if PicPayExtractor is None:
                    raise RuntimeError('Módulo PICPAY.picpay_extractor não disponível')
                extractor = PicPayExtractor()
                credits = extractor.extract_credits(filepath)

                for e in credits:
                    if should_exclude_transaction(e.description, exclude_names):
                        excluded_count += 1
                        continue
                        
                    amt = e.amount.quantize(Decimal('.01'), rounding=ROUND_DOWN)
                    total += amt
                    all_rows.append({
                        'date': e.date,
                        'type': e.transaction_type,
                        'description': e.description,
                        'amount': f"R$ {str(amt).replace('.', ',')}",
                        'amount_plain': str(amt).replace('.', ',')
                    })

            elif bank == 'mercadopago':
                if MercadoPagoExtractor is None:
                    raise RuntimeError('Módulo MERCADOPAGO.mercadopago_extractor não disponível')
                extractor = MercadoPagoExtractor()
                credits = extractor.extract_credits(filepath)

                for e in credits:
                    if should_exclude_transaction(e.description, exclude_names):
                        excluded_count += 1
                        continue
                        
                    amt = e.amount.quantize(Decimal('.01'), rounding=ROUND_DOWN)
                    total += amt
                    all_rows.append({
                        'date': e.date,
                        'type': e.transaction_type,
                        'description': e.description,
                        'amount': f"R$ {str(amt).replace('.', ',')}",
                        'amount_plain': str(amt).replace('.', ',')
                    })
            else:
                raise ValueError(f'Banco "{bank}" não suportado.')
        
        if bank == 'santander':
            total_str = f"R$ {total:.2f}".replace('.', ',')
        else:
            total_str = f"R$ {str(total.quantize(Decimal('.01'))).replace('.', ',')}"
        
        if excluded_count > 0:
            flash(f'{excluded_count} transação(ões) excluída(s) pelos nomes informados.', 'info')
        
        bank_labels = {
            'itau': 'Itaú',
            'itau_new': 'Itaú',
            'santander': 'Santander',
            'nubank': 'Nubank',
            'picpay': 'PicPay',
            'mercadopago': 'Mercado Pago'
        }
        bank_label = bank_labels.get(bank, bank.capitalize())
        
        return render_template('results.html', bank_label=bank_label, rows=all_rows, total=total_str)

    except Exception as exc:
        import traceback
        error_msg = str(exc)
        if app.debug:
            # In debug mode, show more details
            flash(f'Erro ao processar: {error_msg}')
            app.logger.error(f'Processing error: {traceback.format_exc()}')
        else:
            # In production, show user-friendly message
            flash('Erro ao processar o extrato. Verifique se o arquivo está correto e tente novamente.')
            app.logger.error(f'Processing error: {error_msg}')
        return redirect(url_for('index'))
    finally:
        for fp in filepaths:
            if os.path.exists(fp):
                try:
                    os.remove(fp)
                except Exception:
                    pass


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') != 'production'
    app.run(host='0.0.0.0', port=port, debug=debug)
