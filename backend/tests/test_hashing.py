import os
import shutil
import tempfile
import pytest
from app.core.hashing import hash_bytes, hash_file, hash_json, hash_directory

def test_hash_bytes():
    data = b"VisionTrust AI - Defense CV Integrity"
    # Expected SHA-256 for this exact byte sequence
    h1 = hash_bytes(data)
    h2 = hash_bytes(data)
    assert len(h1) == 64
    assert h1 == h2
    assert hash_bytes(b"different data") != h1

def test_hash_file():
    with tempfile.NamedTemporaryFile(delete=False) as tf:
        tf.write(b"Military Reconnaissance Image Byte Stream")
        tf_path = tf.name

    try:
        f_hash = hash_file(tf_path)
        expected = hash_bytes(b"Military Reconnaissance Image Byte Stream")
        assert f_hash == expected
    finally:
        os.remove(tf_path)

def test_hash_file_non_existent():
    with pytest.raises(FileNotFoundError):
        hash_file("non_existent_file_path_xyz.bin")

def test_hash_json_canonicalization():
    # Different key ordering and whitespace must produce the EXACT same canonical hash
    obj1 = {"model_id": "RESNET-18", "confidence": 0.95, "tags": ["recon", "tanks"]}
    obj2 = {"tags": ["recon", "tanks"], "confidence": 0.95, "model_id": "RESNET-18"}
    
    h1 = hash_json(obj1)
    h2 = hash_json(obj2)
    assert h1 == h2

    # Modified content must change the hash
    obj3 = {"model_id": "RESNET-18", "confidence": 0.94, "tags": ["recon", "tanks"]}
    assert hash_json(obj3) != h1

def test_hash_directory_determinism():
    temp_dir = tempfile.mkdtemp()
    try:
        # Create nested file structure
        sub1 = os.path.join(temp_dir, "sub1")
        sub2 = os.path.join(temp_dir, "sub2")
        os.makedirs(sub1, exist_ok=True)
        os.makedirs(sub2, exist_ok=True)

        with open(os.path.join(temp_dir, "manifest.txt"), "w") as f:
            f.write("manifest contents")
        with open(os.path.join(sub1, "img_b.png"), "w") as f:
            f.write("image b pixel bytes")
        with open(os.path.join(sub2, "img_a.png"), "w") as f:
            f.write("image a pixel bytes")

        dir_hash1, manifest1 = hash_directory(temp_dir)
        dir_hash2, manifest2 = hash_directory(temp_dir)

        # Determinism check
        assert dir_hash1 == dir_hash2
        assert len(manifest1) == 3
        # Manifest keys must be posix normalized
        assert "manifest.txt" in manifest1
        assert "sub1/img_b.png" in manifest1
        assert "sub2/img_a.png" in manifest1

        # Tampering one file alters directory hash
        with open(os.path.join(sub1, "img_b.png"), "w") as f:
            f.write("tampered pixel bytes")
        
        dir_hash_tampered, _ = hash_directory(temp_dir)
        assert dir_hash_tampered != dir_hash1

    finally:
        shutil.rmtree(temp_dir)
