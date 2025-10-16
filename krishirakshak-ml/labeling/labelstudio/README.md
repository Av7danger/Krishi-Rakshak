# Label Studio Integration

1. Create a project and import `project_config.xml` (labels: aphid, caterpillar, leaf_spot, healthy).
2. Import images from `data/raw/`.
3. Export JSON when done and place under `data/labeled/export.json`.
4. Convert to YOLO with:

```bash
python labeling/label_conversion.py --ls-json data/labeled/export.json --out datasets/build/labels/train
```

## Localized instructions (Hindi example)
- कृपया कीट/रोग के चार बॉक्स लेबल का उपयोग करें: aphid, caterpillar, leaf_spot, healthy
- बॉक्स को पत्ते के प्रभावित हिस्से तक सीमित रखें
- संदिग्ध मामलों में "healthy" न चुनें; छोड़ दें या "leaf_spot" चुनें

## Versioning with DVC or Git LFS
- DVC (recommended):
  - `dvc init` (once)
  - `dvc add data/labeled/`
  - `git add data/labeled.dvc .gitignore && git commit -m "label data version"`
  - `dvc remote add -d origin <s3://bucket or gdrive://id>`
  - `dvc push`
- Git LFS:
  - `git lfs install`
  - `git lfs track "data/labeled/**"`
  - `git add .gitattributes data/labeled && git commit -m "label data" && git push`

