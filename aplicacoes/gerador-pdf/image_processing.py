"""Bounded JPEG/PNG processing. Uploads and derivatives stay in memory."""

import io
import warnings
import zipfile
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageCms, ImageOps, UnidentifiedImageError
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

MAX_FILES = 20
MAX_FILE_BYTES = 10 * 1024 * 1024
MAX_BATCH_BYTES = 50 * 1024 * 1024
MAX_PIXELS = 16_000_000
MAX_BATCH_PIXELS = 32_000_000
MAX_SIDE = 8000
MAX_OUTPUT_BYTES = 60 * 1024 * 1024
MAX_ICC_BYTES = 1024 * 1024
MAX_TILES = 10_000
FORMATS = ("JPEG", "PNG")
EXTENSIONS = {".jpg": "JPEG", ".jpeg": "JPEG", ".png": "PNG"}
SRGB_PROFILE = ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB")).tobytes()


class ImageInputError(ValueError):
    """Public error messages contain no upload names, paths or decoder detail."""


class BoundedBuffer(io.BytesIO):
    def write(self, data):
        if self.tell() + len(data) > MAX_OUTPUT_BYTES:
            raise ImageInputError("A saída excede 60 MiB. Divida o lote em partes menores.")
        return super().write(data)


@dataclass(frozen=True)
class ValidatedUpload:
    data: bytes
    format: str
    width: int
    height: int


def _read_bounded(upload):
    try:
        position = upload.tell()
        upload.seek(0)
        data = upload.read(MAX_FILE_BYTES + 1)
        upload.seek(position)
    except (OSError, ValueError, AttributeError):
        raise ImageInputError("Não foi possível ler a imagem enviada.") from None
    if not data or len(data) > MAX_FILE_BYTES:
        raise ImageInputError("Cada imagem deve ter conteúdo e no máximo 10 MiB.")
    return data


def validate_upload(upload):
    if isinstance(upload, ValidatedUpload):
        return upload
    expected = EXTENSIONS.get(Path(getattr(upload, "name", "")).suffix.lower())
    if expected is None:
        raise ImageInputError("Envie somente arquivos JPEG ou PNG.")
    data = _read_bounded(upload)
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(io.BytesIO(data), formats=FORMATS) as image:
                if image.format != expected:
                    raise ImageInputError("O conteúdo não corresponde à extensão JPEG/PNG do arquivo.")
                width, height = image.size
                if (width < 1 or height < 1 or max(width, height) > MAX_SIDE
                        or width * height > MAX_PIXELS):
                    raise ImageInputError("Cada imagem deve ter até 16 megapixels e 8000 pixels por lado.")
                if getattr(image, "n_frames", 1) != 1:
                    raise ImageInputError("Imagens animadas não são aceitas. Envie uma imagem estática.")
                image.verify()
        return ValidatedUpload(data, expected, width, height)
    except ImageInputError:
        raise
    except (UnidentifiedImageError, OSError, ValueError, SyntaxError,
            Image.DecompressionBombError, Image.DecompressionBombWarning):
        raise ImageInputError("Imagem inválida ou incompleta. Envie um JPEG/PNG válido.") from None


def validate_batch(uploads):
    uploads = list(uploads)
    if not uploads or len(uploads) > MAX_FILES:
        raise ImageInputError("Envie de 1 a 20 imagens por lote, incluindo a capa.")
    validated = []
    byte_count = pixel_count = 0
    for upload in uploads:
        item = validate_upload(upload)
        byte_count += len(item.data)
        pixel_count += item.width * item.height
        if byte_count > MAX_BATCH_BYTES or pixel_count > MAX_BATCH_PIXELS:
            raise ImageInputError("O lote excede 50 MiB ou 32 megapixels. Divida-o em partes menores.")
        validated.append(item)
    return validated


def load_image(upload):
    item = validate_upload(upload)
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(io.BytesIO(item.data), formats=FORMATS) as image:
                image.load()  # Reject truncated pixel data as well as invalid headers.
                oriented = ImageOps.exif_transpose(image)
                alpha = oriented.convert("RGBA").getchannel("A")
                profile = oriented.info.get("icc_profile")
                if profile:
                    if len(profile) > MAX_ICC_BYTES:
                        raise ImageInputError("O perfil de cor da imagem é maior que o limite permitido.")
                    source = ImageCms.ImageCmsProfile(io.BytesIO(profile))
                    color_input = oriented if oriented.mode == "CMYK" else oriented.convert("RGB")
                    rgb = ImageCms.profileToProfile(color_input, source,
                                                   ImageCms.createProfile("sRGB"), outputMode="RGB")
                else:
                    rgb = oriented.convert("RGB")
                clean = Image.new("RGBA", rgb.size)
                clean.paste(rgb)
                clean.putalpha(alpha)
                # Fresh pixel image, standardized color profile: no EXIF/XMP/comments.
                clean.info["icc_profile"] = SRGB_PROFILE
                return clean
    except ImageInputError:
        raise
    except (UnidentifiedImageError, OSError, ValueError, SyntaxError,
            Image.DecompressionBombError, Image.DecompressionBombWarning, ImageCms.PyCMSError):
        raise ImageInputError("Não foi possível decodificar a imagem ou o perfil de cor.") from None


