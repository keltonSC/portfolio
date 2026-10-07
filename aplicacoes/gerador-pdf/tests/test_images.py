import io
import struct
import unittest
import zipfile
import zlib
from unittest.mock import patch

from PIL import Image, ImageCms, PngImagePlugin
from pypdf import PdfReader

import image_processing as processing
import PDFapp as app

SETTINGS = ("Centro", 0.2, 0.6, 4, False)
PRIVATE_MARKER = "SYNTHETIC_PRIVATE_METADATA"


def upload(format="PNG", size=(40, 20), name=None, **kwargs):
    output = io.BytesIO()
    image = Image.new("RGB", size, (45, 120, 210))
    image.save(output, format=format, **kwargs)
    output.seek(0)
    output.name = name or ("fixture.jpg" if format == "JPEG" else "fixture.png")
    return output


class ImageTests(unittest.TestCase):
    def setUp(self):
        self.watermark = Image.new("RGBA", (12, 6), (255, 255, 255, 180))

    def assert_private_metadata_removed(self, data):
        self.assertNotIn(PRIVATE_MARKER.encode(), data)
        with Image.open(io.BytesIO(data)) as image:
            self.assertFalse(image.getexif())
            self.assertNotIn("xmp", image.info)
            self.assertNotIn("comment", image.info)
            self.assertNotIn("Author", image.info)
            profile = ImageCms.ImageCmsProfile(io.BytesIO(image.info["icc_profile"]))
            self.assertIn("sRGB", ImageCms.getProfileName(profile))

    def test_valid_jpeg_png_and_stream_position(self):
        for format in processing.FORMATS:
            with self.subTest(format=format):
                source = upload(format)
                source.seek(5)
                image = processing.load_image(source)
                self.assertEqual(source.tell(), 5)
                self.assertEqual(image.size, (40, 20))
                self.assertEqual(image.mode, "RGBA")

    def test_disguised_decoder_and_extension_mismatch_rejected(self):
        for source in [upload("GIF", name="pretend.jpg"),
                       upload("PNG", name="pretend.jpg"),
                       upload("PNG", name="pretend.txt")]:
            with self.subTest(name=source.name):
                with self.assertRaises(processing.ImageInputError):
                    processing.load_image(source)

    def test_fits_decoder_is_never_enabled(self):
        source = io.BytesIO(b"SIMPLE  =                    T" + b" " * 2850)
        source.name = "pretend.png"
        with patch.object(processing.Image, "open", wraps=Image.open) as opener:
            with self.assertRaises(processing.ImageInputError):
                processing.load_image(source)
            self.assertEqual(opener.call_args.kwargs["formats"], ("JPEG", "PNG"))

    def test_invalid_and_truncated_data_rejected_safely(self):
        sources = [io.BytesIO(b"not an image"), io.BytesIO(upload("JPEG").getvalue()[:-30])]
        for source in sources:
            source.name = "private-person.jpg"
            with self.subTest(size=len(source.getvalue())):
                with self.assertRaises(processing.ImageInputError) as error:
                    processing.load_image(source)
                self.assertNotIn(source.name, str(error.exception))

    def test_byte_limit_and_empty_upload(self):
        for payload in [b"", b"x" * 65]:
            source = io.BytesIO(payload)
            source.name = "fixture.png"
            with patch.object(processing, "MAX_FILE_BYTES", 64):
                with self.assertRaises(processing.ImageInputError):
                    processing.validate_upload(source)

    def test_large_declared_dimensions_rejected_before_decode(self):
        source = bytearray(upload(size=(1, 1)).getvalue())
        source[16:24] = struct.pack(">II", processing.MAX_SIDE + 1, 1)
        source[29:33] = struct.pack(">I", zlib.crc32(source[12:29]))
        file = io.BytesIO(source)
        file.name = "fixture.png"
        with self.assertRaisesRegex(processing.ImageInputError, "8000"):
            processing.load_image(file)

    def test_pixel_and_decompression_bomb_limits(self):
        source = upload(size=(40, 20))
        with patch.object(processing, "MAX_PIXELS", 799):
            with self.assertRaises(processing.ImageInputError):
                processing.load_image(source)
        with patch.object(Image, "MAX_IMAGE_PIXELS", 100):
            with self.assertRaises(processing.ImageInputError):
                processing.load_image(source)

    def test_animation_rejected(self):
        source = io.BytesIO()
        frames = [Image.new("RGB", (8, 8), color) for color in ["red", "blue"]]
        frames[0].save(source, format="PNG", save_all=True, append_images=frames[1:], duration=100)
        source.name = "animated.png"
        with self.assertRaisesRegex(processing.ImageInputError, "animadas"):
            processing.load_image(source)

    def test_batch_quantity_byte_and_pixel_limits(self):
        with self.assertRaises(processing.ImageInputError):
            processing.validate_batch([upload()] * 21)
        with self.assertRaises(processing.ImageInputError):
            processing.validate_batch([])
        with patch.object(processing, "MAX_BATCH_BYTES", 1):
            with self.assertRaises(processing.ImageInputError):
                processing.validate_batch([upload()])
        with patch.object(processing, "MAX_BATCH_PIXELS", 1599):
            with self.assertRaises(processing.ImageInputError):
                processing.validate_batch([upload(), upload()])

    def test_exif_orientation_and_personal_tags_removed(self):
        exif = Image.Exif()
        exif[274] = 6
        exif[315] = PRIVATE_MARKER
        exif[37510] = PRIVATE_MARKER.encode()
        exif[34853] = {1: "N", 2: (1.0, 2.0, 3.0), 3: "E", 4: (4.0, 5.0, 6.0)}
        source = upload("JPEG", exif=exif)
        before = source.getvalue()
        image = processing.load_image(source)
        self.assertEqual(image.size, (20, 40))
        data, _, _ = processing.process_file(source, self.watermark, *SETTINGS)
        self.assert_private_metadata_removed(data)
        self.assertEqual(source.getvalue(), before)
        with Image.open(io.BytesIO(data)) as result:
            self.assertEqual(result.size, (20, 40))

    def test_png_text_exif_and_comments_removed(self):
        metadata = PngImagePlugin.PngInfo()
        metadata.add_text("Author", PRIVATE_MARKER)
        metadata.add_text("XML:com.adobe.xmp", PRIVATE_MARKER)
        exif = Image.Exif()
        exif[315] = PRIVATE_MARKER
        source = upload(pnginfo=metadata, exif=exif)
        data, _, _ = processing.process_file(source, self.watermark, *SETTINGS)
        self.assert_private_metadata_removed(data)

    def test_standardized_color_and_alpha(self):
        source = upload(icc_profile=processing.SRGB_PROFILE)
        loaded = processing.load_image(source)
        self.assertEqual(loaded.getpixel((0, 0)), (45, 120, 210, 255))
        transparent = io.BytesIO()
        Image.new("RGBA", (8, 8), (20, 30, 40, 100)).save(transparent, format="PNG")
        transparent.name = "alpha.png"
        self.assertEqual(processing.load_image(transparent).getpixel((0, 0))[3], 100)

    def test_exif_orientation_rotates_pixels_correctly(self):
        original = Image.new("RGB", (2, 3))
        original.putdata([(255, 0, 0), (0, 255, 0), (0, 0, 255),
                          (255, 255, 255), (255, 128, 0), (128, 0, 255)])
        exif = Image.Exif()
        exif[274] = 6
        source = io.BytesIO()
        original.save(source, format="PNG", exif=exif)
        source.name = "rotation.png"
        result = processing.load_image(source)
        self.assertEqual(result.size, (3, 2))
        self.assertEqual(result.getpixel((2, 0))[:3], (255, 0, 0))
        self.assertEqual(result.getpixel((0, 0))[:3], (255, 128, 0))
        self.assertFalse(result.getexif())

    def test_invalid_icc_rejected_without_source_detail(self):
        source = upload(icc_profile=b"invalid-profile-" + PRIVATE_MARKER.encode())
        with self.assertRaises(processing.ImageInputError) as error:
            processing.load_image(source)
        self.assertNotIn(PRIVATE_MARKER, str(error.exception))

    def test_zip_has_safe_unique_names_and_sanitized_images(self):
        sources = [upload(name="../../private-person.png"), upload(name="../../private-person.png")]
        data = processing.build_batch_zip(sources, self.watermark, *SETTINGS)
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            self.assertEqual(archive.namelist(), ["imagem_001_marcadagua.png", "imagem_002_marcadagua.png"])
            self.assertIsNone(archive.testzip())
            for entry in archive.namelist():
                self.assert_private_metadata_removed(archive.read(entry))

    def test_pdf_pages_images_and_no_source_metadata(self):
        exif = Image.Exif()
        exif[315] = PRIVATE_MARKER
        data = processing.build_batch_pdf([upload("JPEG", exif=exif), upload()], self.watermark, *SETTINGS)
        document = PdfReader(io.BytesIO(data), strict=True)
        self.assertEqual(len(document.pages), 2)
        self.assertNotIn(PRIVATE_MARKER.encode(), data)
        for page in document.pages:
            self.assertEqual(len(page.images), 1)
            for image in page.images:
                self.assertNotIn(PRIVATE_MARKER.encode(), image.data)

    def test_brochure_and_combined_pdf_integration(self):
        with patch.object(app, "get_native_logo", return_value=None):
            cover = app.build_folheto_pdf(
                processing.load_image(upload()), "Projeto fictício", "Bairro fictício", "",
                {}, wm_for_cover=self.watermark, wm_position=SETTINGS[0], wm_scale=SETTINGS[1],
                wm_opacity=SETTINGS[2], wm_margin=SETTINGS[3], wm_tile=SETTINGS[4],
            )
            combined = app.build_combined_pdf(upload(), [upload()], "Projeto fictício",
                                             "Bairro fictício", "", {}, self.watermark, *SETTINGS)
        self.assertEqual(len(PdfReader(io.BytesIO(cover), strict=True).pages), 1)
        self.assertEqual(len(PdfReader(io.BytesIO(combined), strict=True).pages), 2)

    def test_output_bound_rejects_pdf_zip_and_image_outputs(self):
        with patch.object(processing, "MAX_OUTPUT_BYTES", 20):
            for exporter in [processing.build_batch_pdf, processing.build_batch_zip]:
                with self.subTest(exporter=exporter.__name__):
                    with self.assertRaises(processing.ImageInputError):
                        exporter([upload()], self.watermark, *SETTINGS)
            with self.assertRaises(processing.ImageInputError):
                processing.process_file(upload(), self.watermark, *SETTINGS)

    def test_individual_output_aggregate_limit(self):
        with patch.object(processing, "process_file", return_value=(b"x" * 12, "png", "image/png")):
            with patch.object(processing, "MAX_OUTPUT_BYTES", 20):
                with self.assertRaises(processing.ImageInputError):
                    processing.build_individual_images([upload(), upload()], self.watermark, *SETTINGS)

    def test_dense_tiling_and_invalid_settings_rejected(self):
        with patch.object(processing, "MAX_TILES", 1):
            with self.assertRaises(processing.ImageInputError):
                processing.watermark_once(Image.new("RGBA", (40, 20)), self.watermark,
                                          "Centro", 0.2, 0.6, 0, True)
        with self.assertRaises(processing.ImageInputError):
            processing.watermark_once(Image.new("RGBA", (40, 20)), self.watermark,
                                      "Centro", 0.01, 0.6, 0, False)

    def test_generic_demo_watermark_without_brand_assets(self):
        with patch.object(app.os.path, "exists", return_value=False):
            self.assertIsNone(app.get_native_logo())
            watermark = app.get_native_watermark()
        self.assertEqual(watermark.mode, "RGBA")
        self.assertGreater(watermark.getchannel("A").getextrema()[1], 0)


if __name__ == "__main__":
    unittest.main()
