# Multi-omics troubleshooting

- Verify specimen/timepoint mappings from source records. Metadata consistency
  cannot independently authenticate biological identity.
- Report excluded specimens per view and revisit selection bias.
- A subject spanning train and test is leakage. Regroup before fitting any
  learned preprocessing or prediction method.
- Protein identifiers, gene IDs and metabolite annotations are distinct namespaces.
  Resolve ambiguity with organism and release provenance.
- Correlation can reflect composition, batch or an intentionally shared synthetic
  trend. It does not establish regulation, causation or a biomarker.
- A documented MOFA2 or SNF option remains NOT_RUN until that implementation
  executes with its own evidence.

Established method targets include
[MOFA2 documentation](https://biofam.github.io/MOFA2/) and
[scikit-learn leakage guidance](https://scikit-learn.org/stable/common_pitfalls.html).
These are optional workflow targets. This recipe executes NumPy/pandas cross-view
association, with versions recorded per run.
