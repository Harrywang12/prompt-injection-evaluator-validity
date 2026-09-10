# Final dataset-use audit

Audit date: 2026-08-18 (America/Toronto)

This is a provenance and permissions audit, not legal advice. The frozen task wrapper is `SheltonLiu-N/Universal-Prompt-Injection` revision `19bf570084c82e663d722d1e2ebbdf4395b837c3`, whose repository is MIT-licensed. That wrapper license does not relicense underlying corpora. Split identifications below use the wrapper's task label, exact row count, and official benchmark split sizes. The operational study split remains the exact committed task CSV and hash recorded in `final_generation_config.yaml`.

## Publication-wide rule

The public research repository must not publish raw upstream source text, source reference answers, confirmatory prompts containing that text, or raw victim responses that reproduce it unless the applicable upstream license affirmatively permits redistribution and all required attribution/share-alike terms are satisfied. Restricted material must be preserved in access-controlled storage. Public reproducibility artifacts may contain source identifiers where permitted, hashes, exclusion reasons, sampling probabilities, aggregate statistics, and code that authorized users can run against their own lawful copies.

## Duplicate sentence detection — MRPC

- **Exact dataset/split:** Microsoft Research Paraphrase Corpus, GLUE development/validation split, 408 rows.
- **Frozen wrapper:** `duplicate_sentence_detection/data.csv`, 408 rows, dataset field `MRPC`.
- **Upstream owner/source:** Microsoft Research; [official Microsoft download](https://www.microsoft.com/en-us/download/details.aspx?id=52398). GLUE states that it cannot redistribute MRPC and directs users to the original source and its standardized splitting script ([GLUE FAQ](https://gluebenchmark.com/faq/)).
- **Access conditions:** public Microsoft download; GLUE's 408-row development split is constructed from the original corpus.
- **Terms:** the current official download page requests citation and describes news-source provenance but does not display an affirmative open-data license. GLUE explicitly defers to each original dataset's terms.
- **Planned research use:** **RESOLVED for internal, noncommercial benchmark research**, subject to citation and institutional policy. The official source intentionally releases the corpus for research use.
- **Redistribution:** not affirmatively established. Do not publish raw MRPC-derived text, prompts, reference answers, or text-bearing responses.

## Grammar correction — JFLEG

- **Exact dataset/split:** JFLEG test/evaluation split as represented by the frozen wrapper, 748 rows. The official repository calls this the test split; its README currently describes 747 sentences, so the wrapper's exact 748-row file and hash, rather than the prose count, define the operational frame.
- **Frozen wrapper:** `grammar_correction/data.csv`, 748 rows, dataset field `Jfleg`.
- **Upstream owner/source:** Courtney Napoles, Keisuke Sakaguchi, Joel Tetreault and the JFLEG/GUG contributors; [official JFLEG repository](https://github.com/keisks/jfleg).
- **Access conditions:** public repository.
- **Terms:** Creative Commons Attribution-NonCommercial-ShareAlike 4.0 (`CC BY-NC-SA 4.0`) as stated by the official repository.
- **Planned research use:** **RESOLVED** for this noncommercial research use with attribution.
- **Redistribution:** permitted only with attribution, noncommercial use, and share-alike compliance. To avoid mixing licenses, the public project repository will exclude raw JFLEG text unless it is released in a clearly separated CC BY-NC-SA 4.0 artifact with required attribution.

## Hate detection — HSOL

- **Exact dataset/split:** Davidson et al. Hate Speech and Offensive Language full labeled dataset, 24,783 rows.
- **Frozen wrapper:** `hate_detection/data.csv`, 24,783 rows, dataset field `HSOL`.
- **Upstream owner/source:** Thomas Davidson, Dana Warmsley, Michael Macy, and Ingmar Weber; [official author repository](https://github.com/t-davidson/hate-speech-and-offensive-language).
- **Access conditions:** public repository; content includes racist, sexist, homophobic, and otherwise offensive text. The authors request citation and recommend reviewing known corrections/issues.
- **Terms:** the official repository, including its `data` directory, carries an MIT license. The corpus contains social-media text, so third-party/platform rights and ethical handling remain relevant even though the repository grants reuse rights.
- **Planned research use:** **RESOLVED** with citation, content-safety handling, and no attempt to contact or identify speakers.
- **Redistribution:** the repository license permits redistribution with its notice, but this project will conservatively exclude raw tweet text and text-bearing responses from public Git because of third-party content and platform-policy risk.

## Natural language inference — RTE

- **Exact dataset/split:** GLUE Recognizing Textual Entailment development/validation split, 277 rows.
- **Frozen wrapper:** `natural_language_inference/data.csv`, 277 rows, dataset field `RTE`.
- **Upstream owner/source:** GLUE's RTE task, derived from the annual PASCAL/NIST textual-entailment challenges; [GLUE FAQ](https://gluebenchmark.com/faq/) and [NIST TAC RTE information](https://tac.nist.gov/2008/rte/index.html).
- **Access conditions:** the standardized GLUE task is publicly downloadable. Some original TAC data require registration and an Agreement Concerning Dissemination of TAC Results; GLUE directs users to original task licenses rather than applying a blanket GLUE license.
- **Terms:** no single open license covering all underlying RTE text was established. The frozen 277-row count identifies the GLUE development split, but the wrapper does not retain per-example original challenge/license identifiers.
- **Planned research use:** **RESOLVED for internal benchmark evaluation** under the publicly distributed GLUE task, with citation and no attempt to expand beyond the frozen wrapper. This is not a finding that every underlying text is openly licensed.
- **Redistribution:** not established. Exclude raw RTE text, prompts, reference answers, and text-bearing responses from public release.

## Sentiment analysis — SST-2

- **Exact dataset/split:** GLUE SST-2 development/validation split, 872 rows, derived from the Stanford Sentiment Treebank binary task.
- **Frozen wrapper:** `sentiment_analysis/data.csv`, 872 rows, dataset field `SST2`.
- **Upstream owner/source:** Stanford NLP / Richard Socher and collaborators; [official Stanford Sentiment Treebank site](https://nlp.stanford.edu/sentiment/) and [GLUE FAQ](https://gluebenchmark.com/faq/).
- **Access conditions:** publicly downloadable for benchmark research. GLUE distributes a tokenized standard split and refers users to original terms.
- **Terms:** no affirmative dataset license was found on the official SST distribution page or GLUE card. The source sentences are movie-review excerpts originally collected from Rotten Tomatoes/Pang and Lee.
- **Planned research use:** **RESOLVED for internal academic benchmark evaluation** with required citations and conservative handling.
- **Redistribution:** not affirmatively established. Exclude raw SST-2 text, prompts, reference answers, and text-bearing responses from public release.

## Spam detection — SMS Spam Collection

- **Exact dataset/split:** complete UCI SMS Spam Collection, 5,574 rows; it has no official train/test split.
- **Frozen wrapper:** `spam_detection/data.csv`, 5,574 rows, dataset field `SMS Spam`.
- **Upstream owner/source:** Tiago Almeida and José María Gómez Hidalgo; [official UCI dataset record](https://archive.ics.uci.edu/dataset/228/sms+spam+collection), DOI `10.24432/C5CC84`.
- **Access conditions:** public direct download.
- **Terms:** UCI identifies this dataset as Creative Commons Attribution 4.0 (`CC BY 4.0`), permitting sharing and adaptation for any purpose with attribution.
- **Planned research use:** **RESOLVED** with attribution.
- **Redistribution:** permitted under CC BY 4.0 with attribution. The project will nevertheless omit raw messages from the default public Git history to minimize personal-data and third-party-message risk.

## Summarization — BillSum U.S. federal bills

- **Exact dataset/split:** `FiscalNote/billsum`, U.S. federal `test` split only, 3,269 rows, at Git revision `3d8510441c06a3d9dfb32eb0d7f80151730bcc4f`. The separate `ca_test` split and the training split are excluded. The pinned parquet is `data/test-00000-of-00001.parquet`, SHA-256 `2733cb656a2a6fbff0fc012ca50bbf159615ff6451c0adb229884bbd474780b3`.
- **Fields used:** `text` is the legitimate input, `summary` is retained as the reference answer, and `title` is retained as provenance metadata. A zero-based parquet row index is the source-row ID.
- **Upstream owner/source:** FiscalNote's [official BillSum repository](https://github.com/FiscalNote/BillSum) and [data documentation](https://github.com/FiscalNote/BillSum/blob/master/BillSum_Data_Documentation.md) describe U.S. Congressional bill text and summaries collected from GovInfo/Thomas.gov. The [BillSum paper](https://aclanthology.org/D19-5406/) introduces the U.S. Congressional and California bill summarization dataset. GovInfo is the U.S. Government Publishing Office's official public-information service.
- **Access conditions:** the [official Hugging Face dataset repository/card](https://huggingface.co/datasets/FiscalNote/billsum/blob/main/README.md) is public and nongated. The card separately identifies `test` and `ca_test`; this study uses only `test`.
- **Terms:** the official dataset card identifies the dataset license as `cc0-1.0` and specifically states that the U.S. bills were collected from GovInfo under CC0-1.0. [GovInfo's policies](https://www.govinfo.gov/about/policies) state that U.S. Government works are generally not copyrightable under 17 U.S.C. § 105, while warning that government publications can contain third-party material. This audit therefore does not infer rights from a wrapper alone: it relies on the official BillSum terms and federal-source provenance, and excludes the California split.
- **Planned research use:** **RESOLVED** for the planned research use of the U.S. federal `test` split, with source and paper citation. This is a provenance/permissions determination, not legal advice.
- **Redistribution:** the documented CC0-1.0 status permits reuse and redistribution of the U.S. BillSum material. Preserve provenance and do not imply that unrelated third-party content is licensed merely because it appears in a government publication. The project will still default to publishing source IDs, hashes, code, and aggregate results rather than duplicating the raw corpus.
- **Context eligibility:** before future sampling, all eight frozen attack variants are rendered with each pinned tokenizer. Complete prompts must be at most 8,000 input tokens in all 24 checks, with 128 output tokens reserved. Of 3,269 U.S. test rows, 3,268 passed; one was excluded for context length. No victim response was generated.

## Superseded planned summarization source — Gigaword

Gigaword was originally planned, but applicable LDC authorization for the processed newswire source could not be established. It was removed before external preregistration, before confirmatory source sampling, and before any confirmatory generation. It is not an active confirmatory dependency. The dated substitution record is `source_substitution_001_gigaword_to_billsum.md`.

## Overall determination

The dataset-use audit is **RESOLVED for external preregistration**. JFLEG, HSOL, SMS Spam, and U.S. federal BillSum have affirmative reusable terms. MRPC, RTE, and SST-2 are restricted to conservative internal academic benchmark use with raw public redistribution excluded. The inaccessible Gigaword source is historical only and has no role in the active design. A wrapper license is not treated as an upstream corpus license.
