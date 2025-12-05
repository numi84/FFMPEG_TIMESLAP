# Codec Compatibility Matrix

## Overview

This document details which FFMPEG parameters are compatible with each codec.

## Parameter Compatibility Table

| Parameter | H.264 (libx264) | H.265 (libx265) | AV1 (libsvtav1) |
|-----------|----------------|----------------|-----------------|
| **Preset** | ✅ Named (ultrafast-veryslow) | ✅ Named (ultrafast-veryslow) | ✅ Numeric (0-13) |
| **Profile** | ✅ baseline, main, high, high10, high422, high444 | ✅ main, main10, main422-10, main444-8 | ❌ Not used |
| **Level** | ✅ 3.0-5.2 | ⚠️ Optional | ❌ Not used |
| **CRF** | ✅ 0-51 | ✅ 0-51 | ✅ 0-63 |
| **Pixel Format** | ✅ yuv420p, yuv422p, yuv444p | ✅ yuv420p, yuv422p, yuv444p | ✅ yuv420p, yuv422p, yuv444p |
| **Movflags** | ✅ +faststart | ✅ +faststart | ✅ +faststart |
| **Tag** | ❌ Not used | ✅ hvc1 (recommended) | ❌ Not used |

## Detailed Codec Specifications

### H.264 (libx264)

**Supported Presets:**
- ultrafast, superfast, veryfast, faster, fast, medium, slow, slower, veryslow

**Supported Profiles:**
- `baseline` - Basic compatibility (mobile devices)
- `main` - Most devices
- `high` - High quality (recommended for desktop)
- `high10` - 10-bit color depth
- `high422` - 4:2:2 chroma subsampling
- `high444` - 4:4:4 chroma subsampling (lossless)

**Supported Levels:**
- 3.0, 3.1, 4.0, 4.1, 4.2, 5.0, 5.1, 5.2
- Higher levels = higher resolution/bitrate support

**CRF Range:**
- 0-51 (0=lossless, 18=visually lossless, 23=good, 28=acceptable, 51=worst)

**Command Example:**
```bash
ffmpeg -framerate 30 -i input%04d.jpg \
  -c:v libx264 \
  -preset slow \
  -profile:v high \
  -level 4.0 \
  -crf 18 \
  -pix_fmt yuv420p \
  -movflags +faststart \
  output.mp4
```

---

### H.265 / HEVC (libx265)

**Supported Presets:**
- ultrafast, superfast, veryfast, faster, fast, medium, slow, slower, veryslow
- Same names as H.264 but different internal encoding

**Supported Profiles:**
- `main` - 8-bit, 4:2:0 (most common)
- `main10` - 10-bit, 4:2:0
- `main422-10` - 10-bit, 4:2:2
- `main444-8` - 8-bit, 4:4:4
- `main-intra`, `main10-intra` - Intra-only encoding
- Many more specialized profiles...

**Profile Mapping from H.264:**
- H.264 `baseline` → H.265 `main`
- H.264 `main` → H.265 `main`
- H.264 `high` → H.265 `main`
- H.264 `high10` → H.265 `main10`
- H.264 `high422` → H.265 `main422-10`
- H.264 `high444` → H.265 `main444-8`

**Level:**
- Optional for H.265 (auto-detected from resolution/framerate)
- If specified, same range as H.264 (3.0-5.2)

**CRF Range:**
- 0-51 (same as H.264)
- Recommended: 20-28 (H.265 is more efficient, so higher CRF = similar quality to H.264)

**Special Parameters:**
- `-tag:v hvc1` - Required for QuickTime/Apple compatibility
- Without this, videos may not play on macOS/iOS

**Command Example:**
```bash
ffmpeg -framerate 30 -i input%04d.jpg \
  -c:v libx265 \
  -preset slow \
  -profile:v main \
  -crf 20 \
  -pix_fmt yuv420p \
  -tag:v hvc1 \
  -movflags +faststart \
  output.mp4
```

---

### AV1 (libsvtav1)

**Supported Presets:**
- 0-13 (numeric only!)
- 0 = slowest/best quality
- 5 = medium (default)
- 13 = fastest/lowest quality

**Preset Mapping from Named Presets:**
- `ultrafast` → 13
- `superfast` → 12
- `veryfast` → 10
- `faster` → 8
- `fast` → 6
- `medium` → 5
- `slow` → 4
- `slower` → 2
- `veryslow` → 0

