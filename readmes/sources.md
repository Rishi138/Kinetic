# Kinetic — Supporting Research

This document collects the clinical and technical research behind Kinetic's design decisions. It's included for transparency: every metric this project tracks, and every measurement tradeoff it makes, is grounded in published literature rather than assumption. Where the literature is mixed or unsettled, that's noted explicitly rather than omitted.

---

## 1. Home PT lacks objective feedback, and unsupervised exercise quality measurably degrades

**Study:** Mitchell, U.H., Lee, H., Dennis, H.E., & Seeley, M.K. (2022). "Quality of knee strengthening exercises performed at home deteriorates after one week." *BMC Musculoskeletal Disorders*, 23, 165.

**Design:** Cross-sectional laboratory study.

**Sample:** 19 healthy middle-aged/older volunteers (mean age 63.1 ± 8.6 years).

**Procedure:** 36 reflective markers were placed on standard anatomical landmarks (ASIS/PSIS, iliac crest, femoral epicondyles, malleoli, metatarsal heads, calcaneus) and tracked by 12 high-speed Qualisys cameras at 100 Hz — gold-standard marker-based motion capture. Each participant was taught four exercises (knee flexion, straight leg raise, "V-in"/"V-out," side-lying hip abduction) by a physical therapist using verbal, visual, and manual correction until performed correctly. One week later, with no further coaching, participants repeated the same exercises. Knee and hip sagittal/rotational angles were extracted and compared via repeated-measures t-tests.

**Result:** Not a single participant reproduced all four exercises correctly a week later. Movement kinematics changed significantly (p < 0.05) across multiple exercises. For the "V-out" exercise specifically, average hip rotation shifted 232% further into external rotation than at the initial visit — enough to recruit the wrong muscle group (quadriceps instead of the intended hip abductors) without the participant being aware.

**Kinetic-specific takeaway:** This is close to a controlled experiment for Kinetic's core premise. These weren't non-compliant patients — they were coached until correct and still drifted within seven days, silently, with no signal to the patient that anything had changed. That's the exact blind spot Kinetic addresses: it doesn't rely on the patient noticing their own form has drifted.

**Citation:** Mitchell UH, Lee H, Dennis HE, Seeley MK. Quality of knee strengthening exercises performed at home deteriorates after one week. *BMC Musculoskelet Disord*. 2022;23:165. doi:10.1186/s12891-022-05120-3

---

## 2. Limb Symmetry Index is the real clinical RTS standard — and current thresholds are known to be insufficient on their own

**Study:** Grindem, H., Snyder-Mackler, L., Moksnes, H., Engebretsen, L., & Risberg, M.A. (2016). "Simple decision rules can reduce reinjury risk by 84% after ACL reconstruction: the Delaware-Oslo ACL cohort study." *British Journal of Sports Medicine*, 50(13), 804-808.

**Design:** Prospective 2-year cohort study.

**Sample:** 106 patients who played pivoting sports pre-injury; 74 patients returned to level I (pivoting/cutting) sports with complete follow-up.

**Procedure:** Knee function assessed via the Knee Outcome Survey–Activities of Daily Living Scale, a global rating of knee function, quadriceps strength testing, and a 4-test hop battery, reported as Limb Symmetry Index (injured limb ÷ uninjured limb × 100). Passing RTS criteria required scoring >90 on every measure; failing any one measure counted as a fail. Sports participation and reinjury were tracked monthly for 2 years.

**Result:** Athletes who returned to level I sport had 4.32× the reinjury rate of those who didn't (p = 0.048). Among those who failed RTS criteria, 38.2% suffered a reinjury, versus 5.6% of those who passed. Each month RTS was delayed (up to 9 months post-op) reduced reinjury risk by 51%. A related meta-analysis of this and similar cohorts found each 1% increase in quadriceps LSI corresponded to a 3% reduction in reinjury risk.

**Important caveat (disclosed deliberately):** Despite meeting LSI/RTS criteria, published second-ACL-injury rates remain 20–40% in the broader literature, and researchers have specifically questioned using the uninvolved limb as a baseline, since it often shows strength deficits of its own post-injury.

**Kinetic-specific takeaway:** LSI is the actual clinical decision rule, backed by a strong, well-powered dose-response relationship in a real prospective cohort — not an invented proxy. But the field's own literature agrees single-number LSI thresholds miss things, which is the direct justification for Kinetic tracking movement *quality* (valgus, hip drop, trunk lean) alongside LSI rather than LSI alone. That's aligned with where the research community itself says the next improvement needs to come from.

**Citation:** Grindem H, Snyder-Mackler L, Moksnes H, Engebretsen L, Risberg MA. Simple decision rules can reduce reinjury risk by 84% after ACL reconstruction: the Delaware-Oslo ACL cohort study. *Br J Sports Med*. 2016;50(13):804-808. doi:10.1136/bjsports-2016-096031

