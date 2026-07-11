Here’s a clean way to design this system using only classical computer vision + face recognition libraries in Python (no LLM needed).

---

# 1. Define the Overall Goal Clearly

You want to:

1. Scan all images in a folder
2. Detect all faces
3. Identify which faces belong to the same person
4. Build a mapping:

   * Person A → photos containing them
   * Person B → photos containing them
5. Score photos by quality/clarity
6. Iteratively:

   * Pick the person with the fewest photos
   * Keep their best photo
   * Remove all other photos containing that person
   * Remove every person appearing in the kept photo from future processing
7. Continue until all people are processed

This is essentially:

* Face clustering
* Photo quality ranking
* Greedy set-cover style selection

---

# 2. Suggested Tech Stack

Use these components:

## Face Detection + Embedding

Best practical options:

### Option A (recommended)

* `InsightFace`
* Very accurate
* Fast
* Gives:

  * face detection
  * face embeddings
  * landmarks

### Option B

* `face_recognition`
* Easier but slower and less accurate on large datasets

For a serious project:
→ Use `InsightFace`

---

# 3. High-Level Pipeline

Your system should run in these stages:

```text
Stage 1 → Scan Images
Stage 2 → Detect Faces
Stage 3 → Generate Face Embeddings
Stage 4 → Cluster Faces into People
Stage 5 → Build Person ↔ Photo Mapping
Stage 6 → Compute Photo Quality Scores
Stage 7 → Run Selection + Deletion Algorithm
Stage 8 → Export Results
```

---

# 4. Stage 1 — Scan Images

Traverse the folder recursively.

For every image:

Store:

```text
photo_id
file_path
width
height
timestamp (optional)
```

Create a unique internal ID for every image.

---

# 5. Stage 2 — Detect Faces

For each image:

Run face detection.

For every detected face:

Extract:

* bounding box
* face crop
* landmarks
* confidence score

Important:
Discard:

* blurry tiny faces
* profile faces
* low-confidence detections

Store each detected face as:

```text
face_id
photo_id
bbox
embedding
```

---

# 6. Stage 3 — Generate Face Embeddings

For every face crop:

Generate a numerical vector representation (embedding).

Typical embedding size:

* 128
* 256
* 512 dimensions

This embedding represents facial identity.

Faces of the same person should have nearby embeddings in vector space.

---

# 7. Stage 4 — Cluster Faces into People

Now you need to group embeddings.

This is the most important step.

## Use Clustering

Recommended:

* DBSCAN
* HDBSCAN

Why:

* You don’t know number of people beforehand
* Works well for face clustering

Process:

```text
Input:
all face embeddings

Output:
cluster_1 → Person A
cluster_2 → Person B
...
```

Each cluster = one person.

---

# 8. Handle Noise / Unknown Faces

Some detections will be bad.

DBSCAN labels them as:

```text
-1
```

Ignore those.

---

# 9. Build Person ↔ Photo Mapping

Now build:

## Person to Photos

```text
Person_1:
    photo_3
    photo_9
    photo_22
```

## Photo to Persons

```text
photo_22:
    Person_1
    Person_5
    Person_7
```

You need BOTH mappings.

---

# 10. Count Photos Per Person

Now compute:

```text
Person_1 → 15 photos
Person_2 → 3 photos
Person_3 → 90 photos
```

Important:
Count UNIQUE photos only.

If same person appears twice in one image:
→ count as one photo.

---

# 11. Stage 6 — Compute Photo Quality Score

This is critical.

You need a combined score.

---

# 12. Quality Metrics You Should Use

For each photo compute:

## A. Sharpness / Blur Score

Use:

* Variance of Laplacian

Higher variance:
→ sharper image

---

## B. Face Size Score

Larger face:
→ usually better portrait quality

Use:

```text
face_area / image_area
```

---

## C. Face Pose Score

Use landmarks to estimate:

* frontal face preferred
* side faces penalized

---

## D. Eye Visibility

Check:

* both eyes visible
* open eyes preferred

---

## E. Brightness

Avoid:

* too dark
* overexposed

---

## F. Detection Confidence

Face detector confidence score.

---

# 13. Create a Final Quality Formula

Example conceptual formula:

