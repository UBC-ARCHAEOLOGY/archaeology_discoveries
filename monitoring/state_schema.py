"""Strict public-state schema. Reject unknown fields; never reset or sanitize on restore."""
from datetime import date
import json
import hashlib
from zoneinfo import ZoneInfo
from datetime import datetime
import re

SCHEMA = 3
OBSERVATION_PROJECTION = 3
CATEGORIES = ('Field discovery', 'Reanalysis', 'Mixed', 'Unresolved')
MODES = ('monitor', 'review', 'audit')
DIAGNOSTICS = {None, 'http_403_access_or_terms', 'metadata_not_found', 'rate_limited',
               'http_server_error', 'http_client_error', 'proxy_403',
               'network_or_invalid_response', 'cursor_missing_or_repeated'}
MAX_BYTES = 32_000_000


def taxonomy_hash(config):
    return hashlib.sha256(json.dumps(config['tag_rules'], sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def require(condition):
    if not condition:
        raise ValueError('Invalid durable state; recovery requires review, never automatic reset')


def exact(value, keys):
    require(isinstance(value, dict) and set(value) == set(keys))


def hash_string(value, length=64):
    return isinstance(value, str) and re.fullmatch('[a-f0-9]{'+str(length)+'}', value) is not None


def day(value, start, end):
    require(isinstance(value, str) and re.fullmatch(r'\d{4}-\d{2}-\d{2}', value) is not None)
    parsed = date.fromisoformat(value)
    require(start <= parsed <= end)
    return parsed


def allowed_list(value, allowed, limit):
    require(isinstance(value, list) and len(value) <= limit)
    require(all(isinstance(v, str) and v in allowed for v in value))
    require(len(value) == len(set(value)))


def validate(state, registry, config, today=None):
    today = today or datetime.now(ZoneInfo('America/Vancouver')).date()
    start = date.fromisoformat(config['start_date'])
    allowed = {'observation_projection', 'taxonomy_sha256', 'schema', 'sources', 'observations', 'runs', '_parent', 'last_monitor_access', 'last_monitor_date'}
    require(isinstance(state, dict) and set(state) <= allowed and {'observation_projection', 'taxonomy_sha256', 'schema', 'sources', 'observations', 'runs'} <= set(state))
    require(type(state['observation_projection']) is int and state['observation_projection'] == OBSERVATION_PROJECTION)
    require(state['taxonomy_sha256'] == taxonomy_hash(config))
    require(type(state['schema']) is int and state['schema'] == SCHEMA)
    require(all(isinstance(state[k], dict) for k in ('sources', 'observations', 'runs')))
    source_ids = {s['id'] for s in registry['sources'] if s.get('enabled') and s['adapter'] == 'crossref'}
    require(set(state['sources']) <= source_ids)
    for source in state['sources'].values():
        require(isinstance(source, dict) and bool(source) and set(source) <= {'watermark', 'pending'})
        if 'watermark' in source:
            day(source['watermark'], start, today)
        if 'pending' in source:
            window = source['pending']
            exact(window, {'since', 'until', 'cursor'})
            require(day(window['since'], start, today) <= day(window['until'], start, today))
            require(isinstance(window['cursor'], str) and 0 < len(window['cursor']) <= 16384)
            require(re.fullmatch(r'\*|[A-Za-z0-9_+/=\-]+', window['cursor']) is not None)
    require(len(state['observations']) <= 100000)
    for identity, row in state['observations'].items():
        require(hash_string(identity))
        exact(row, {'first_seen', 'last_seen', 'source_ids', 'tags', 'classification', 'identity_keys'})
        require(day(row['first_seen'], start, today) <= day(row['last_seen'], start, today))
        allowed_list(row['source_ids'], source_ids, len(source_ids))
        require(bool(row['source_ids']))
        require(row['classification'] == 'Unresolved')  # collector cannot attest academic type
        exact(row['tags'], config['tag_rules'])
        for dim, rules in config['tag_rules'].items():
            allowed_list(row['tags'][dim], set(rules), len(rules))
        require(isinstance(row['identity_keys'], list) and len(row['identity_keys']) <= 3)
        require(all(hash_string(key) for key in row['identity_keys']))
        require(len(set(row['identity_keys'])) == len(row['identity_keys']))
    require(len(state['runs']) <= 10000)
    for key, run in state['runs'].items():
        require(isinstance(key, str) and len(key.split(':')) == 2)
        when, mode = key.split(':')
        day(when, start, today)
        require(mode in MODES)
        exact(run, {'report_sha256', 'outages'})
        require(hash_string(run['report_sha256']))
        allowed_list(run['outages'], source_ids, len(source_ids))
    require(('last_monitor_access' in state) == ('last_monitor_date' in state))
    if 'last_monitor_date' in state:
        day(state['last_monitor_date'], start, today)
        access = state['last_monitor_access']
        require(isinstance(access, list) and len(access) <= len(source_ids))
        seen = set()
        for entry in access:
            exact(entry, {'source', 'status', 'diagnostic', 'pages', 'watermark_advanced', 'since', 'until'})
            require(isinstance(entry['source'], str) and entry['source'] in source_ids and entry['source'] not in seen)
            seen.add(entry['source'])
            require(entry['status'] in ('complete', 'incomplete'))
            require(isinstance(entry['diagnostic'], (str, type(None))) and entry['diagnostic'] in DIAGNOSTICS)
            require(type(entry['pages']) is int and 0 <= entry['pages'] <= config['max_pages_per_source'])
            require(type(entry['watermark_advanced']) is bool and entry['watermark_advanced'] == (entry['status'] == 'complete'))
            require(day(entry['since'], start, today) <= day(entry['until'], start, today))
    if '_parent' in state:
        require(state['_parent'] is None or hash_string(state['_parent'], 40))
    return state


def no_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result)
        result[key] = value
    return result


def decode(payload, registry, config):
    require(len(payload) <= MAX_BYTES)
    return validate(json.loads(payload, object_pairs_hook=no_duplicate_keys), registry, config)
