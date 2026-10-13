# Reference camera calibration

Reference: `20261013_223009.jpg`, original 4000 x 3000 (4:3).

## Verified EXIF

- Camera: Samsung Galaxy S25+
- Capture time: 2026-10-13 22:30:09, +09:00
- Focal length: 5.4 mm; 35 mm equivalent: 23 mm
- Digital zoom: 1.0; orientation: 1 (no rotation)
- Exposure: approximately 1/120 s, f/1.8, ISO 800, flash off

## Projection and pose

The 35 mm equivalent focal length is treated as a diagonal equivalence.
Using a 43.2666 mm full-frame diagonal and the photo's 4:3 aspect gives
a vertical field of view of 58.8762 degrees (horizontal approximately 73.9 degrees).
This is an initial pinhole estimate; EXIF does not provide calibrated lens distortion
or the principal point after the phone's image processing.

The pose was fitted using the four back-wall corners and the ceiling-hole center,
with the existing 25 x 20 x 15 scene dimensions. Measured image coordinates on an
1824 x 1368 copy were (428,277), (1398,267), (1407,1026), (441,1040), (906,163).

- Eye in scene units: (-0.11961, 10.49493, -16.62716)
- Forward: (0.007726, -0.035888, 0.999326), about 2.06 degrees downward
- Up: (-0.013733, 0.999258, 0.035992), including the photo's slight roll
- Mean landmark error: approximately 15.5 px at 4000 x 3000, or 4.0 px at 1024 x 768

The cardboard is not perfectly rectangular and the hole is irregular, so this is
an approximate fit. The objects were then positioned using their horizontal
silhouette centers and their bottom contact points in the photograph:

- Case and lid seam center: (4.20, 1.39, 9.57)
- Cap center: (-4.16, 1.50, 4.47)

Their dimensions were retained. At 1024 x 768, the target silhouette centers are
approximately x=405.6 and x=650; the lower silhouette edges are approximately
y=646 and y=716. Remaining shape, lighting, and material differences are separate
from this position fit.

Press `R` to restore the calibrated camera. The initial window uses the photo's 4:3 aspect.