**Profile:**
- ❌ Not supported by libsvtav1
- Automatically determined from pixel format

**Level:**
- ❌ Not supported by libsvtav1
- Auto-detected from content

**CRF Range:**
- 0-63 (extended range compared to H.264/H.265)
- Recommended: 23-35 for good quality

**Pixel Formats:**
- yuv420p (8-bit)
- yuv420p10le (10-bit)

**Command Example:**
```bash
ffmpeg -framerate 30 -i input%04d.jpg \
  -c:v libsvtav1 \
  -preset 5 \
  -crf 30 \
  -pix_fmt yuv420p \
  -movflags +faststart \
  output.mp4
```

---

## Common Issues & Solutions

### Issue: "unknown profile <high>" with H.265

**Cause:** H.265 doesn't have a "high" profile, only "main", "main10", etc.

**Solution:** Use profile mapping function to convert H.264 profiles to H.265 equivalents.

### Issue: AV1 encoding fails with "Invalid preset"

**Cause:** libsvtav1 requires numeric presets (0-13), not named presets.

**Solution:** Map named presets to numeric values.

### Issue: Video doesn't play on iPhone/iPad with H.265

**Cause:** Missing `-tag:v hvc1` parameter.

**Solution:** Always add `-tag:v hvc1` for H.265 encoding.

### Issue: Different quality at same CRF between codecs

**Cause:** Each codec has different compression efficiency.

**Reality:**
- H.264 CRF 18 ≈ H.265 CRF 20-22 ≈ AV1 CRF 28-30 (similar visual quality)
- H.265 is ~25-50% more efficient than H.264
- AV1 is ~30-50% more efficient than H.265

---

## Recommended Settings by Use Case

### YouTube Upload (H.264)
```
Codec: libx264
Preset: slow
Profile: high
Level: 4.2
CRF: 18
Resolution: 1920x1080 or 3840x2160
```

### YouTube 4K (H.265)
```
Codec: libx265
Preset: slow
Profile: main
CRF: 20
Resolution: 3840x2160
Tag: hvc1
```

### Archive (H.265 for space savings)
```
Codec: libx265
Preset: veryslow
Profile: main
CRF: 15
Resolution: Original
Tag: hvc1
```

### Instagram (H.264 for compatibility)
```
Codec: libx264
Preset: medium
Profile: main
CRF: 23
Resolution: 1080x1080
```

### Modern Web (AV1 for best compression)
```
Codec: libsvtav1
Preset: 4
CRF: 30
Resolution: 1920x1080
```

---

## Implementation Notes

### Current Implementation Issues

1. **Profile dropdown shows H.264 profiles for all codecs**
   - Fix: Dynamically update profile list based on selected codec
   - OR: Hide profile setting for AV1

2. **Level setting shown for AV1**
   - Fix: Hide level setting when AV1 is selected

3. **Preset names used for AV1**
   - Fix: ✅ Already implemented - mapping function converts to numeric

4. **CRF range doesn't adjust per codec**
   - Current: 0-51 for all
   - Should be: 0-63 for AV1
   - Impact: Minor (51 still works, just not optimal)

---

## Future Improvements

1. **Dynamic UI Updates:**
   - Show/hide profile based on codec
   - Show/hide level based on codec
   - Update CRF slider max value based on codec
   - Show codec-specific tooltips

2. **Codec-Aware Presets:**
   - Adjust default CRF when codec changes
   - Suggest better quality settings per codec

3. **Better Error Messages:**
   - Detect invalid parameter combinations before encoding
   - Show codec-specific validation errors

---

## Testing Matrix

| Codec | Preset | Profile | CRF | Status |
|-------|--------|---------|-----|--------|
| libx264 | medium | high | 18 | ✅ Works |
| libx264 | slow | baseline | 23 | ✅ Works |
| libx265 | medium | main | 20 | ✅ Works (with mapping) |
| libx265 | slow | main10 | 15 | ✅ Works (with mapping) |
| libsvtav1 | 5 | (none) | 30 | ✅ Works (with mapping) |
| libsvtav1 | 0 | (none) | 25 | ✅ Works (with mapping) |

---

*Last Updated: 2025-12-03*
