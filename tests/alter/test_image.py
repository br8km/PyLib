from pathlib import Path

from PIL import Image
from pylib.alter.image import ImageRehasher



class Tester:
    """TeseCase for Rehash Image."""

    width = 100
    height = 100
    frames = 10

    rehasher = ImageRehasher()

    def gen_image(self) -> Image.Image:
        """Generate new image with random color."""
        return Image.new(
            mode="RGB",
            size=(self.width, self.height),
            color=self.rehasher.rnd_pixel(),
        )

    def test_png_rehash(self, tmp_path: Path) -> None:
        """Test rehash png image."""
        file_old = tmp_path / "old.png"
        file_new = tmp_path / "new.png"

        file_old.unlink(missing_ok=True)
        file_new.unlink(missing_ok=True)

        assert file_old.is_file() is False
        assert file_new.is_file() is False

        img = self.gen_image()
        img.save(fp=file_old, format="PNG")

        assert file_old.is_file()
        hash_old = self.rehasher.get_hash(file_old)
        assert hash_old

        file_new, obj_new = self.rehasher.new_image(file_old, file_new)
        assert file_new.is_file()

        hash_new = self.rehasher.get_hash(obj_new)
        assert hash_new
        assert hash_old != hash_new
        print(f"png.hash_old = {hash_old}")
        print(f"png.hash_new = {hash_new}")

        file_old.unlink(missing_ok=True)
        file_new.unlink(missing_ok=True)

        assert file_old.is_file() is False
        assert file_new.is_file() is False

    def test_jpg_rehash(self, tmp_path: Path) -> None:
        """Test rehash jpg image."""
        file_old = tmp_path / "old.jpg"
        file_new = tmp_path / "new.jpg"

        file_old.unlink(missing_ok=True)
        file_new.unlink(missing_ok=True)

        assert file_old.is_file() is False
        assert file_new.is_file() is False

        img = self.gen_image()
        img.save(fp=file_old, format="JPEG")
        assert file_old.is_file()
        hash_old = self.rehasher.get_hash(file_old)
        assert hash_old

        file_new, obj_new = self.rehasher.new_image(file_old, file_new)
        assert file_new.is_file()

        hash_new = self.rehasher.get_hash(obj_new)
        assert hash_new
        assert hash_old != hash_new
        print(f"jpg.hash_old = {hash_old}")
        print(f"jpg.hash_new = {hash_new}")

        file_old.unlink(missing_ok=True)
        file_new.unlink(missing_ok=True)

        assert file_old.is_file() is False
        assert file_new.is_file() is False

    def test_gif_rehash(self, tmp_path: Path) -> None:
        """Test rehash gif image."""
        file_old = tmp_path / "old.gif"
        file_new = tmp_path / "new.gif"

        file_old.unlink(missing_ok=True)
        file_new.unlink(missing_ok=True)

        assert file_old.is_file() is False
        assert file_new.is_file() is False

        img, *imgs = [self.gen_image() for _ in range(self.frames)]
        img.save(
            fp=file_old,
            format="GIF",
            append_images=imgs,
            save_all=True,
            druation=100,
            loop=1,
        )

        assert file_old.is_file()
        hash_old = self.rehasher.get_hash(file_old)
        assert hash_old

        file_new, obj_new = self.rehasher.new_image(file_old, file_new)
        assert file_new.is_file()

        hash_new = self.rehasher.get_hash(obj_new)
        assert hash_new
        assert hash_old != hash_new
        print(f"gif.hash_old = {hash_old}")
        print(f"gif.hash_new = {hash_new}")

        file_old.unlink(missing_ok=True)
        file_new.unlink(missing_ok=True)

        assert file_old.is_file() is False
        assert file_new.is_file() is False
