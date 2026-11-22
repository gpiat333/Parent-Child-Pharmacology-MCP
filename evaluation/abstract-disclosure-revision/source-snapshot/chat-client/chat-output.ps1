function Format-EvidenceAnswer([string]$Answer, [switch]$NoEvidence) {
    $disclaimer = 'Informational only; not medical advice. Compiled from public NIH/NLM/FDA data, which may be incomplete or out of date. Patients should talk to a clinician, pharmacist or poison control before starting, stopping or changing any medication.'
    $noEvidenceDisclaimer = 'Informational only; not medical advice. Patients should talk to a clinician, pharmacist or poison control before starting, stopping or changing any medication.'
    # Remove only exact copies; never strip clinical caveats or referrals by fuzzy matching.
    $Answer = $Answer.Replace($disclaimer, "").Trim()
    $Answer = $Answer.Replace($noEvidenceDisclaimer, "").Trim()
    $footer = if ($NoEvidence) { $noEvidenceDisclaimer } else { $disclaimer }
    return $Answer.TrimEnd() + "`n`n" + $footer
}
