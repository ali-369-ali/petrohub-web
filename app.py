import os
import json
from flask import Flask, render_template_string, request, jsonify, make_response

app = Flask(__name__)
app.secret_key = "petrohub-secret-key-production"

LANGUAGES = {
    'fa': {'name': 'فارسی', 'dir': 'rtl', 'flag': '🇮🇷'},
    'en': {'name': 'English', 'dir': 'ltr', 'flag': '🇬🇧'},
    'ar': {'name': 'العربية', 'dir': 'rtl', 'flag': '🇦🇪'},
    'ru': {'name': 'Русский', 'dir': 'ltr', 'flag': '🇷🇺'},
    'zh': {'name': '中文', 'dir': 'ltr', 'flag': '🇨🇳'},
    'tr': {'name': 'Türkçe', 'dir': 'ltr', 'flag': '🇹🇷'}
}

PRODUCTS = [
    {
        "id": "bitumen-6070",
        "category": "bitumen",
        "hs_code": "2713.20.00",
        "title": {
            "fa": "قیر نفوذی صادراتی ۶۰/۷۰",
            "en": "Penetration Grade Bitumen 60/70",
            "ar": "البيتوامين درجة الاختراق 60/70",
            "ru": "Битум нефтяной дорожный 60/70",
            "zh": "渗透级沥青 60/70",
            "tr": "Penetrasyon Asfalt 60/70"
        },
        "specs": {
            "Penetration": "60 - 70 dmm",
            "Softening Point": "49 - 56 °C",
            "Specific Gravity": "1.01 - 1.06 g/cm³",
            "Ductility": "> 100 cm",
            "Purity": "> 99.5%"
        },
        "moq": "500 MT",
        "packaging": "New Steel Drums (180kg / 240kg), Jumbo Bags (1000kg), Bulk Flexitank",
        "incoterms": "FOB Bandar Abbas, CFR Jebel Ali, CIF Global Ports"
    },
    {
        "id": "bitumen-80100",
        "category": "bitumen",
        "hs_code": "2713.20.00",
        "title": {
            "fa": "قیر نفوذی صادراتی ۸۰/۱۰۰",
            "en": "Penetration Grade Bitumen 80/100",
            "ar": "البيتوامين درجة الاختراق 80/100",
            "ru": "Битум нефтяной дорожный 80/100",
            "zh": "渗透级沥青 80/100",
            "tr": "Penetrasyon Asfalt 80/100"
        },
        "specs": {
            "Penetration": "80 - 100 dmm",
            "Softening Point": "45 - 52 °C",
            "Specific Gravity": "1.01 - 1.05 g/cm³",
            "Ductility": "> 100 cm",
            "Purity": "> 99.5%"
        },
        "moq": "500 MT",
        "packaging": "New Steel Drums, Jumbo Bags, Bulk Flexitank",
        "incoterms": "FOB Bandar Abbas, CFR, CIF"
    },
    {
        "id": "base-oil-sn150",
        "category": "base_oil",
        "hs_code": "2710.19.91",
        "title": {
            "fa": "روغن پایه Virgin SN150",
            "en": "Virgin Base Oil SN150",
            "ar": "زيت الأساس SN150 البكر",
            "ru": "Базовое масло Virgin SN150",
            "zh": "原生产线基础油 SN150",
            "tr": "Bakir Baz Yağı SN150"
        },
        "specs": {
            "Kinematic Viscosity @ 40°C": "28 - 32 cSt",
            "Viscosity Index": "Min 95",
            "Flash Point (COC)": "Min 200 °C",
            "Pour Point": "Max -6 °C",
            "Color": "Max 1.0"
        },
        "moq": "200 MT",
        "packaging": "Flexibags, Steel Drums (208L), IBC Tanks, Bulk Tankers",
        "incoterms": "FOB Bandar Abbas, CFR Jebel Ali"
    },
    {
        "id": "base-oil-sn500",
        "category": "base_oil",
        "hs_code": "2710.19.91",
        "title": {
            "fa": "روغن پایه Virgin SN500",
            "en": "Virgin Base Oil SN500",
            "ar": "زيت الأساس SN500 البكر",
            "ru": "Базовое масло Virgin SN500",
            "zh": "原生产线基础油 SN500",
            "tr": "Bakir Baz Yağı SN500"
        },
        "specs": {
            "Kinematic Viscosity @ 100°C": "10.5 - 11.5 cSt",
            "Viscosity Index": "Min 95",
            "Flash Point (COC)": "Min 230 °C",
            "Pour Point": "Max -3 °C",
            "Color": "Max 1.5"
        },
        "moq": "200 MT",
        "packaging": "Flexibags, Steel Drums (208L), Bulk",
        "incoterms": "FOB, CFR, CIF"
    },
    {
        "id": "paraffin-wax",
        "category": "wax",
        "hs_code": "2712.20.00",
        "title": {
            "fa": "پارافین وکس نیمه تصفیه شده (3-5% روغن)",
            "en": "Semi-Refined Paraffin Wax (3-5% Oil)",
            "ar": "شمع البرافين شبه المكرر",
            "ru": "Парафин нефтяной полуочищенный",
            "zh": "半精炼石蜡 (含油量 3-5%)",
            "tr": "Yarı Rafine Parafin Vaks"
        },
        "specs": {
            "Melting Point": "60 - 62 °C",
            "Oil Content": "3.0 - 5.0 %",
            "Color": "White",
            "Odor": "None"
        },
        "moq": "100 MT",
        "packaging": "5-Ply Cartons (25kg), Bags",
        "incoterms": "FOB, CFR, CIF"
    },
    {
        "id": "hdpe-pipe",
        "category": "polymers",
        "hs_code": "3901.20.00",
        "title": {
            "fa": "پلی‌اتیلن سنگین گرید لوله (HDPE PE100)",
            "en": "HDPE PE100 Pipe Grade Resin",
            "ar": "البولي إيثيلين عالي الكثافة PE100",
            "ru": "Полиэтилен высокой плотности PE100",
            "zh": "高密度聚乙烯 PE100 管材级",
            "tr": "HDPE PE100 Boru Tipi Polietilen"
        },
        "specs": {
            "Density": "0.958 - 0.960 g/cm³",
            "MFR (190°C/5kg)": "0.22 - 0.28 g/10min",
            "Carbon Black Content": "2.0 - 2.5 %"
        },
        "moq": "100 MT",
        "packaging": "25kg PP Bags, Palletized",
        "incoterms": "FOB, CFR, CIF"
    }
]

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="{{ lang }}" dir="{{ lang_dir }}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PetroHub Global | International Trade of Petroleum & Bitumen Derivatives</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&family=Montserrat:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-dark: #0B0F19;
            --card-dark: #151C2C;
            --accent-gold: #D4AF37;
            --accent-gold-light: #F3E5AB;
            --text-light: #E2E8F0;
            --text-muted: #94A3B8;
            --border-gold: rgba(212, 175, 55, 0.3);
        }
        body {
            background-color: var(--bg-dark);
            color: var(--text-light);
            font-family: {% if lang_dir == 'rtl' %}'Tajawal', sans-serif{% else %}'Montserrat', sans-serif{% endif %};
        }
        .gold-text { color: var(--accent-gold); }
        .bg-card { background-color: var(--card-dark); border: 1px solid var(--border-gold); }
        .navbar { background: rgba(11, 15, 25, 0.95); border-bottom: 1px solid var(--border-gold); backdrop-filter: blur(10px); }
        .hero-section {
            background: linear-gradient(180deg, rgba(11,15,25,0.7) 0%, rgba(11,15,25,1) 100%), url('https://images.unsplash.com/photo-1518709268805-4e9042af9f23?auto=format&fit=crop&w=1600&q=80');
            background-size: cover; background-position: center; padding: 100px 0 60px 0;
        }
        .product-card {
            background: var(--card-dark);
            border: 1px solid var(--border-gold);
            border-radius: 12px;
            transition: all 0.3s ease;
        }
        .product-card:hover { transform: translateY(-5px); box-shadow: 0 10px 30px rgba(212, 175, 55, 0.15); }
        .btn-gold {
            background: linear-gradient(135deg, #D4AF37 0%, #AA7C11 100%);
            color: #000; font-weight: 700; border: none; padding: 10px 24px; border-radius: 6px;
        }
        .btn-gold:hover { background: linear-gradient(135deg, #F3E5AB 0%, #D4AF37 100%); color: #000; }
        .whatsapp-btn {
            position: fixed; bottom: 25px; right: 25px; background: #25D366; color: white;
            border-radius: 50px; padding: 14px 22px; font-weight: bold; font-size: 16px;
            box-shadow: 0 4px 15px rgba(37,211,102,0.4); z-index: 1000; text-decoration: none; display: flex; align-items: center; gap: 8px;
        }
        .whatsapp-btn:hover { background: #1EBE57; color: white; }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg sticky-top">
        <div class="container">
            <a class="navbar-brand gold-text fw-bold fs-3" href="/"><i class="fa-solid fa-oil-well me-2"></i>PetroHub Global</a>
            <div class="d-flex align-items-center gap-2">
                <div class="dropdown">
                    <button class="btn btn-outline-warning dropdown-toggle btn-sm" type="button" data-bs-toggle="dropdown">
                        {{ current_lang.flag }} {{ current_lang.name }}
                    </button>
                    <ul class="dropdown-menu dropdown-menu-dark">
                        {% for code, info in languages.items() %}
                        <li><a class="dropdown-item" href="/set_language/{{ code }}">{{ info.flag }} {{ info.name }}</a></li>
                        {% endfor %}
                    </ul>
                </div>
            </div>
        </div>
    </nav>

    <div class="hero-section text-center">
        <div class="container">
            <h1 class="display-4 fw-bold gold-text mb-3">PETROHUB GLOBAL</h1>
            <p class="lead text-light mb-4">Direct Supply & Export of Bitumen, Base Oils, Wax & Petrochemicals</p>
            <div class="d-flex justify-content-center gap-3">
                <a href="#rfq" class="btn btn-gold"><i class="fa-solid fa-paper-plane me-2"></i>Request Quotation (RFQ)</a>
                <a href="https://wa.me/989120000000?text=Hello%20PetroHub%20Global" target="_blank" class="btn btn-outline-warning"><i class="fa-brands fa-whatsapp me-2"></i>WhatsApp Direct</a>
            </div>
        </div>
    </div>

    <div class="container my-5" id="products">
        <h2 class="gold-text border-bottom border-warning pb-2 mb-4"><i class="fa-solid fa-boxes-stacked me-2"></i>Export Products Specification</h2>
        <div class="row g-4">
            {% for p in products %}
            <div class="col-md-6 col-lg-4">
                <div class="product-card p-4 h-100 d-flex flex-column justify-content-between">
                    <div>
                        <span class="badge bg-warning text-dark mb-2">HS: {{ p.hs_code }}</span>
                        <h4 class="gold-text fs-5">{{ p.title[lang] or p.title['en'] }}</h4>
                        <table class="table table-dark table-sm text-start mt-3 opacity-75" style="font-size: 0.85rem;">
                            {% for spec_key, spec_val in p.specs.items() %}
                            <tr>
                                <td>{{ spec_key }}</td>
                                <th class="text-warning text-end">{{ spec_val }}</th>
                            </tr>
                            {% endfor %}
                        </table>
                    </div>
                    <div class="mt-3 pt-3 border-top border-secondary">
                        <small class="d-block text-muted">MOQ: <strong class="text-light">{{ p.moq }}</strong></small>
                        <small class="d-block text-muted mb-3">Terms: <strong class="text-light">{{ p.incoterms }}</strong></small>
                        <a href="https://wa.me/989120000000?text=Inquiry%20for%20{{ p.title['en'] }}" target="_blank" class="btn btn-outline-warning btn-sm w-100"><i class="fa-brands fa-whatsapp me-1"></i>Inquire Product</a>
                    </div>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>

    <div class="container my-5 p-4 bg-card rounded-3" id="rfq">
        <h3 class="gold-text mb-3"><i class="fa-solid fa-file-signature me-2"></i>Official Request for Quotation (RFQ)</h3>
        <p class="text-muted">Fill in your exact inquiry details to receive an official FCO / Soft Offer within 24 hours.</p>
        <form action="/submit_rfq" method="POST" class="row g-3">
            <div class="col-md-6">
                <label class="form-label text-light">Company Name</label>
                <input type="text" name="company" class="form-control bg-dark text-light border-secondary" required>
            </div>
            <div class="col-md-6">
                <label class="form-label text-light">Official Email / Phone</label>
                <input type="text" name="contact" class="form-control bg-dark text-light border-secondary" required>
            </div>
            <div class="col-md-6">
                <label class="form-label text-light">Product Required</label>
                <select name="product" class="form-select bg-dark text-light border-secondary">
                    {% for p in products %}
                    <option value="{{ p.id }}">{{ p.title['en'] }}</option>
                    {% endfor %}
                </select>
            </div>
            <div class="col-md-6">
                <label class="form-label text-light">Quantity & Incoterm (e.g. 1000 MT CIF Jebel Ali)</label>
                <input type="text" name="details" class="form-control bg-dark text-light border-secondary" required>
            </div>
            <div class="col-12">
                <button type="submit" class="btn btn-gold w-100 py-2 fs-6"><i class="fa-solid fa-paper-plane me-2"></i>Send Formal RFQ</button>
            </div>
        </form>
    </div>

    <footer class="text-center py-4 border-top border-secondary mt-5 text-muted">
        <div class="container">
            <p class="mb-1">© 2026 PetroHub Global (petrohubtrade.com). All Rights Reserved.</p>
            <small>Petroleum & Bitumen Derivatives Export Desk</small>
        </div>
    </footer>

    <a href="https://wa.me/989120000000?text=Hello%20PetroHub%20Team" target="_blank" class="whatsapp-btn">
        <i class="fa-brands fa-whatsapp fs-4"></i> WhatsApp Support
    </a>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

@app.route('/')
def index():
    lang = request.cookies.get('user_lang', 'en')
    if lang not in LANGUAGES:
        lang = 'en'
    return render_template_string(
        HTML_TEMPLATE,
        lang=lang,
        lang_dir=LANGUAGES[lang]['dir'],
        current_lang=LANGUAGES[lang],
        languages=LANGUAGES,
        products=PRODUCTS
    )

@app.route('/set_language/<lang_code>')
def set_language(lang_code):
    if lang_code not in LANGUAGES:
        lang_code = 'en'
    resp = make_response(jsonify({'status': 'success', 'lang': lang_code}))
    resp.set_cookie('user_lang', lang_code, max_age=30*24*60*60)
    return resp

@app.route('/submit_rfq', methods=['POST'])
def submit_rfq():
    return jsonify({
        "status": "success",
        "message": "RFQ received successfully. Our trade department will contact you within 24 hours."
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
