"""Structured, route-specific 2026 eligibility screening; human attestations still required."""
from datetime import date
import ipaddress
import re
from urllib.parse import urlsplit

ROUTES = ('first_public_announcement', 'first_substantive_publication', 'Reanalysis')


def https_provenance_url(value):
    """Validate the supplied URL, never upgrade HTTP as identity normalization does."""
    if not isinstance(value, str) or any(c.isspace() or ord(c) < 32 or ord(c) == 127 for c in value) or '\\' in value:
        return False
    try:
        parsed = urlsplit(value)
        host = parsed.hostname
        if (parsed.scheme != 'https' or not value.startswith('https://') or not host or
            parsed.username is not None or parsed.password is not None or parsed.fragment or
            parsed.port not in (None, 443)):
            return False
        try:
            return ipaddress.ip_address(host).is_global
        except ValueError:
            return bool(re.fullmatch(r'[A-Za-z0-9](?:[A-Za-z0-9.-]*[A-Za-z0-9])?', host)
                        and '.' in host and not host.endswith(('.local', '.localhost', '.internal')))
    except (ValueError, TypeError):
        return False


def exact_date(value, today, year=None):
    if not isinstance(value, str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', value):
        return False
    try:
        parsed = date.fromisoformat(value)
        return parsed <= today and (year is None or parsed.year == year)
    except ValueError:
        return False


def text(value):
    return isinstance(value, str) and bool(value.strip())


def references(value, sources):
    return (isinstance(value, list) and bool(value) and
            all(isinstance(v, str) and v in sources for v in value) and len(set(value)) == len(value))


def supported_statement(value, sources):
    return (isinstance(value, dict) and set(value) == {'statement', 'source_ids'} and
            text(value['statement']) and references(value['source_ids'], sources))


def publication_dates(value, today, sources):
    """Known dates need cited verification; absent editions need supported N/A.
    Unknown is not verified. A first-date assertion alone never reconciles history.
    """
    fields = {'online', 'print', 'first_publication'}
    if not isinstance(value, dict) or set(value) != fields | {'verification'}:
        return False
    if not exact_date(value['first_publication'], today, 2026):
        return False
    if value['online'] is None and value['print'] is None:
        return False
    verification = value['verification']
    if not isinstance(verification, dict) or set(verification) != fields:
        return False
    for field in fields:
        receipt = verification[field]
        if (not isinstance(receipt, dict) or set(receipt) != {'status', 'source_ids', 'rationale'} or
            not references(receipt['source_ids'], sources) or not text(receipt['rationale'])):
            return False
        if value[field] is None:
            if field == 'first_publication' or receipt['status'] != 'not_applicable':
                return False
        elif not exact_date(value[field], today) or receipt['status'] != 'verified':
            return False
    known = [value[field] for field in fields if value[field] is not None]
    return value['first_publication'] == min(known)


def _validate(route, evidence, sources, today):
    """Return reasons, never equate structured input with independent fact verification."""
    if route not in ROUTES or not isinstance(evidence, dict) or set(evidence) != {route}:
        return ['eligibility_structure_or_route_invalid']
    data = evidence[route]
    if not isinstance(data, dict):
        return ['eligibility_evidence_invalid']
    reasons = []
    def check(condition, code):
        if not condition:
            reasons.append(code)
    if route == 'first_public_announcement':
        check(set(data) == {'announcement_date', 'fieldwork_dates', 'first_announcement_confirmed',
                           'announcement_source_ids', 'field_context_source_ids', 'earlier_announcement_search'}, 'announcement_schema')
        check(exact_date(data.get('announcement_date'), today, 2026), 'announcement_not_confirmed_2026')
        fieldwork = data.get('fieldwork_dates')
        check(isinstance(fieldwork, list) and bool(fieldwork) and
              all(exact_date(d, today) and d <= data.get('announcement_date', '') for d in fieldwork), 'fieldwork_history_missing_or_conflicting')
        check(data.get('first_announcement_confirmed') is True, 'first_announcement_unverified')
        for field in ('announcement_source_ids', 'field_context_source_ids'):
            check(references(data.get(field), sources), 'missing_' + field)
        check(supported_statement(data.get('earlier_announcement_search'), sources), 'announcement_history_search_missing')
    else:
        required = {'publication_dates', 'publication_source_ids', 'peer_reviewed',
                    'earlier_publications', 'history_search'}
        required |= {'substantive_increment'} if route == 'first_substantive_publication' else {
            'legacy_material', 'legacy_provenance', 'analysis_date', 'important_question', 'interpretive_gain', 'gain_type'}
        check(set(data) == required, 'publication_or_reanalysis_schema')
        check(publication_dates(data.get('publication_dates'), today, sources), 'ineligible_or_tentative_publication_dates')
        check(data.get('peer_reviewed') is True, 'peer_review_not_verified')
        check(references(data.get('publication_source_ids'), sources), 'publication_sources_missing')
        check(supported_statement(data.get('history_search'), sources), 'publication_history_search_missing')
        history = data.get('earlier_publications')
        check(isinstance(history, list), 'earlier_publication_history_missing')
        if isinstance(history, list):
            for item in history:
                check(isinstance(item, dict) and set(item) == {'date', 'stage', 'description', 'source_ids'} and
                      exact_date(item.get('date'), today) and item.get('stage') in ('preliminary', 'full', 'conference', 'partial') and text(item.get('description')) and
                      references(item.get('source_ids'), sources), 'earlier_publication_history_invalid')
        if route == 'first_substantive_publication':
            check(supported_statement(data.get('substantive_increment'), sources), 'substantive_increment_not_supported')
        else:
            check(data.get('legacy_material') is True, 'legacy_material_unverified')
            legacy = data.get('legacy_provenance')
            check(isinstance(legacy, dict) and set(legacy) == {'material_or_dataset', 'original_dates', 'source_ids'} and
                  text(legacy.get('material_or_dataset')) and references(legacy.get('source_ids'), sources) and
                  isinstance(legacy.get('original_dates'), list) and bool(legacy['original_dates']) and
                  all(exact_date(d, today) and d < data.get('analysis_date', '') for d in legacy['original_dates']), 'legacy_provenance_or_original_dates_missing')
            check(exact_date(data.get('analysis_date'), today, 2026), 'analysis_date_not_2026')
            if publication_dates(data.get('publication_dates'), today, sources) and exact_date(data.get('analysis_date'), today):
                check(data['analysis_date'] <= data['publication_dates']['first_publication'], 'analysis_after_publication')
            for field in ('important_question', 'interpretive_gain'):
                check(supported_statement(data.get(field), sources), 'unsupported_' + field)
            check(data.get('gain_type') == 'major_new_interpretation', 'insufficient_reanalysis_gain')
    return reasons


def validate(route, evidence, sources, today):
    try:
        return _validate(route, evidence, sources, today)
    except (TypeError, ValueError, KeyError, AttributeError):
        return ['eligibility_evidence_invalid']
