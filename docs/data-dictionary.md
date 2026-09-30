# Data dictionary and feature inventory

This inventory is derived from column names and dtypes saved in the original notebook. It is not a clinical codebook. Numeric labels, units, response options, and the meaning of spreadsheet-export columns must be confirmed from the data source.

## Core fields and encodings

| Field or group | Role and representation | Treatment in the cleaned notebook |
|---|---|---|
| `SF 36` | Numeric spreadsheet outcome; scoring formula unavailable. | Kept separate from features; raw units for new regression results. |
| `Age`, `weight`, `height`, `Pulse rate`, `Sex`, `Pain` | Demographic, measurement, and coded fields. Units and code meanings are not specified in the notebook. | Retained as numeric when present. |
| `Sno`, `Name`, `Place of birth`, `date`, `month`, `year`, `CR` | Known identity or record fields. The precise administrative definition of `CR` is not supplied. | Excluded before inspection and defensively inside the transformer. |
| `Q1`–`Q36` | Raw questionnaire responses. Exact instrument version and scoring directions unavailable. | Excluded. |
| `Value_Q1`–`Value_Q36` | Scored questionnaire responses. May contribute to the outcome; this is unverified. | Excluded in the primary regression setting; included in reconstruction and descriptive exploration. |
| `Site` | Text tumour-site category. | Lowercase/trim; training categories occurring fewer than 5 times map to `other`; one-hot encode. |
| `staging (TNM)` | Text containing T, N, M stage components. | Replaced by numeric category fields; letter substages collapsed. |
| `Staging` | Overall categorical stage. | I→6, II→5, III→4, IVA→3, IVB→2, IVC→1. |
| `Prakriti` | V/P/K string combination; case and letter order varied in source. | Membership encoded separately; a missing code produces missing indicators. |
| `Prakriti.1` | Duplicate-named Prakriti text field. | Excluded; its exact relationship to `Prakriti` was not documented. |
| `Vatta`, `Pitta`, `Kapha` | Existing numeric fields. Original definitions/scales unavailable. | Preserved without overwriting. |
| Coded physical, behavioural, and lifestyle fields | Mostly integer or floating-point response codes. | Retained as numeric where schema-compatible; mean imputation is an inherited exploratory assumption. |
| `Unnamed:` fields | Headerless spreadsheet-export columns. | Missingness filtering may remove them; retained meanings need a codebook. |

## Engineered feature definitions

| Feature | Definition | Information lost or interpretation limit |
|---|---|---|
| `Tumorsize` | T category 0–4 extracted from the TNM string. | Not a size in millimetres; letter substages and prefix semantics are not modeled. |
| `Lymphnodes` | N category 0–3. | Not a count of nodes; letter substages are collapsed. |
| `Metastasis` | M category 0 or 1. | Categorical encoding, not a probability. |
| `Vata_present` | 1 if V occurs in normalized Prakriti code, otherwise 0; missing code remains missing. | Indicates label membership only. |
| `Pitta_present` | Same rule for P. | Separate from numeric `Pitta`. |
| `Kapha_present` | Same rule for K. | Separate from numeric `Kapha`. |
| `Site_<category>` | One-hot site indicator after training-vocabulary grouping. | Reference category is dropped; categories depend on the training sample. |

Unknown non-empty TNM, stage, or Prakriti labels raise an error for private review. This is a syntax/schema check, not validation of clinical staging rules.

## Missingness policy

The original workflow removed exactly the 30 columns with the most missing entries across the full cohort. The cleaned transformer ranks engineered features using its fit sample, removes up to 30 columns actually containing missing values, and always removes fully empty columns even if they exceed that budget. Ties preserve column order. For regression the fit sample is training data; the test set never selects columns. Complete columns are not discarded merely to fill the budget.

Remaining missing numeric features are mean-imputed and standardized. This policy is retained for continuity and needs sensitivity analysis; coded or ordinal responses may require other treatment.

## Original 143-column numeric matrix

The table below lists the matrix at the original notebook's pre-imputation dtype inspection, excluding the subsequently removed `Prakriti.1`. It includes the outcome; the original regression used 142 predictors after removing the outcome. These names are historical and are not a promise that a cleaned fit produces the same columns.

