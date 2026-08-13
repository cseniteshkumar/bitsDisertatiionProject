Run the merge of `gpt_researcher/` into `backend/`.

1. Dry-run merge (archive kept, original retained):

```bash
python3 tools/merge_gpt_to_backend.py
```

2. Merge and delete original `gpt_researcher` after successful merge:

```bash
python3 tools/merge_gpt_to_backend.py --delete-original
```

3. After running the script, run the smoke test and verify:

```bash
python3 tools/smoke_test.py
```

4. If everything is green, commit the changes:

```bash
git add -A
git commit -m "Merge gpt_researcher into backend; archive original; update imports"
```

If any import conflicts remain, open the failing files and adjust imports or resolve
duplicate files created with the `.gpt_researcher` suffix in `backend/`.
