# Squash-merging dev into main

This project uses a permanent `dev` branch for day-to-day work and a clean
`main` branch that accumulates one commit per milestone. The procedure below
merges all commits on `dev` into a single commit on `main`.

## Procedure

```bash
# 1. Switch to main
git checkout main

# 2. Squash-merge dev, resolving all content conflicts in favour of dev
git merge --squash -X theirs dev

# 3. Remove files that exist on main but were deleted on dev
#    (adjust filenames as needed — git will report modify/delete conflicts)
git rm <file1> <file2>

# 4. Overwrite all auto-merged files with dev's exact versions
git checkout dev -- .

# 5. Commit (git will have pre-populated the message with all squashed commits)
git commit

# 6. Push to GitHub
git push origin main

# 7. Return to dev and continue working
git checkout dev
```

## Why this works

- `git merge --squash` stages dev's changes onto main without creating a merge
  commit or copying dev's commit history.
- `-X theirs` resolves conflict markers automatically in favour of dev, but
  does not affect files that git auto-merges without conflict markers — those
  can end up with mixed content from both branches.
- `git checkout dev -- .` corrects that by overwriting the entire index and
  working tree with dev's exact file tree, guaranteeing that the resulting
  commit is identical in content to dev's tip.
- `git rm` is needed for any file that was deleted on dev but still exists on
  main, because modify/delete conflicts are not resolved by `-X theirs`.

## Important rule

Always squash-merge dev into main — never use a regular `git merge`. A regular
merge would pull all of dev's individual commits into main's history, defeating
the purpose of keeping main clean.

## Continuing on dev

After the squash-merge, dev is completely untouched. Its full commit history is
preserved and new commits can be added normally. The two branches remain
independent: git does not track any link between them after a squash-merge, so
there is no risk of accidentally pulling dev's history into main in a future
merge.
