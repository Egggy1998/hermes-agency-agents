// Self-check for catalog overlay logic: node check-catalog.mjs
import { readFileSync } from 'node:fs'
import assert from 'node:assert/strict'

const src = readFileSync(new URL('./plugin.js', import.meta.url), 'utf8')
const pick = (from, to) => src.slice(src.indexOf(from), src.indexOf(to))
const store = {}
const pluginCtx = { storage: { set: (k, v) => { store[k] = JSON.parse(JSON.stringify(v)) } } }
const EXPERTS = [{ slug: 'ceo', name: 'CEO', division: 'leadership', description: 'd', emoji: 'x' }]
const TEAMS = [{ id: 'exec', name: 'Exec', description: '', goal: 'grow', members: ['ceo'] }]
const useState = () => []; const useEffect = () => {}
// Test-only: evaluates a slice of our own local plugin.js, no external input.
const api = new Function('pluginCtx', 'EXPERTS', 'TEAMS', 'useState', 'useEffect',
  pick('const CATALOG_KEY', 'function Avatar(') +
  'return { normalizeCatalog, saveCatalog, catalogExperts, catalogTeams, expertInstruction, teamInstruction, teamMembers, slugify, CATALOG_KEY }'
)(pluginCtx, EXPERTS, TEAMS, useState, useEffect)

assert.equal(api.slugify('  Growth Hacker!! VN '), 'growth-hacker-vn')
const bad = api.normalizeCatalog({ experts: [{ slug: 'x' }], teams: 'nope', expertOverrides: [] })
assert.deepEqual(bad, { experts: [], expertOverrides: {}, teams: [], teamOverrides: {} })

const catalog = api.normalizeCatalog({
  experts: [{ slug: 'vn-seo', name: 'VN SEO', division: 'custom', description: '', prompt: 'Do SEO', emoji: '✦' }],
  expertOverrides: { ceo: { name: 'Chief', prompt: '' } },
  teams: [{ id: 'mine', name: 'Mine', goal: 'win', members: ['ceo', 'vn-seo'] }],
  teamOverrides: { exec: { name: 'Exec 2', members: ['ceo'] } }
})
api.saveCatalog(catalog)
assert.deepEqual(store[api.CATALOG_KEY], catalog)

const experts = api.catalogExperts(catalog)
assert.equal(experts.length, 2)
assert.equal(experts[0].name, 'Chief')
assert.match(api.expertInstruction(experts[0]), /agency_agents_load with slug "ceo"/)
assert.match(api.expertInstruction(experts[1]), /Do SEO/)

const teams = api.catalogTeams(catalog)
assert.deepEqual(teams.map(t => t.name), ['Exec 2', 'Mine'])
assert.match(api.teamInstruction(teams[0], experts), /^Use agency-agents-router/)
assert.match(api.teamInstruction({ name: 'T', goal: 'Ship it.', members: ['ceo'] }, experts), /goal: Ship it\. Task/)
assert.match(api.teamInstruction(teams[1], experts), /## VN SEO\nDo SEO/)
assert.deepEqual(api.teamMembers({ members: ['vn-seo', 'gone'] }, experts).map(e => e.name), ['VN SEO', 'gone'])
console.log('catalog check: ok')
