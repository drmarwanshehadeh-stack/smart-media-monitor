# NARA Pilot Reliability Test — Issues 558–560

## Methodological status

This is a model recoding reproducibility test, not a full human intercoder reliability study. The same analytical system re-coded the three editorials using the codebook rules, then the second-pass coding was compared against the original pilot coding. A future validation round should use at least one independent human coder who is blinded to the first coding.

## Source basis

- Issue 558 editorial: «الكفارات والدرجات»
- Issue 559 editorial: «صراع العقيدة»
- Issue 560 editorial: «جلاء القلوب»

## Normalization before comparison

To avoid false disagreement caused by wording differences, comparison uses normalized analytical classes rather than raw prose. Examples:

- «خفض حاد للتعبئة والعودة للوعظ» and «خفض التعبئة/عودة للوعظ» are treated as the same change class.
- Secondary-frame fields are compared at the primary secondary-frame level; additional optional tags are not treated as categorical disagreement.
- Multi-label fields such as ideological references and communication goals are evaluated by core-label overlap rather than string identity.

## Results

### Core categorical variables

| Variable | Agreement | Pilot interpretation |
|---|---:|---|
| Communication topic | 3/3 = 100% | Stable |
| Primary media frame | 3/3 = 100% | Stable |
| Self/Other structure | 3/3 = 100% | Stable at normalized class level |
| Geographic orientation | 3/3 = 100% | Stable |
| Temporal orientation | 3/3 = 100% | Stable after normalization |
| Change vs previous issue | 3/3 = 100% | Stable after normalization |

For variables with more than one observed category in the three-case sample, exact agreement is 100%; therefore Cohen's kappa is 1.00. Because n=3 is extremely small, this should be treated as a pilot signal only, not as a publishable reliability estimate.

### Ordinal scales

| Variable | Round 1 | Round 2 | Agreement |
|---|---|---|---|
| Violence legitimation | 0, 4, 0 | 0, 4, 0 | 100% |
| Mobilization intensity | 1, 4, 1 | 1, 4, 1 | 100% |

Quadratic-weighted Cohen's kappa is 1.00 for both ordinal scales in this pilot sample. Again, the result is unstable because the sample contains only three editorials and uses the same model as recoder.

### Multi-label variables

Ideological references, actors and communication goals show full agreement on the core labels. Minor differences are wording/granularity differences rather than substantive contradictions. Example: Round 1 coded issue 559 secondary frame as «الاستراتيجية/المسؤولية» while Round 2 selected «الاستراتيجية» as the principal secondary frame. This indicates that the codebook should explicitly distinguish one required secondary frame from optional supplementary frames.

## Ambiguities discovered

1. **Secondary frame**: require exactly one secondary frame, with separate optional `additional_frames[]`.
2. **Communication goals**: distinguish primary goal from supporting goals; otherwise multi-label strings may appear inconsistent despite analytical agreement.
3. **Self/Other structure**: use controlled categories plus a free-text description.
4. **Change vs previous issue**: code change on separate axes — topic, mobilization, enemy focus, frame, and violence-legitimation — instead of one composite phrase.
5. **Ideological references**: distinguish source type (Qur'an, hadith, tafsir, scholar, organizational authority) from rhetorical function (legitimation, identity, mobilization, enemy construction, moral instruction).

## Revised acceptance rules

For pilot expansion, a variable is considered ready for automation when:

- Exact agreement >= 0.80 on nominal categories, and
- Cohen's kappa >= 0.70 where kappa is computable, and
- Weighted kappa >= 0.70 for ordinal scales, and
- No recurring disagreement reflects an unclear codebook definition.

The preferred target for the stabilized system is >= 0.80 kappa on core variables.

## Next validation stage

Expand the sample to at least 20–30 editorials spanning different discourse types and periods. Have an independent human coder code a blinded sample using the same codebook. Compute Cohen's kappa for nominal variables, weighted kappa for ordinal variables, and agreement/Jaccard scores for multi-label fields. Revise definitions after adjudicating disagreements, then freeze Codebook v1.0.
