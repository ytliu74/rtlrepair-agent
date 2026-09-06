#!/usr/bin/env bash
# Optional document-export tooling, not a baseline runtime dependency.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
pandoc proposal/capstone_proposal.md \
    --resource-path=proposal \
    --reference-doc=CSE598-capstone-proposal-template.docx \
    --output=proposal/capstone_proposal.docx
pandoc proposal/capstone_proposal.md \
    --resource-path=proposal \
    --pdf-engine=xelatex \
    -V documentclass=article -V fontsize=11pt \
    -V geometry:margin=0.8in -V colorlinks=true \
    --output=proposal/capstone_proposal.pdf
echo 'Exported proposal/capstone_proposal.docx and proposal/capstone_proposal.pdf'
echo 'Review pagination and evidence status before submitting.'