Original `Pitta` and `Kapha` entries below were already overwritten by membership indicators. Their displayed dtypes therefore do not describe the original score scale. The cleaned version retains the score fields and adds distinct membership fields.

| Original feature | Saved dtype | Cleaned treatment |
|---|---|---|
| `Age` | int64 | Numeric candidate, subject to training missingness filter |
| `weight` | int64 | Numeric candidate, subject to training missingness filter |
| `height` | int64 | Numeric candidate, subject to training missingness filter |
| `Pulse rate` | int64 | Numeric candidate, subject to training missingness filter |
| `CR` | int64 | Excluded identifier |
| `Sex` | int64 | Numeric candidate, subject to training missingness filter |
| `Staging` | float64 | Numeric candidate, subject to training missingness filter |
| `Pain` | int64 | Numeric candidate, subject to training missingness filter |
| `SF 36` | int64 | Outcome only |
| `Value_Q1` | int64 | Reconstruction/descriptive settings only |
| `Value_Q2` | int64 | Reconstruction/descriptive settings only |
| `Value_Q3` | int64 | Reconstruction/descriptive settings only |
| `Value_Q4` | int64 | Reconstruction/descriptive settings only |
| `Value_Q5` | int64 | Reconstruction/descriptive settings only |
| `Value_Q6` | int64 | Reconstruction/descriptive settings only |
| `Value_Q7` | int64 | Reconstruction/descriptive settings only |
| `Value_Q8` | int64 | Reconstruction/descriptive settings only |
| `Value_Q9` | int64 | Reconstruction/descriptive settings only |
| `Value_Q10` | int64 | Reconstruction/descriptive settings only |
| `Value_Q11` | int64 | Reconstruction/descriptive settings only |
| `Value_Q12` | int64 | Reconstruction/descriptive settings only |
| `Value_Q13` | int64 | Reconstruction/descriptive settings only |
| `Value_Q14` | int64 | Reconstruction/descriptive settings only |
| `Value_Q15` | int64 | Reconstruction/descriptive settings only |
| `Value_Q16` | int64 | Reconstruction/descriptive settings only |
| `Value_Q17` | int64 | Reconstruction/descriptive settings only |
| `Value_Q18` | int64 | Reconstruction/descriptive settings only |
| `Value_Q19` | int64 | Reconstruction/descriptive settings only |
| `Value_Q20` | int64 | Reconstruction/descriptive settings only |
| `Value_Q21` | int64 | Reconstruction/descriptive settings only |
| `Value_Q22` | int64 | Reconstruction/descriptive settings only |
| `Value_Q23` | int64 | Reconstruction/descriptive settings only |
| `Value_Q24` | int64 | Reconstruction/descriptive settings only |
| `Value_Q25` | int64 | Reconstruction/descriptive settings only |
| `Value_Q26` | int64 | Reconstruction/descriptive settings only |
| `Value_Q27` | int64 | Reconstruction/descriptive settings only |
| `Value_Q28` | int64 | Reconstruction/descriptive settings only |
| `Value_Q29` | int64 | Reconstruction/descriptive settings only |
| `Value_Q30` | int64 | Reconstruction/descriptive settings only |
| `Value_Q31` | int64 | Reconstruction/descriptive settings only |
| `Value_Q32` | int64 | Reconstruction/descriptive settings only |
| `Value_Q33` | int64 | Reconstruction/descriptive settings only |
| `Value_Q34` | int64 | Reconstruction/descriptive settings only |
| `Value_Q35` | int64 | Reconstruction/descriptive settings only |
| `Value_Q36` | int64 | Reconstruction/descriptive settings only |
| `Vatta` | float64 | Numeric candidate, subject to training missingness filter |
| `Pitta` | int64 | Preserve original score; add separate presence indicator |
| `Kapha` | int64 | Preserve original score; add separate presence indicator |
| `1. The built` | int64 | Numeric candidate, subject to training missingness filter |
| `The body stature / physique (body frame, height)` | int64 | Numeric candidate, subject to training missingness filter |
| `Unnamed: 96` | float64 | Numeric candidate, subject to training missingness filter |
| `The body parts look like` | int64 | Numeric candidate, subject to training missingness filter |
| `The body smell is (body odor)` | float64 | Numeric candidate, subject to training missingness filter |
| `The general appearance` | int64 | Numeric candidate, subject to training missingness filter |
| `The size of the forehead` | float64 | Numeric candidate, subject to training missingness filter |
| `The Hands (length of hand from shoulder to tip of middle finger)` | float64 | Numeric candidate, subject to training missingness filter |
| `The chest (massiveness of chest)` | float64 | Numeric candidate, subject to training missingness filter |
| `The appearance of joints` | float64 | Numeric candidate, subject to training missingness filter |
| `Unnamed: 104` | float64 | Numeric candidate, subject to training missingness filter |
| `The functioning of the joints` | int64 | Numeric candidate, subject to training missingness filter |
| `11. The tone and / or appearance of tendons` | float64 | Numeric candidate, subject to training missingness filter |
| `12. Texture of body muscles on touch (to examine the belly of the muscles)` | float64 | Numeric candidate, subject to training missingness filter |
| `Colour of the sclera (The colour of the white part of the eyes)` | float64 | Numeric candidate, subject to training missingness filter |
| `Iris colour` | float64 | Numeric candidate, subject to training missingness filter |
| `The size of the eyes` | float64 | Numeric candidate, subject to training missingness filter |
| `The appearance of the eyes in general` | float64 | Numeric candidate, subject to training missingness filter |
| `Unnamed: 113` | float64 | Numeric candidate, subject to training missingness filter |
| `Unnamed: 114` | float64 | Numeric candidate, subject to training missingness filter |
| `Appearance of eye lashes` | float64 | Numeric candidate, subject to training missingness filter |
| `Unnamed: 116` | float64 | Numeric candidate, subject to training missingness filter |
| `The skin complexion` | float64 | Numeric candidate, subject to training missingness filter |
| `21. Skin moisture` | float64 | Numeric candidate, subject to training missingness filter |
| `Unnamed: 121` | float64 | Numeric candidate, subject to training missingness filter |
| `Skin texture (on touch)` | float64 | Numeric candidate, subject to training missingness filter |
| `The temperature of the skin at the room temperature` | float64 | Numeric candidate, subject to training missingness filter |
| `Description suiting to the skin` | float64 | Numeric candidate, subject to training missingness filter |
| `Color of the hair` | int64 | Numeric candidate, subject to training missingness filter |
| `Hair moisture and strength of the hair roots (of body hair and scalp hair to be judged by touch)` | int64 | Numeric candidate, subject to training missingness filter |
| `Look wise texture of hair and amount of hair` | int64 | Numeric candidate, subject to training missingness filter |
| `Early hair loss or early balding` | float64 | Numeric candidate, subject to training missingness filter |
| `Texture and quantity of hair of beard and mustache` | int64 | Numeric candidate, subject to training missingness filter |
| `31. Overall nature of appetite` | int64 | Numeric candidate, subject to training missingness filter |
| `Amount of food per meal` | int64 | Numeric candidate, subject to training missingness filter |
| `Frequency of food Intake (digestive capacity)` | int64 | Numeric candidate, subject to training missingness filter |
| `Capacity to skip meals (Tolerance to hunger)` | float64 | Numeric candidate, subject to training missingness filter |
| `Eating habits` | int64 | Numeric candidate, subject to training missingness filter |
| `36. Quantity of water to satisfy thirst along with frequency of thirst` | int64 | Numeric candidate, subject to training missingness filter |
| `Stools` | float64 | Numeric candidate, subject to training missingness filter |
| `Perspiration (Quantity and incidence)` | int64 | Numeric candidate, subject to training missingness filter |
| `Micturation (Quantity and Frequency of Urine)` | float64 | Numeric candidate, subject to training missingness filter |
| `41. Duration for sleep` | int64 | Numeric candidate, subject to training missingness filter |
| `Nature of sleep, freshness after sleep` | float64 | Numeric candidate, subject to training missingness filter |
| `Unnamed: 149` | float64 | Numeric candidate, subject to training missingness filter |
| `Dreams: - most often dreams are related to` | float64 | Numeric candidate, subject to training missingness filter |
| `The walk gait - style and speed (habit of stumbling to objects while walking)` | int64 | Numeric candidate, subject to training missingness filter |
| `Movements and activities` | int64 | Numeric candidate, subject to training missingness filter |
| `46. Physical stamina` | int64 | Numeric candidate, subject to training missingness filter |
| `Voice (quality and pitch of voice)` | int64 | Numeric candidate, subject to training missingness filter |
| `Speech (speaking style)` | int64 | Numeric candidate, subject to training missingness filter |
| `Effectiveness of Speech on Others` | int64 | Numeric candidate, subject to training missingness filter |
| `Sexual desire and function` | float64 | Numeric candidate, subject to training missingness filter |
| `51. Amount of semen` | int64 | Numeric candidate, subject to training missingness filter |
| `Fertility (Choose the best suited answer)` | float64 | Numeric candidate, subject to training missingness filter |
| `Likes and dislikes for food, beverages` | int64 | Numeric candidate, subject to training missingness filter |
| `Unnamed: 162` | float64 | Numeric candidate, subject to training missingness filter |
| `Likes and dislikes for weather or climatic conditions` | int64 | Numeric candidate, subject to training missingness filter |
| `Disliking and / or level of tolerance` | int64 | Numeric candidate, subject to training missingness filter |
| `56. Liking for Various Tastes (Choose Most Favorite)` | int64 | Numeric candidate, subject to training missingness filter |
| `Unnamed: 166` | float64 | Numeric candidate, subject to training missingness filter |
| `57. Hobbies / likings` | float64 | Numeric candidate, subject to training missingness filter |
| `Tendency for possession and donation` | int64 | Numeric candidate, subject to training missingness filter |
| `Unnamed: 176` | float64 | Numeric candidate, subject to training missingness filter |
| `Temperament` | int64 | Numeric candidate, subject to training missingness filter |
| `Unnamed: 179` | float64 | Numeric candidate, subject to training missingness filter |
| `Initiative` | int64 | Numeric candidate, subject to training missingness filter |
| `Unnamed: 182` | float64 | Numeric candidate, subject to training missingness filter |
| `61. Memory (quality and span)` | int64 | Numeric candidate, subject to training missingness filter |
| `Unnamed: 184` | float64 | Numeric candidate, subject to training missingness filter |
| `62. Friendship` | float64 | Numeric candidate, subject to training missingness filter |
| `Unnamed: 186` | float64 | Numeric candidate, subject to training missingness filter |
| `Unnamed: 187` | float64 | Numeric candidate, subject to training missingness filter |
| `Unnamed: 188` | float64 | Numeric candidate, subject to training missingness filter |
| `Concentration` | int64 | Numeric candidate, subject to training missingness filter |
| `Decisive power` | int64 | Numeric candidate, subject to training missingness filter |
| `Performance in field of wisdom` | int64 | Numeric candidate, subject to training missingness filter |
| `Unnamed: 192` | float64 | Numeric candidate, subject to training missingness filter |
| `66 Other qualities` | int64 | Numeric candidate, subject to training missingness filter |
| `Unnamed: 196` | float64 | Numeric candidate, subject to training missingness filter |
| `Resemblance to the animals` | int64 | Numeric candidate, subject to training missingness filter |
| `Acquirement of wealth / means of living (success in life in view of material and financial gain)` | float64 | Numeric candidate, subject to training missingness filter |
| `with age changes that have occurred to the hair` | float64 | Numeric candidate, subject to training missingness filter |
| `Site_hypopharyngeal` | bool | Training-derived dummy vocabulary |
| `Site_maxillary sinus` | bool | Training-derived dummy vocabulary |
| `Site_nasopharyngeal carcinoma` | bool | Training-derived dummy vocabulary |
| `Site_oral cavity` | bool | Training-derived dummy vocabulary |
| `Site_oropharyngeal` | bool | Training-derived dummy vocabulary |
| `Site_other` | bool | Training-derived dummy vocabulary |
| `Site_sinonasal carcinoma` | bool | Training-derived dummy vocabulary |
| `Site_supraglottic` | bool | Training-derived dummy vocabulary |
| `Tumorsize` | float64 | Numeric candidate, subject to training missingness filter |
| `Lymphnodes` | float64 | Numeric candidate, subject to training missingness filter |
| `Metastasis` | float64 | Numeric candidate, subject to training missingness filter |
| `Vata` | int64 | Replaced by Vata_present |
