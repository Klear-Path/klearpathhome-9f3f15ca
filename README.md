# Klear Path Home — CANONICAL PRODUCTION REPOSITORY

This repository is the **single source of truth** for the Klear Path Home website.

- Production domain: https://klearpathhome.org
- Lovable project: https://lovable.dev/projects/c751391e-f4d3-4557-946a-887eee09ae9c
- Production branch: `main`
- Canonical repository: `Klear-Path/klearpathhome-9f3f15ca`

## Operating rule

All website changes — whether made through Lovable, GitHub, ChatGPT, KlearForge, or a local IDE — must land in **this repository**.

`main` represents production source code. Lovable is the production builder/host and is synchronized with this repository.

Do **not** make website changes in `Klear-Path/klearpathhome`; that repository is legacy and retained only for history/recovery.

## Deployment flow

```
edit -> Klear-Path/klearpathhome-9f3f15ca -> main -> Lovable sync -> verify -> publish
```

A code change is not considered live until the Lovable production deployment has been verified.

## Stack

- Vite
- TypeScript
- React
- shadcn/ui
- Tailwind CSS
- Supabase
- Stripe
- Google Analytics / Google Ads
