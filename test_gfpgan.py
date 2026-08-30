import os
import cv2

from gfpgan import GFPGANer


INPUT = "uploads/631f9f329119467dadfd9e2a97edef59_input.jpg"
OUTPUT = "results/gfpgan_test.png"
MODEL = "weights/GFPGANv1.4.pth"


print("=" * 60)
print("GFPGAN v1.4 TEST")
print("=" * 60)

print("Input :", INPUT)
print("Model :", MODEL)
print("Output:", OUTPUT)
print("=" * 60)


if not os.path.isfile(INPUT):
    raise FileNotFoundError(
        "Input image not found: " + INPUT
    )


if not os.path.isfile(MODEL):
    raise FileNotFoundError(
        "GFPGAN model not found: " + MODEL
    )


os.makedirs(
    "results",
    exist_ok=True
)


print("\nLoading GFPGAN v1.4...")


restorer = GFPGANer(
    model_path=MODEL,
    upscale=1,
    arch="clean",
    channel_multiplier=2,
    bg_upsampler=None,
    device="cpu"
)


print("Model loaded.")


img = cv2.imread(INPUT)


if img is None:
    raise RuntimeError(
        "Could not read input image."
    )


print("Image loaded.")
print("Size:", img.shape)


print("\nRunning GFPGAN...")


cropped_faces, restored_faces, restored_img = restorer.enhance(
    img,
    has_aligned=False,
    only_center_face=False,
    paste_back=True,
    weight=0.5
)


cv2.imwrite(
    OUTPUT,
    restored_img
)


print("\n" + "=" * 60)
print("GFPGAN TEST COMPLETE")
print("=" * 60)

print("Final:", os.path.abspath(OUTPUT))
print("=" * 60)