---

## 3. MediaPipe is a validated, clinically-correlated measurement tool — with a specific, documented limitation this project's design already accounts for

**Study:** Lafayette, T.B.G., et al., as characterized in Menezes et al., "A comprehensive analysis of the machine learning pose estimation models used in human movement and posture analyses: a narrative review," *Heliyon*, 2024; independently corroborated in Nunes et al., "Validation of Angle Estimation Based on Body Tracking Data from RGB-D and RGB Cameras for Biomechanical Assessment," *Sensors*, 2023, 23(1), 3.

**Design (Lafayette et al.):** Quantitative validation comparing MediaPipe-derived joint angles against gold-standard Qualisys marker-based motion capture.

**Result:** MediaPipe correlated strongly with Qualisys — mean Pearson's r = 0.80 ± 0.1 for lower-limb movement, r = 0.91 ± 0.08 for upper-limb — with "excellent" absolute error relative to established clinical error tolerances.

**Corroborating study (Nunes et al., independent replication):** 60 recorded movement trials compared MediaPipe, Kinect, and two other RGB-D sensors against Qualisys. MediaPipe had the lowest median absolute angular error of the group (7.01°) and the lowest error dispersion, with all correlations significant at p < 0.001.

**The specific limitation this project's design accounts for:** Multiple independent studies flag MediaPipe's depth (z-axis) estimation as its weak point specifically. One large benchmark (Physio2.2M — 2.2M frames, 25 participants) found mean joint-position error of 72–122mm in the 2D image plane versus 146–249mm once 3D depth is included. A squat-specific validation study found systematic hip-angle bias (mean −17.49°) when relying on 3D estimation. This is a repeated, specific finding across the literature, not an isolated critique.

**Design decision this motivates:** Rather than trusting MediaPipe's raw z-coordinate for knee valgus/varus scoring, Kinetic computes deviation geometrically from a single, slightly angled camera view — mirroring the established 2D frontal plane projection angle (FPPA) methodology already used in the clinical literature as a validated alternative to full 3D motion capture for this exact purpose (see Hewett et al. 2005; Willson & Davis 2008). This wasn't only a cost-driven workaround — it converges with the field's own preferred simplification. In development, this simpler geometric approach also empirically outperformed a more complex 3D-derived calculation, which is consistent with the z-axis error literature above.

**Citations:**
- Menezes MLR, et al. A comprehensive analysis of the machine learning pose estimation models used in human movement and posture analyses: a narrative review. *Heliyon*. 2024.
- Nunes JP, et al. Validation of Angle Estimation Based on Body Tracking Data from RGB-D and RGB Cameras for Biomechanical Assessment. *Sensors*. 2023;23(1):3. doi:10.3390/s23010003
- Hewett TE, Myer GD, Ford KR, et al. Biomechanical measures of neuromuscular control and valgus loading of the knee predict anterior cruciate ligament injury risk in female athletes. *Am J Sports Med*. 2005;33(4):492-501.

---

## Known Limitations & Design Tradeoffs

Being explicit about what this system does *not* do, and why, is part of making it trustworthy.

- **2D geometric approximation, not 3D ground truth.** Valgus/varus scoring uses the hip–knee–ankle deviation line from a single angled camera, not full 3D biomechanical modeling. This mirrors validated clinical FPPA methodology (see §3), but it is still an approximation, not a lab-grade measurement — it does not replace instrumented gait analysis or a clinician's in-person assessment.
- **Single, affordable camera setup.** No motion-capture-grade hardware is used. Error tolerances follow single-RGB-camera validation studies (§3), not marker-based studies (§1, §2), which have tighter error margins than this system can achieve.
- **Knee valgus/varus is a risk factor, not a diagnosis.** The biomechanical link between dynamic knee valgus and ACL loading is well established (Hewett et al. 2005; Quatman et al. 2014), but population-level prospective studies on whether frontal-plane knee motion alone *predicts* future non-contact ACL injury are mixed (e.g., Nilstad et al. found no such association in elite female athletes). Kinetic treats valgus as one input among several (alongside hip drop, trunk lean, and LSI) rather than a standalone predictive score, consistent with current best evidence.
- **LSI's known blind spot.** As discussed in §2, LSI compares the injured limb to the uninjured limb — but the uninjured limb itself is often weaker than an uninjured peer's would be. LSI thresholds in this system should be read as one input into recovery tracking, not a standalone clearance criterion.
- **Not a replacement for clinical care.** This system is intended to close the feedback gap *between* PT sessions, not to replace a physical therapist's judgment, in-person assessment, or return-to-sport clearance decision.

---

*This document will be updated as new metrics (hip drop, trunk lean, longitudinal session tracking) are added, with corresponding research cited for each.*