```text
quality_score =
    0.35 * sharpness
  + 0.25 * face_size
  + 0.20 * frontal_pose
  + 0.10 * brightness
  + 0.10 * detector_confidence
```

Normalize all scores before combining.

---

# 14. Ranking Photos for Each Person

Now for each person:

Sort their photos descending by:

```text
quality_score
```

Store:

```text
Person_2:
    photo_9   score=0.95
    photo_3   score=0.82
    photo_15  score=0.71
```

---

# 15. Your Selection Algorithm (Core Logic)

This is the heart of your system.

---

# 16. Initialize Working Structures

Create:

## Active People Set

```text
remaining_people
```

## Active Photos Set

```text
remaining_photos
```

## Final Selected Photos

```text
selected_photos
```

---

# 17. Main Iterative Process

Repeat until no people remain.

---

# 18. Step A — Recompute Counts

For remaining people only:

Count how many remaining photos contain them.

---

# 19. Step B — Pick Rarest Person

Choose:

```text
person_with_minimum_photo_count
```

Reason:
You want to preserve scarce identities first.

---

# 20. Step C — Select Their Best Photo

From their remaining photos:

Pick highest-ranked photo.

```text
best_photo = top quality photo
```

Add to:

```text
selected_photos
```

---

# 21. Step D — Find Everyone in That Photo

Use:

```text
photo_to_persons[best_photo]
```

Suppose photo contains:

```text
Person_2
Person_5
Person_9
```

---

# 22. Step E — Remove Those People

Delete:

```text
Person_2
Person_5
Person_9
```

from:

```text
remaining_people
```

Why:
They are now already represented.

---

# 23. Step F — Remove Redundant Photos

Delete all remaining photos containing those people.

This prevents duplicate representation.

---

# 24. Repeat

Continue until:

```text
remaining_people = empty
```

---

# 25. Important Edge Cases

You must handle:

## A. Same Group Appearing Together Everywhere

If:

```text
A+B+C always together
```

One photo solves all three.

---

## B. Bad Clusters

Sometimes one person becomes:

```text
cluster_7
cluster_12
```

Need threshold tuning.

---

## C. False Positives

People incorrectly merged.

Need embedding distance threshold calibration.

---

## D. Tiny Faces

Ignore faces below minimum size.

---

# 26. Data Structures You’ll Need

---

## Photo Object

```text
photo_id
path
quality_score
persons_present
```

---

## Person Object

```text
person_id
photo_ids
sorted_photos
count
```

---

## Face Object

```text
face_id
photo_id
embedding
bbox
cluster_id
```

---

# 27. Recommended Folder Structure

```text
project/
│
├── images/
├── embeddings/
├── crops/
├── clusters/
├── results/
├── logs/
└── cache/
```

---

# 28. Save Intermediate Results

Very important.

Save:

* embeddings
* clusters
* mappings
* quality scores

Because face processing is expensive.

Use:

* SQLite
  or
* Pickle/Parquet/JSON

---

# 29. Performance Considerations

If you have thousands of photos:

Use:

* batch processing
* GPU inference
* multiprocessing

Most expensive steps:

1. face detection
2. embedding generation

---

# 30. Suggested Development Order

Do NOT build everything at once.

Build in this order:

## Phase 1

Face detection on images

## Phase 2

Face embeddings

## Phase 3

Clustering

## Phase 4

Person-photo mapping

## Phase 5

Quality scoring

## Phase 6

Selection algorithm

## Phase 7

Deletion pipeline

---

# 31. Test on Small Dataset First

Start with:

```text
50–100 photos
```

Manually inspect:

* clusters
* rankings
* selections

Then scale.

---

# 32. Final Output You Can Generate

## A. CSV

```text
person_id, photo_count, selected_photo
```

---

## B. Folder Structure

```text
selected/
deleted/
```

---

## C. Visual Reports

Optional:

* contact sheets
* face clusters
* duplicate groups

---

# 33. Most Important Engineering Decision

The success of your project depends mostly on:

```text
face clustering quality
```

NOT on the selection algorithm.

Spend most effort tuning:

* embedding model
* clustering thresholds
* filtering bad detections

---

# 34. Recommended Exact Stack (Practical)

If you want the most practical route:

```text
Python
OpenCV
InsightFace
NumPy
scikit-learn
HDBSCAN
Pandas
SQLite
```

This is enough to build the entire system.
