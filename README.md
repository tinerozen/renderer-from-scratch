# Renderer from scratch

A small ray tracer written with only `numpy` and `matplotlib`. The scene is a sphere and two planes lit by a point light. It renders in grayscale with hard shadows and a crude two-pass indirect lighting.

```bash
pip install -r requirements.txt
python renderer.py
```

## How it works

1. **`render()`, first stage.** It casts a ray per pixel from the camera, finds the closest sphere/plane hit (`collision()`), and adds direct light from every light that isn't blocked. Every lit point is stored per object as a new small `Light` (the "illumination map").
2. **`render2()`, second stage.** It renders again at a higher resolution. This time each hit point also gathers light from the illumination-map points of *other* objects, which gives light bounced off the floor and walls.

The image is the sum of both stages.

## Structure

```
renderer.py     the ray tracer; saves renders/image_dark_sh.png (stage 1, 30×30) and renders/image.png (stage 2, 500×500)
obj_loader.py   start of a .obj loader, reads models/model.obj into triangles (not used by the renderer yet)
models/         model.obj (one triangle), teapot.obj
renders/        output images; "5-50.png" = stage 1 at 5×5, stage 2 at 50×50
```

The resolution comparison block at the bottom of `renderer.py` still calls `render()`/`render2()` the old way, with no arguments, so the script stops there after saving `image.png`.
