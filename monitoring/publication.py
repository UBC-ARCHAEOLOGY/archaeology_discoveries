"""Fail-closed dossier gate. Evaluation never writes the academic archive.

An accepted dossier authorizes preparation of a transaction PR, never direct main
writes, merging, rank changes, or bypass of editorial QA. Attestations are reviewed
in repository policy, never accepted from remote data or collector flags.
"""
from datetime import date
import re
import monitor as m
import eligibility as e
from datetime import datetime, timezone

CHECKS = (
    'primary_facts', 'firstness_and_history', 'field_context', 'scholarly_significance',
    'independent_metadata_and_dates', 'limitations', 'bilingual_consistency',
    'privacy_and_indigenous_permissions', 'regional_and_chronological_balance',
    'journal_quality_and_retraction', 'archive_identity_search', 'deterministic_build_and_editorial_qa',
    'stable_ids_sidebar_map_counts_status',
)
REQUIRED_TEXT = ('field_context', 'significance', 'limitations', 'earlier_history',
                 'description_en', 'description_zh', 'selection_reason_en', 'selection_reason_zh')


def evaluate(dossier, policy, existing_dois=(), existing_titles=(), today=None):
    today = today or date.today()
    reasons = []
    if policy.get('enabled') is not True:
        reasons.append('policy_disabled')
    for field in ('independent_gate_review', 'standing_authorization', 'live_verified_new_record_run', 'rank_integration_procedure'):
        if not isinstance(policy.get(field), str) or not policy[field].startswith('https://github.com/UBC-ARCHAEOLOGY/archaeology_discoveries/'):
            reasons.append('missing_' + field)
    if dossier.get('origin') != 'live':
        reasons.append('not_live_evidence')
    if dossier.get('metadata_only') is not False:
        reasons.append('metadata_only_or_unspecified')
    if dossier.get('new_project') is not True or dossier.get('changes_existing') is not False:
        reasons.append('existing_or_unspecified_project')
    if dossier.get('changes_ranking') is not False:
        reasons.append('ranking_change')
    if dossier.get('status') != 'Additional candidate':
        reasons.append('unsupported_status')
    identifier = m.doi(dossier.get('doi'))
    if not identifier or identifier in {m.doi(d) for d in existing_dois}:
        reasons.append('missing_or_duplicate_doi')
    if not dossier.get('authors') or not m.norm(dossier.get('title', '')):
        reasons.append('missing_author_or_title')
    if m.norm(dossier.get('title', '')) in {m.norm(t) for t in existing_titles}:
        reasons.append('duplicate_title_or_twin_doi')
    for field in REQUIRED_TEXT:
        if not isinstance(dossier.get(field), str) or not dossier[field].strip():
            reasons.append('missing_' + field)
    for flag in ('retracted', 'quality_concern', 'conflicting_evidence', 'sensitive_location', 'identity_conflict', 'bilingual_mismatch', 'geography_outlier'):
        if dossier.get(flag) is not False:
            reasons.append(flag + '_or_unresolved')
    if 'publication_dates' in dossier:
        reasons.append('legacy_publication_dates_not_supported')
    provenance = dossier.get('primary_sources', [])
    source_ids = set()
    if not isinstance(provenance, list) or not provenance:
        reasons.append('primary_provenance_missing')
    else:
        for source in provenance:
            valid = isinstance(source, dict)
            if valid:
                sid = source.get('id')
                valid = isinstance(sid, str) and re.fullmatch('[a-zA-Z0-9_-]{1,64}', sid) is not None and sid not in source_ids
                if valid:
                    source_ids.add(sid)
                try:
                    retrieved = datetime.fromisoformat(source.get('retrieved_at', '').replace('Z', '+00:00'))
                    valid = valid and retrieved.tzinfo is not None and retrieved.astimezone(timezone.utc).date() <= today
                except (ValueError, TypeError, AttributeError):
                    valid = False
                valid = (valid and e.https_provenance_url(source.get('url')) and
                         isinstance(source.get('sha256'), str) and re.fullmatch('[a-f0-9]{64}', source['sha256']) is not None and
                         type(source.get('http_status')) is int and source['http_status'] == 200)
            if not valid:
                reasons.append('invalid_primary_provenance')
    reasons.extend(e.validate(dossier.get('eligibility_route'), dossier.get('eligibility_evidence'), source_ids, today))
    # Hash binds every claim, bilingual wording, history and primary-source receipt.
    approval = policy.get('approved_dossiers', {}).get(m.digest(dossier), {})
    if approval.get('editor') not in policy.get('responsible_editors', []) or not approval.get('approval_reference'):
        reasons.append('no_bound_editor_authorization')
    for check in CHECKS:
        attestation = approval.get('checks', {}).get(check, {})
        if not isinstance(attestation, dict) or attestation.get('result') != 'pass' or not attestation.get('evidence_reference'):
            reasons.append('unattested_' + check)
    return {'dossier_sha256': m.digest(dossier), 'allowed': not reasons,
            'action': 'prepare_transaction_pr' if not reasons else 'remain_provisional',
            'reasons': sorted(set(reasons))}
