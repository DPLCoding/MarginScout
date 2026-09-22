# Public repository publication checklist

The safe publication unit is this `public-showcase` directory only. Do not initialize or push the private MarginScout project root.

## 1. Personalize the public files

Replace the placeholders in `README.md`, `SECURITY.md`, `PRIVACY.md`, and `docs/REDDIT_API_APPLICATION.md`:

```powershell
rg -n "<[A-Z_]+>" .
```

Use a public contact address. Do not paste a Reddit client secret, refresh token, OpenAI key, database URL, or production hostname into any document.

## 2. Run the zero-network checks

From this directory:

```powershell
python -m unittest discover -s tests -v
python tools/audit_release.py --strict
```

The audit fails for unexpected files, forbidden filenames, common credential formats, private keys, and unresolved placeholders in strict mode. It is a backstop, not a substitute for manually reading every file.

## 3. Review exactly what will be public

Initialize a new repository only inside this directory:

```powershell
git init
git branch -M main
git add .
git status --short
git diff --cached --stat
git diff --cached
```

Confirm that the staged files match `PUBLIC_FILES.txt`. In particular, there must be no `.env`, database, log, backup, screenshot containing personal information, private plan, copied production module, or parent-directory file.

## 4. Commit locally

```powershell
git commit -m "Publish MarginScout architecture and integration excerpt"
```

Create the empty public GitHub repository under your own account, add its remote, and push this directory. Do not use an import tool pointed at the private project folder.

## 5. Final browser review

After publishing:

- open every repository file on GitHub;
- confirm Mermaid diagrams render;
- confirm your contact and repository/privacy URLs are correct;
- check the Git history contains only the curated public files;
- enable secret scanning if your GitHub plan provides it; and
- use the public repository URL in the Reddit application while clearly stating that it is a sanitized excerpt.

## If a secret is exposed

Deleting it in a later commit is not sufficient. Immediately revoke/rotate the credential, remove it from Git history, and verify the remote history before continuing.
