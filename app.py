from flask import Flask, request, send_file, jsonify
import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer
from qrcode.image.styles.colormasks import RadialGradiantColorMask
from PIL import Image
import io
import os

app = Flask(__name__)

@app.route("/generate_sheet", methods=["POST"])
def generate_sheet():
    try:
        data_list = request.get_json().get("data", [])
        cols, rows = 5, 10
        qr_size = 200
        page_width = cols * qr_size
        page_height = rows * qr_size
        sheet = Image.new("RGB", (page_width, page_height), "white")

        logo = Image.open("doll.png")
        logo_size = 100
        logo.thumbnail((logo_size, logo_size))

        for idx, item in enumerate(data_list[:50]):
            code = item.get("X1", "AVX")
            qr_url = f"https://qr-ref-api-main.onrender.com/view/{code}"

            qr = qrcode.QRCode(
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=10,
                border=4,
            )
            qr.add_data(qr_url)
            qr.make(fit=True)

            img_qr = qr.make_image(
                image_factory=StyledPilImage,
                module_drawer=RoundedModuleDrawer(),
                color_mask=RadialGradiantColorMask(
                    center_color=(0, 102, 255),
                    edge_color=(255, 0, 255)
                )
            ).convert("RGB")

            qr_width, qr_height = img_qr.size
            pos = ((qr_width - logo_size) // 2, (qr_height - logo_size) // 2)
            img_qr.paste(logo, pos, mask=logo if logo.mode == 'RGBA' else None)

            img_qr = img_qr.resize((qr_size, qr_size))
            x = (idx % cols) * qr_size
            y = (idx // cols) * qr_size
            sheet.paste(img_qr, (x, y))

        output = io.BytesIO()
        sheet.save(output, format="PNG")
        output.seek(0)
        return send_file(output, mimetype="image/png")

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
