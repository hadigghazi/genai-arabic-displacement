* =============================================================================.
* 02_hypotheses.sps - descriptives, confirmatory tests and robustness checks.
* The choices behind every test are in analysis/ANALYSIS-DECISIONS.md.
* Written for SPSS 23. Done only in analysis/03_python_stats.py: Holm corrections, Page's trend test,.
* HC3 standard errors (SPSS 23's REGRESSION has no HC3 option), the wild bootstrap, the H5 and E1 mediation,.
* the Firth logit, the ordinal H4 check, exact signed-rank p for groups of 15 or fewer non-zero answers,.
* effect sizes, Wilson intervals and omega. SPSS shows classical OLS errors; the paper reports the HC3 ones.
* Run 01_import_and_score.sps first (this file reads the .sav that 01 writes). Then: select all, Run.
* NOTE FOR EDITING: every comment line must end with a period. A comment line that does not end.
* with a period swallows the next command. analysis/lint_sps.py checks this.
* =============================================================================.

FILE HANDLE proj /NAME='C:\Users\User\ai-language-gap-paper\analysis'.
GET FILE='proj/data/ai-arabic-survey.sav'.
* Show variable names, not the long question labels, so tables fit the page without shrinking.
SET TVARS=NAMES.

* Legacy NPAR TESTS compares two variables, so a one-sample test against zero pairs each.
* domain with a variable that is always 0.
COMPUTE zero = 0.
* Same direction as the loss scores (higher = more loss), for the social-media comparison.
COMPUTE SocialLoss = -SocialMedia.
COMPUTE SocialDecrease = (SocialMedia < 0).
COMPUTE Under25 = (Age25 = 0).
COMPUTE RegisterDecline = -Abil_Register_f.
* Same setting, and also no start of English-medium study or work (sensitivity).
COMPUTE stable_noeng = (stable = 1 AND Events_4 = 0).
VARIABLE LEVEL d_WorkStudy d_Writing d_Self d_Personal d_Family d_Fusha d_Religion d_Consume
  Displacement Displacement4 DialectLoss FormalLoss Disp_Fusha Disp_WorkStudy Disp_Personal Disp_Family
  AbilityDecline QualityGap AI_Intensity EnglishShare SocialLoss RegisterDecline zero (SCALE).
EXECUTE.

* ============================================================ participants.
TITLE 'Participants'.
* Submitted, consented, eligible, outside the core sample, straight-liners.
FREQUENCIES Consent Eligible excl_region moved core straightline.

* ============================================================ all respondents from here on.
TITLE 'All respondents: descriptives and the eight areas'.
* The primary sample is all respondents. The core sample is analysed as a sensitivity check at the end.
FILTER OFF.

* ------------------------------------------------------------ Table 1: the sample.
FREQUENCIES Consent Eligible L1_Home_1 TO L1_Home_4 Role Education Field Age Gender
  Country_GrewUp Country_Now Moved_Since2022 AI_Start AI_Freq AI_TaskShare AI_Breadth_1 TO AI_Breadth_8
  AI_Lang AI_Content AI_ContentLang FushaPreAI Sch_SciLang Uni_Lang Eng_Prof Events_1 TO Events_6.

* ------------------------------------------------------------ the other questionnaire items.
FREQUENCIES SocialMedia Abil_Lexical Abil_Fluency Abil_ArabicOnly Abil_Register
  Gap_Understand Gap_Accuracy Gap_Voice Gap_Equal
  Future_WorkStudy Future_Writing Future_Self Future_Personal Future_Family Future_Formal Future_Religion Future_Consume.

* ------------------------------------------------------------ reliability.
RELIABILITY /VARIABLES=d_WorkStudy d_Writing d_Self d_Personal d_Family d_Fusha d_Religion d_Consume
  /SCALE("Displacement") ALL /MODEL=ALPHA /SUMMARY=TOTAL.
RELIABILITY /VARIABLES=Abil_Lexical Abil_Fluency Abil_ArabicOnly /SCALE("Ability decline") ALL /MODEL=ALPHA /SUMMARY=TOTAL.
RELIABILITY /VARIABLES=Gap_Understand Gap_Accuracy Gap_Voice Gap_Equal_r /SCALE("Quality gap") ALL /MODEL=ALPHA /SUMMARY=TOTAL.
RELIABILITY /VARIABLES=Gap_Understand Gap_Accuracy Gap_Equal_r /SCALE("Quality gap, 3 items") ALL /MODEL=ALPHA /SUMMARY=TOTAL.

* ------------------------------------------------------------ RQ1: the domain profile (descriptive).
* Current use, and AI-attributed change in every domain (less / no change / more).
FREQUENCIES CurUse_WorkStudy CurUse_Writing CurUse_Self CurUse_Personal CurUse_Family CurUse_Religion
  CurUse_Formal CurUse_Consume.
FREQUENCIES d_WorkStudy d_Writing d_Self d_Personal d_Family d_Fusha d_Religion d_Consume Switch_Mode
  SwitchEng SwitchEng_bin DomainsLost.
DESCRIPTIVES d_WorkStudy d_Writing d_Self d_Personal d_Family d_Fusha d_Religion d_Consume
  /STATISTICS=MEAN STDDEV MIN MAX.
* Switching between Arabic and English: more or less, against no change.
NPAR TESTS /SIGN=zero WITH Switch_Mode (PAIRED) /MISSING ANALYSIS.

* ============================================================ FAMILY A (Holm in Python).
TITLE 'Family A: direction and order of the change (H1, H2)'.
* H1a: Fusha. Wilcoxon signed-rank against 0, with the exact sign test alongside.
NPAR TESTS /WILCOXON=zero WITH d_Fusha (PAIRED) /SIGN=zero WITH d_Fusha (PAIRED) /MISSING ANALYSIS.

* H1b: work/study.
NPAR TESTS /WILCOXON=zero WITH d_WorkStudy (PAIRED) /SIGN=zero WITH d_WorkStudy (PAIRED) /MISSING ANALYSIS.

* H2a: Fishman's order, work/study > personal > family. Page's trend test is in Python.
* Here: the Friedman omnibus test, Kendall's W, and the pairwise Wilcoxon tests (complete cases).
NPAR TESTS /FRIEDMAN=Disp_WorkStudy Disp_Personal Disp_Family
  /KENDALL=Disp_WorkStudy Disp_Personal Disp_Family
  /WILCOXON=Disp_WorkStudy Disp_WorkStudy Disp_Personal WITH Disp_Family Disp_Personal Disp_Family (PAIRED)
  /MISSING LISTWISE.

* H2b: Fusha loses more than the spoken dialect (mean of self, personal, family).
NPAR TESTS /WILCOXON=Disp_Fusha WITH DialectLoss (PAIRED) /MISSING ANALYSIS.

* ============================================================ FAMILY B (HC3 and Holm in Python).
TITLE 'Family B: what predicts the decrease (H3, H4)'.
* Covariates: age (25 or over) and EventMove (started English-medium study or work, or moved country).
* H3. Block 1 enters the covariates, block 2 the three H3 predictors: the R-square change F in block 2.
* is the (classical) joint test of the three predictors.
REGRESSION
  /DESCRIPTIVES=MEAN STDDEV N
  /STATISTICS COEFF OUTS CI(95) R ANOVA CHANGE COLLIN TOL
  /DEPENDENT Displacement
  /METHOD=ENTER Age25 EventMove
  /METHOD=ENTER AI_Intensity EnglishShare QualityGap.

* H4: displacement and perceived ability decline. Cook's distance is saved for the influence check.
REGRESSION
  /DESCRIPTIVES=MEAN STDDEV N
  /STATISTICS COEFF OUTS CI(95) R ANOVA
  /DEPENDENT AbilityDecline
  /METHOD=ENTER Displacement Age25 EventMove
  /SAVE COOK(cook_h4).

* Each H3 predictor on its own, with the covariates.
REGRESSION /STATISTICS COEFF OUTS CI(95) R ANOVA /DEPENDENT Displacement
  /METHOD=ENTER AI_Intensity Age25 EventMove.
REGRESSION /STATISTICS COEFF OUTS CI(95) R ANOVA /DEPENDENT Displacement
  /METHOD=ENTER QualityGap Age25 EventMove.

* H5 (mediation) and E1 are in Python: SPSS 23 cannot run PROCESS.

* ============================================================ robustness.
TITLE 'Robustness: the alternative at each decision point'.
* Spearman matrix of the main scores, with English proficiency.
NONPAR CORR /VARIABLES=Displacement Displacement4 FormalLoss Disp_Fusha Disp_WorkStudy AbilityDecline
  QualityGap AI_Intensity EnglishShare SocialLoss Eng_Prof Switch_Mode /PRINT=SPEARMAN TWOTAIL /MISSING=PAIRWISE.

* AI or technology in general. Social media is one overall question, the AI scores average.
* several domains, so compare against both and report the pair as a bracket.
NPAR TESTS /WILCOXON=SocialLoss SocialLoss WITH Displacement FormalLoss (PAIRED) /MISSING ANALYSIS.
* The AI-attributed decrease among those who did and did not report a social-media decrease.
MEANS TABLES=Displacement BY SocialDecrease /CELLS=MEAN COUNT STDDEV.
NPAR TESTS /M-W=Displacement BY SocialDecrease(0 1).
* H3 and H4 with social-media attribution controlled.
REGRESSION /STATISTICS COEFF OUTS CI(95) R ANOVA /DEPENDENT Displacement
  /METHOD=ENTER AI_Intensity EnglishShare QualityGap Age25 EventMove SocialLoss.
REGRESSION /STATISTICS COEFF OUTS CI(95) R ANOVA /DEPENDENT AbilityDecline
  /METHOD=ENTER Displacement Age25 EventMove SocialLoss.

* Change of setting as a rival explanation for the work/study decrease.
* stable = studying or working, and no new university, graduation or job (25 people, 11 of them aged 25+).
NPAR TESTS /M-W=d_WorkStudy BY Events_1(0 1).
NPAR TESTS /M-W=d_WorkStudy BY stable(0 1).
TEMPORARY.
SELECT IF (Under25 = 1).
NPAR TESTS /M-W=d_WorkStudy BY stable(0 1).
REGRESSION /STATISTICS COEFF OUTS CI(95) R ANOVA /DEPENDENT d_WorkStudy
  /METHOD=ENTER stable Age25.
TEMPORARY.
SELECT IF (stable = 1).
NPAR TESTS /WILCOXON=zero WITH d_WorkStudy (PAIRED) /SIGN=zero WITH d_WorkStudy (PAIRED) /MISSING ANALYSIS.
TEMPORARY.
SELECT IF (stable_noeng = 1).
NPAR TESTS /WILCOXON=zero WITH d_WorkStudy (PAIRED) /SIGN=zero WITH d_WorkStudy (PAIRED) /MISSING ANALYSIS.
* Life transitions as covariates.
REGRESSION /STATISTICS COEFF OUTS CI(95) R ANOVA /DEPENDENT Displacement
  /METHOD=ENTER AI_Intensity EnglishShare QualityGap Age25 EventMove Events_1 Events_2 Events_3.
REGRESSION /STATISTICS COEFF OUTS CI(95) R ANOVA /DEPENDENT AbilityDecline
  /METHOD=ENTER Displacement Age25 EventMove Events_1 Events_2 Events_3.

* Without the straight-liners.
TEMPORARY.
SELECT IF (straightline = 0).
NPAR TESTS /WILCOXON=zero WITH d_Fusha (PAIRED) /SIGN=zero WITH d_Fusha (PAIRED) /MISSING ANALYSIS.
TEMPORARY.
SELECT IF (straightline = 0).
REGRESSION /STATISTICS COEFF OUTS CI(95) R ANOVA /DEPENDENT Displacement
  /METHOD=ENTER AI_Intensity EnglishShare QualityGap Age25 EventMove.
TEMPORARY.
SELECT IF (straightline = 0).
REGRESSION /STATISTICS COEFF OUTS CI(95) R ANOVA /DEPENDENT AbilityDecline
  /METHOD=ENTER Displacement Age25 EventMove.

* Without the most influential case in H4 (largest Cook's distance).
AGGREGATE /OUTFILE=* MODE=ADDVARIABLES OVERWRITE=YES /cook_max=MAX(cook_h4).
DESCRIPTIVES cook_h4 /STATISTICS=MEAN MAX.
TEMPORARY.
SELECT IF (MISSING(cook_h4) OR cook_h4 < cook_max).
REGRESSION /STATISTICS COEFF OUTS CI(95) R ANOVA /DEPENDENT Displacement
  /METHOD=ENTER AI_Intensity EnglishShare QualityGap Age25 EventMove.
TEMPORARY.
SELECT IF (MISSING(cook_h4) OR cook_h4 < cook_max).
REGRESSION /STATISTICS COEFF OUTS CI(95) R ANOVA /DEPENDENT AbilityDecline
  /METHOD=ENTER Displacement Age25 EventMove.

* Covariate sets: none; age only; + English proficiency; + computing field and AI tenure.
REGRESSION /STATISTICS COEFF OUTS CI(95) R ANOVA /DEPENDENT Displacement
  /METHOD=ENTER AI_Intensity EnglishShare QualityGap.
REGRESSION /STATISTICS COEFF OUTS CI(95) R ANOVA /DEPENDENT AbilityDecline
  /METHOD=ENTER Displacement.
REGRESSION /STATISTICS COEFF OUTS CI(95) R ANOVA /DEPENDENT Displacement
  /METHOD=ENTER AI_Intensity EnglishShare QualityGap Age25.
REGRESSION /STATISTICS COEFF OUTS CI(95) R ANOVA /DEPENDENT AbilityDecline
  /METHOD=ENTER Displacement Age25.
REGRESSION /STATISTICS COEFF OUTS CI(95) R ANOVA /DEPENDENT Displacement
  /METHOD=ENTER AI_Intensity EnglishShare QualityGap Age25 EventMove Eng_Prof.
REGRESSION /STATISTICS COEFF OUTS CI(95) R ANOVA /DEPENDENT AbilityDecline
  /METHOD=ENTER Displacement Age25 EventMove Eng_Prof.
REGRESSION /STATISTICS COEFF OUTS CI(95) R ANOVA /DEPENDENT Displacement
  /METHOD=ENTER AI_Intensity EnglishShare QualityGap Age25 EventMove Computing AI_TenureRank.
REGRESSION /STATISTICS COEFF OUTS CI(95) R ANOVA /DEPENDENT AbilityDecline
  /METHOD=ENTER Displacement Age25 EventMove Computing AI_TenureRank.

* Displacement over writing, self, personal and family only (sensitivity).
REGRESSION /STATISTICS COEFF OUTS CI(95) R ANOVA /DEPENDENT Displacement4
  /METHOD=ENTER AI_Intensity EnglishShare QualityGap Age25 EventMove.
REGRESSION /STATISTICS COEFF OUTS CI(95) R ANOVA /DEPENDENT AbilityDecline
  /METHOD=ENTER Displacement4 Age25 EventMove.

* The spoken dialect only (self, personal, family).
REGRESSION /STATISTICS COEFF OUTS CI(95) R ANOVA /DEPENDENT DialectLoss
  /METHOD=ENTER AI_Intensity EnglishShare QualityGap Age25 EventMove.
REGRESSION /STATISTICS COEFF OUTS CI(95) R ANOVA /DEPENDENT AbilityDecline
  /METHOD=ENTER DialectLoss Age25 EventMove.

* ============================================================ exploratory.
TITLE 'Exploratory: formal writing in Fusha'.
* E3: among those who wrote Fusha before AI, a harder time writing it and the attributed decrease.
NONPAR CORR /VARIABLES=RegisterDecline Displacement /PRINT=SPEARMAN TWOTAIL /MISSING=PAIRWISE.

* ============================================================ core sample (sensitivity).
TITLE 'Core sample (sensitivity check)'.
* Grew up and lives in the Arab region, no move since 2022; same tests as for all respondents.
FILTER BY core.
NPAR TESTS /WILCOXON=zero WITH d_Fusha (PAIRED) /SIGN=zero WITH d_Fusha (PAIRED) /MISSING ANALYSIS.
NPAR TESTS /WILCOXON=zero WITH d_WorkStudy (PAIRED) /SIGN=zero WITH d_WorkStudy (PAIRED) /MISSING ANALYSIS.
NPAR TESTS /FRIEDMAN=Disp_WorkStudy Disp_Personal Disp_Family
  /KENDALL=Disp_WorkStudy Disp_Personal Disp_Family
  /WILCOXON=Disp_WorkStudy WITH Disp_Family (PAIRED) /MISSING LISTWISE.
NPAR TESTS /WILCOXON=Disp_Fusha WITH DialectLoss (PAIRED) /MISSING ANALYSIS.
REGRESSION /STATISTICS COEFF OUTS CI(95) R ANOVA /DEPENDENT Displacement
  /METHOD=ENTER AI_Intensity EnglishShare QualityGap Age25 EventMove.
REGRESSION /STATISTICS COEFF OUTS CI(95) R ANOVA /DEPENDENT AbilityDecline
  /METHOD=ENTER Displacement Age25 EventMove.
FILTER OFF.
