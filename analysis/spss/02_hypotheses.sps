* =============================================================================.
* 02_hypotheses.sps - descriptives, confirmatory tests and robustness checks.
* The choices behind every test are in analysis/ANALYSIS-DECISIONS.md.
* Written for SPSS 23. Done only in analysis/03_python_stats.py: Holm corrections, Page's trend test,.
* HC3 standard errors (SPSS 23's REGRESSION has no HC3 option), the wild bootstrap, the H5 and E1 mediation,.
* the Firth logit, exact signed-rank p for groups of 15 or fewer non-zero answers, effect sizes,.
* Wilson intervals and omega. SPSS shows classical OLS errors; the paper reports the HC3 ones.
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
COMPUTE Under25 = (Age25 = 0).
VARIABLE LEVEL d_WorkStudy d_Writing d_Self d_Personal d_Family d_Fusha d_Religion d_Consume
  Displacement Displacement4 DialectLoss FormalLoss Disp_Fusha Disp_WorkStudy Disp_Personal Disp_Family
  AbilityDecline QualityGap AI_Intensity EnglishShare SocialLoss zero (SCALE).
EXECUTE.

* ============================================================ participants.
* Submitted, consented, eligible, outside the primary sample, straight-liners.
FREQUENCIES Consent Eligible excl_region moved core straightline.

* ============================================================ primary sample from here on.
* The primary sample is all respondents (decision of 3 Oct 2026).
* The plan's core sample is analysed as a sensitivity check at the end.
FILTER OFF.

* ------------------------------------------------------------ Table 1: the sample.
FREQUENCIES Consent Eligible L1_Home_1 TO L1_Home_4 Role Education Field Age Gender
  Country_GrewUp Country_Now Moved_Since2022 AI_Start AI_Freq AI_TaskShare AI_Breadth_1 TO AI_Breadth_8
  AI_Lang AI_Content AI_ContentLang FushaPreAI Sch_SciLang Uni_Lang Eng_Prof Events_1 TO Events_6.

* ------------------------------------------------------------ reliability (primary sample).
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

* ============================================================ FAMILY A (Holm in Python).
* H1a: Fusha. Wilcoxon signed-rank against 0, with the exact sign test alongside.
NPAR TESTS /WILCOXON=zero WITH d_Fusha (PAIRED) /SIGN=zero WITH d_Fusha (PAIRED) /MISSING ANALYSIS.

* H1b: work/study.
NPAR TESTS /WILCOXON=zero WITH d_WorkStudy (PAIRED) /SIGN=zero WITH d_WorkStudy (PAIRED) /MISSING ANALYSIS.

* H2a: Fishman's order, work/study > personal > family. Page's trend test is in Python.
* Here: the Friedman omnibus test and the work/study vs family Wilcoxon (complete cases).
NPAR TESTS /FRIEDMAN=Disp_WorkStudy Disp_Personal Disp_Family
  /WILCOXON=Disp_WorkStudy WITH Disp_Family (PAIRED) /MISSING LISTWISE.

* H2b: Fusha loses more than the spoken dialect (mean of self, personal, family).
NPAR TESTS /WILCOXON=Disp_Fusha WITH DialectLoss (PAIRED) /MISSING ANALYSIS.

* ============================================================ FAMILY B (HC3 and Holm in Python).
* Covariates: age (25 or over) and EventMove (in this sample: started English-medium study or work).
* H3. Block 1 enters the covariates, block 2 the three H3 predictors: the R-square change F in block 2.
* is the (classical) joint test of the three predictors.
REGRESSION
  /DESCRIPTIVES=MEAN STDDEV N
  /STATISTICS COEFF OUTS CI(95) R ANOVA CHANGE COLLIN TOL
  /DEPENDENT Displacement
  /METHOD=ENTER Age25 EventMove
  /METHOD=ENTER AI_Intensity EnglishShare QualityGap.

* H4: displacement and perceived ability decline.
REGRESSION
  /DESCRIPTIVES=MEAN STDDEV N
  /STATISTICS COEFF OUTS CI(95) R ANOVA
  /DEPENDENT AbilityDecline
  /METHOD=ENTER Displacement Age25 EventMove.

* H5 (mediation) and E1 are in Python: SPSS 23 cannot run PROCESS.

* ============================================================ robustness.
* Spearman matrix of the main scores.
NONPAR CORR /VARIABLES=Displacement Displacement4 FormalLoss Disp_Fusha Disp_WorkStudy AbilityDecline
  QualityGap AI_Intensity EnglishShare SocialLoss /PRINT=SPEARMAN TWOTAIL.

* AI or technology in general. Social media is one overall question, the AI scores average.
* several domains, so compare against both and report the pair as a bracket.
NPAR TESTS /WILCOXON=SocialLoss SocialLoss WITH Displacement FormalLoss (PAIRED) /MISSING ANALYSIS.
REGRESSION /STATISTICS COEFF OUTS CI(95) R ANOVA /DEPENDENT Displacement
  /METHOD=ENTER AI_Intensity EnglishShare QualityGap Age25 EventMove SocialLoss.

* Change of setting as a rival explanation for the work/study loss.
* stable = same work or study setting throughout the AI period (8 people here, 4 of them aged 25+).
NPAR TESTS /M-W=d_WorkStudy BY stable(0 1).
TEMPORARY.
SELECT IF (Under25 = 1).
NPAR TESTS /M-W=d_WorkStudy BY stable(0 1).
REGRESSION /STATISTICS COEFF OUTS CI(95) R ANOVA /DEPENDENT d_WorkStudy
  /METHOD=ENTER stable Age25.
TEMPORARY.
SELECT IF (stable = 1).
NPAR TESTS /WILCOXON=zero WITH d_WorkStudy (PAIRED) /SIGN=zero WITH d_WorkStudy (PAIRED) /MISSING ANALYSIS.

* Without the straight-liners (in practice id 13; id 29 is in no confirmatory test).
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

* Covariate sets: none; age only (the 27 Sep plan's small-sample rule); + English proficiency.
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

* Displacement over writing, self, personal and family only (the 27 Sep plan's definition).
REGRESSION /STATISTICS COEFF OUTS CI(95) R ANOVA /DEPENDENT Displacement4
  /METHOD=ENTER AI_Intensity EnglishShare QualityGap Age25 EventMove.
REGRESSION /STATISTICS COEFF OUTS CI(95) R ANOVA /DEPENDENT AbilityDecline
  /METHOD=ENTER Displacement4 Age25 EventMove.

* ============================================================ core sample (sensitivity).
* Grew up and lives in the Arab region, no move since 2022; same models as the primary analysis.
FILTER BY core.
NPAR TESTS /WILCOXON=zero WITH d_Fusha (PAIRED) /SIGN=zero WITH d_Fusha (PAIRED) /MISSING ANALYSIS.
NPAR TESTS /WILCOXON=zero WITH d_WorkStudy (PAIRED) /SIGN=zero WITH d_WorkStudy (PAIRED) /MISSING ANALYSIS.
REGRESSION /STATISTICS COEFF OUTS CI(95) R ANOVA /DEPENDENT Displacement
  /METHOD=ENTER AI_Intensity EnglishShare QualityGap Age25 EventMove.
REGRESSION /STATISTICS COEFF OUTS CI(95) R ANOVA /DEPENDENT AbilityDecline
  /METHOD=ENTER Displacement Age25 EventMove.
FILTER OFF.