def watermark_once(base, wm, pos_name, scale, opacity, margin, tile):
    if not 0.05 <= scale <= 0.6 or not 0 <= opacity <= 1 or not 0 <= margin <= 2000:
        raise ImageInputError("Configuração de marca d'água fora dos limites.")
    base = base.convert("RGBA")
    target = max(1, int(min(base.size) * scale))
    ratio = target / max(wm.size)
    wm = wm.convert("RGBA").resize((max(1, int(wm.width * ratio)),
                                    max(1, int(wm.height * ratio))), Image.Resampling.LANCZOS)
    wm.putalpha(wm.getchannel("A").point(lambda value: int(value * opacity)))
    x_center, y_center = (base.width - wm.width) // 2, (base.height - wm.height) // 2
    positions = {
        "Canto superior esquerdo": (margin, margin), "Topo centro": (x_center, margin),
        "Canto superior direito": (base.width - wm.width - margin, margin),
        "Meio esquerdo": (margin, y_center), "Centro": (x_center, y_center),
        "Meio direito": (base.width - wm.width - margin, y_center),
        "Canto inferior esquerdo": (margin, base.height - wm.height - margin),
        "Base centro": (x_center, base.height - wm.height - margin),
        "Canto inferior direito": (base.width - wm.width - margin, base.height - wm.height - margin),
    }
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    if tile:
        xs = range(margin, base.width, wm.width + 2 * margin)
        ys = range(margin, base.height, wm.height + 2 * margin)
        if len(xs) * len(ys) > MAX_TILES:
            raise ImageInputError("O mosaico é muito denso. Aumente a margem ou use uma marca menos estreita.")
        for y in ys:
            for x in xs:
                overlay.alpha_composite(wm, dest=(x, y))
    else:
        if pos_name not in positions:
            raise ImageInputError("Posição de marca d'água inválida.")
        overlay.alpha_composite(wm, dest=positions[pos_name])
    result = Image.alpha_composite(base, overlay)
    result.info.clear()
    result.info["icc_profile"] = SRGB_PROFILE
    return result


def process_image_for_pdf(upload, wm_img, pos_name, scale, opacity, margin, tile):
    result = watermark_once(load_image(upload), wm_img, pos_name, scale, opacity, margin, tile)
    rgb = result.convert("RGB")
    rgb.info.clear()
    return rgb


def process_file(upload, wm_img, pos_name, scale, opacity, margin, tile):
    item = validate_upload(upload)
    result = watermark_once(load_image(item), wm_img, pos_name, scale, opacity, margin, tile)
    output = BoundedBuffer()
    if item.format == "JPEG":
        result.convert("RGB").save(output, format="JPEG", quality=95, subsampling=0,
                                   icc_profile=SRGB_PROFILE)
        return output.getvalue(), "jpg", "image/jpeg"
    result.save(output, format="PNG", icc_profile=SRGB_PROFILE)
    return output.getvalue(), "png", "image/png"


def build_batch_zip(uploads, wm_img, *settings):
    items = validate_batch(uploads)
    output = BoundedBuffer()
    with zipfile.ZipFile(output, mode="w", compression=zipfile.ZIP_STORED) as archive:
        for index, item in enumerate(items, 1):
            data, extension, _ = process_file(item, wm_img, *settings)
            # Source file names may contain personal data or path traversal segments.
            archive.writestr(f"imagem_{index:03d}_marcadagua.{extension}", data)
    return output.getvalue()


def build_individual_images(uploads, wm_img, *settings):
    items = validate_batch(uploads)
    results = []
    total_bytes = 0
    for item in items:
        data, extension, mime = process_file(item, wm_img, *settings)
        total_bytes += len(data)
        if total_bytes > MAX_OUTPUT_BYTES:
            raise ImageInputError("As saídas excedem 60 MiB. Divida o lote em partes menores.")
        results.append((data, extension, mime))
    return results


def build_batch_pdf(uploads, wm_img, *settings):
    items = validate_batch(uploads)
    output = BoundedBuffer()
    pdf = canvas.Canvas(output, pageCompression=1)
    pdf.setTitle("Imagens com marca d'água")
    pdf.setAuthor("")
    for item in items:
        image = process_image_for_pdf(item, wm_img, *settings)
        width, height = image.size
        page_size = (width * 72 / 300, height * 72 / 300)
        pdf.setPageSize(page_size)
        pdf.drawImage(ImageReader(image), 0, 0, *page_size)
        pdf.showPage()
        image.close()
    pdf.save()
    return output.getvalue()
