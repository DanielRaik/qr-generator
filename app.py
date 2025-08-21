from flask import Flask, render_template, request, redirect, url_for, flash
import qrcode
import os
import uuid
import re
from urllib.parse import urlparse

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'sua_chave_secreta_aqui_mudeme')

def is_valid_url(url):
    """Valida se a URL é válida"""
    try:
        # Adiciona http:// se não tiver protocolo
        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url
        
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def normalize_url(url):
    """Normaliza a URL adicionando protocolo se necessário"""
    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url
    return url

@app.route("/", methods=["GET", "POST"])
def index():
    qr_url = None
    
    if request.method == "POST":
        url = request.form.get("url", "").strip()
        color = request.form.get("color") or "black"
        bg_color = request.form.get("bg_color") or "white"
        size = int(request.form.get("size") or 10)

        if not url:
            flash("Por favor, insira uma URL.", "error")
        elif not is_valid_url(url):
            flash("URL inválida. Verifique o formato da URL.", "error")
        else:
            try:
                # Normaliza a URL
                normalized_url = normalize_url(url)
                
                # Gera nome único para o arquivo
                filename = f"qr_{uuid.uuid4().hex[:8]}.png"
                qr_path = os.path.join("static", filename)
                
                # Limpa QR codes antigos (opcional - limite para evitar muito uso de espaço)
                static_files = [f for f in os.listdir("static") if f.startswith("qr_") and f.endswith(".png")]
                if len(static_files) > 10:  # Mantém apenas os 10 mais recentes
                    for old_file in static_files[:-10]:
                        try:
                            os.remove(os.path.join("static", old_file))
                        except:
                            pass

                # Gera o QR code
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_H,
                    box_size=size,
                    border=4,
                )
                qr.add_data(normalized_url)
                qr.make(fit=True)

                img = qr.make_image(fill_color=color, back_color=bg_color)
                img.save(qr_path)
                
                qr_url = url_for('static', filename=filename)
                flash("QR Code gerado com sucesso!", "success")
                
            except Exception as e:
                flash(f"Erro ao gerar QR Code: {str(e)}", "error")

    return render_template("index.html", qr_url=qr_url)

if __name__ == "__main__":
    # Cria pasta static se não existir
    if not os.path.exists("static"):
        os.makedirs("static")
    
    # Para desenvolvimento local
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)